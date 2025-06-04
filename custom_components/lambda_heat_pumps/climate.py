"""Climate platform for Lambda integration."""
from __future__ import annotations
from typing import Any
import logging

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorStateClass

from .const import (
    DOMAIN,
    SENSOR_TYPES,
    FIRMWARE_VERSION,
    BOIL_SENSOR_TEMPLATES,
    HC_SENSOR_TEMPLATES,
    BOIL_OPERATING_STATE,
    HC_OPERATING_STATE,
    DEFAULT_HOT_WATER_MIN_TEMP,
    DEFAULT_HOT_WATER_MAX_TEMP,
    DEFAULT_HEATING_CIRCUIT_MIN_TEMP,
    DEFAULT_HEATING_CIRCUIT_MAX_TEMP,
    DEFAULT_HEATING_CIRCUIT_TEMP_STEP,
    DEFAULT_FIRMWARE,
)
from .utils import build_device_info, is_register_disabled, generate_base_addresses
from .coordinator import LambdaDataUpdateCoordinator  # type: ignore

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Lambda Heat Pumps climate entities."""
    _LOGGER.debug("Setting up Lambda climate entities for entry %s", entry.entry_id)
    
    # Get coordinator from hass.data
    coordinator_data = hass.data[DOMAIN][entry.entry_id]
    if not coordinator_data or "coordinator" not in coordinator_data:
        _LOGGER.error("No coordinator found for entry %s", entry.entry_id)
        return
        
    coordinator = coordinator_data["coordinator"]
    _LOGGER.debug("Found coordinator: %s", coordinator)

    # Get device counts from config
    num_boil = entry.data.get("num_boil", 1)
    num_hc = entry.data.get("num_hc", 1)

    # Create climate entities for each device type
    entities = []

    # Boiler climate entities
    for boil_idx in range(1, num_boil + 1):
        base_address = generate_base_addresses('boil', num_boil)[boil_idx]
        entities.append(
            LambdaBoiler(
                coordinator,
                f"boil{boil_idx}",
                "",  # name intentionally left empty
                base_address,
            )
        )

    # Heating Circuit climate entities
    for hc_idx in range(1, num_hc + 1):
        base_address = generate_base_addresses('hc', num_hc)[hc_idx]
        entities.append(
            LambdaHeatingCircuit(
                coordinator,
                f"hc{hc_idx}",
                "",  # name intentionally left empty
                base_address,
            )
        )

    _LOGGER.debug("Created %d climate entities", len(entities))
    async_add_entities(entities)


class LambdaClimateEntity(CoordinatorEntity, ClimateEntity):
    """Representation of a Lambda climate entity."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_temperature_unit = "°C"
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_modes = [HVACMode.HEAT]  # Nur HEAT-Modus
    _attr_hvac_mode = HVACMode.HEAT  # Immer im HEAT-Modus
    _attr_firmware_version = 1
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(
        self,
        coordinator: "LambdaDataUpdateCoordinator",
        entry: ConfigEntry,
        climate_type: str,
        translation_key: str,
        current_temp_sensor: str,
        target_temp_sensor: str,
        min_temp: float,
        max_temp: float,
        temp_step: float,
        idx: int = 1,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._climate_type = climate_type
        self._translation_key = translation_key
        self._current_temp_sensor = current_temp_sensor
        self._target_temp_sensor = target_temp_sensor
        self._min_temp = min_temp
        self._max_temp = max_temp
        self._temp_step = temp_step
        self._idx = idx

        # Prefix for unique_id/entity_id
        name_prefix = entry.data.get("name", "lambda_wp").lower().replace(" ", "")
        prefix = f"{name_prefix}_"
        self._prefix = prefix

        # Set name and unique_id/entity_id for hot water and heating circuit
        if climate_type.startswith("hot_water"):
            # Extract index (always as int)
            try:
                idx_num = int(climate_type.split("_")[-1])
            except Exception:
                idx_num = idx
            lang = entry.data.get("language", "de")
            if lang == "de":
                self._attr_name = f"Warmwasser{idx_num}"
            else:
                self._attr_name = f"Hot Water{idx_num}"
            self._attr_unique_id = f"{prefix}hot_water_{idx_num}"
            self.entity_id = f"climate.{prefix}hot_water_{idx_num}"
            self._operating_state_sensor = f"boil{idx_num}_operating_state"
        elif climate_type.startswith("heating_circuit"):
            try:
                idx_num = int(climate_type.split("_")[-1])
            except Exception:
                idx_num = idx
            self._attr_name = f"Heizkreis{idx_num}" if entry.data.get("language", "de") == "de" else f"Heating Circuit{idx_num}"
            self._attr_unique_id = f"{prefix}heating_circuit_{idx_num}"
            self.entity_id = f"climate.{prefix}heating_circuit_{idx_num}"
            self._operating_state_sensor = f"hc{idx_num}_operating_state"
        else:
            # Fallback: use climate_type and idx
            self._attr_name = f"{climate_type.capitalize()}{idx}"
            self._attr_unique_id = f"{prefix}{climate_type}{idx}"
            self.entity_id = f"climate.{prefix}{climate_type}{idx}"
            self._operating_state_sensor = None

        self._attr_min_temp = min_temp
        self._attr_max_temp = max_temp
        self._attr_target_temperature_step = temp_step
        _LOGGER.debug(
            "Climate entity initialized: name=%s, unique_id=%s, entity_id=%s, min_temp=%s, max_temp=%s",
            self._attr_name,
            self._attr_unique_id,
            self.entity_id,
            min_temp,
            max_temp,
        )

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self._current_temp_sensor)

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self._target_temp_sensor)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return entity specific state attributes."""
        if not self.coordinator.data or not self._operating_state_sensor:
            return None

        attributes = {}

        # Get the raw operating state value
        data = self.coordinator.data
        operating_state = data.get(self._operating_state_sensor)
        if operating_state is not None:
            try:
                # Convert to integer for mapping
                state_value = int(operating_state)
                # Map the state value to text based on the climate type
                if self._climate_type.startswith("hot_water"):
                    state_text = BOIL_OPERATING_STATE.get(
                        state_value, f"Unknown state ({state_value})"
                    )
                    attributes["operating_state"] = state_text
                elif self._climate_type.startswith("heating_circuit"):
                    state_text = HC_OPERATING_STATE.get(
                        state_value, f"Unknown state ({state_value})"
                    )
                    attributes["operating_state"] = state_text
            except (ValueError, TypeError):
                attributes[
                    "operating_state"
                ] = f"Invalid state value: {operating_state}"

        return attributes

    @property
    def device_info(self):
        # Climate-Entitäten immer dem Hauptgerät zuordnen
        return build_device_info(self._entry, "main")

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        try:
            # Hole die Sensor-Information
            sensor_info = None
            # Prefix entfernen, falls vorhanden
            target_temp_sensor_noprefix = self._target_temp_sensor
            if self._target_temp_sensor.startswith(self._prefix):
                target_temp_sensor_noprefix = self._target_temp_sensor[len(self._prefix):]
            if target_temp_sensor_noprefix.startswith("boil"):
                parts = target_temp_sensor_noprefix.split("_", 1)
                if len(parts) == 2 and parts[1] in BOIL_SENSOR_TEMPLATES:
                    sensor_info = BOIL_SENSOR_TEMPLATES[parts[1]].copy()
                    idx = int(target_temp_sensor_noprefix[4])
                    sensor_info["address"] = (
                        generate_base_addresses('boil', num_boil)[idx]
                        + sensor_info["relative_address"]
                    )
            elif target_temp_sensor_noprefix.startswith("hc"):
                parts = target_temp_sensor_noprefix.split("_", 1)
                if len(parts) == 2 and parts[1] in HC_SENSOR_TEMPLATES:
                    sensor_info = HC_SENSOR_TEMPLATES[parts[1]].copy()
                    idx = int(target_temp_sensor_noprefix[2])
                    sensor_info["address"] = (
                        generate_base_addresses('hc', num_hc)[idx]
                        + sensor_info["relative_address"]
                    )
            else:
                sensor_info = SENSOR_TYPES.get(target_temp_sensor_noprefix)

            if not sensor_info:
                _LOGGER.error(
                    "No sensor definition found for %s",
                    target_temp_sensor_noprefix,
                )
                return

            # Check if the sensor is writeable
            if not sensor_info.get("writeable", False):
                _LOGGER.error(
                    "Sensor %s is not writeable",
                    target_temp_sensor_noprefix,
                )
                return

            # Berechne den Rohwert für das Register
            raw_value = int(temperature / sensor_info["scale"])

            # Schreibe den Wert in das Modbus-Register mit Holding Register Funktion
            result = await self.hass.async_add_executor_job(
                self.coordinator.client.write_registers,
                sensor_info["address"],
                [raw_value],
                self._entry.data.get("slave_id", 1)
            )

            if hasattr(result, "isError") and result.isError():
                _LOGGER.error(
                    "Failed to write target temperature: %s",
                    result,
                )
                return

            # Aktualisiere den Coordinator-Cache
            self.coordinator.data[self._target_temp_sensor] = temperature
            # Aktualisiere die Daten
            await self.coordinator.async_refresh()
            self.async_write_ha_state()
            _LOGGER.debug(
                "Successfully set target temperature to %s°C",
                temperature,
            )
        except Exception as ex:
            _LOGGER.error(
                "Error setting target temperature: %s",
                ex,
            )


class LambdaBoiler(LambdaClimateEntity):
    """Representation of a Lambda Boiler."""

    def __init__(
        self,
        coordinator: "LambdaDataUpdateCoordinator",
        climate_type: str,
        name: str,
        base_address: int,
    ) -> None:
        idx = int(climate_type.replace("boil", ""))
        super().__init__(
            coordinator=coordinator,
            entry=coordinator.entry,
            climate_type=climate_type,
            translation_key="boiler",
            current_temp_sensor=f"{climate_type}_actual_high_temperature",
            target_temp_sensor=f"{climate_type}_target_high_temperature",
            min_temp=DEFAULT_HOT_WATER_MIN_TEMP,
            max_temp=DEFAULT_HOT_WATER_MAX_TEMP,
            temp_step=1,
        )
        self._base_address = base_address
        self._attr_name = f"Boiler {idx}"
        self._attr_unique_id = f"boiler_{idx}"

    @property
    def device_info(self):
        # Boiler-Entitäten immer dem Hauptgerät zuordnen
        return build_device_info(self._entry, "main")


class LambdaHeatingCircuit(LambdaClimateEntity):
    """Representation of a Lambda Heating Circuit."""

    def __init__(
        self,
        coordinator: "LambdaDataUpdateCoordinator",
        climate_type: str,
        name: str,
        base_address: int,
    ) -> None:
        idx = int(climate_type.replace("hc", ""))
        super().__init__(
            coordinator=coordinator,
            entry=coordinator.entry,
            climate_type=climate_type,
            translation_key="heating_circuit",
            current_temp_sensor=f"{climate_type}_room_device_temperature",
            target_temp_sensor=f"{climate_type}_target_room_temperature",
            min_temp=DEFAULT_HEATING_CIRCUIT_MIN_TEMP,
            max_temp=DEFAULT_HEATING_CIRCUIT_MAX_TEMP,
            temp_step=DEFAULT_HEATING_CIRCUIT_TEMP_STEP,
        )
        self._base_address = base_address
        self._attr_name = f"Heizkreis {idx}"
        self._attr_unique_id = f"hc_{idx}"

    @property
    def device_info(self):
        # Heating Circuit-Entitäten immer dem Hauptgerät zuordnen
        return build_device_info(self._entry, "main")
