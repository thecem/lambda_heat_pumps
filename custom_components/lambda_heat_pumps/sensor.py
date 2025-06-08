"""Platform for Lambda WP sensor integration."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SENSOR_TYPES,
    FIRMWARE_VERSION,
    HP_SENSOR_TEMPLATES,
    BOIL_SENSOR_TEMPLATES,
    HC_SENSOR_TEMPLATES,
    BUFFER_SENSOR_TEMPLATES,
    SOLAR_SENSOR_TEMPLATES,
    SOLAR_OPERATION_STATE,
    BUFFER_OPERATION_STATE,
    BUFFER_REQUEST_TYPE,
)
from .coordinator import LambdaDataUpdateCoordinator
from .utils import get_compatible_sensors, build_device_info, generate_base_addresses

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Lambda Heat Pumps sensors."""
    _LOGGER.debug("Setting up Lambda sensors for entry %s", entry.entry_id)
    
    # Get coordinator from hass.data
    coordinator_data = hass.data[DOMAIN][entry.entry_id]
    if not coordinator_data or "coordinator" not in coordinator_data:
        _LOGGER.error("No coordinator found for entry %s", entry.entry_id)
        return
        
    coordinator = coordinator_data["coordinator"]
    _LOGGER.debug("Found coordinator: %s", coordinator)

    # Get device counts from config
    num_hps = entry.data.get("num_hps", 1)
    num_boil = entry.data.get("num_boil", 1)
    num_buff = entry.data.get("num_buff", 0)
    num_sol = entry.data.get("num_sol", 0)
    num_hc = entry.data.get("num_hc", 1)

    # Create sensors for each device type
    sensors = []

    # Heat Pump sensors
    for hp_idx in range(1, num_hps + 1):
        base_address = generate_base_addresses('hp', num_hps)[hp_idx]
        for sensor_id, sensor_info in HP_SENSOR_TEMPLATES.items():
            # Set default device class based on unit if not specified
            device_class = sensor_info.get("device_class")
            if not device_class and sensor_info.get("unit") == "°C":
                device_class = SensorDeviceClass.TEMPERATURE
            elif not device_class and sensor_info.get("unit") == "W":
                device_class = SensorDeviceClass.POWER
            elif not device_class and sensor_info.get("unit") == "Wh":
                device_class = SensorDeviceClass.ENERGY

            sensors.append(
                LambdaSensor(
                    coordinator=coordinator,
                    entry=entry,
                    sensor_id=f"hp{hp_idx}_{sensor_id}",
                    name=sensor_info["name"].format(hp_idx),
                    unit=sensor_info.get("unit", ""),
                    address=base_address + sensor_info["relative_address"],
                    scale=sensor_info.get("scale", 1.0),
                    state_class=sensor_info.get("state_class", ""),
                    device_class=device_class,
                )
            )

    # Boiler sensors
    for boil_idx in range(1, num_boil + 1):
        base_address = generate_base_addresses('boil', num_boil)[boil_idx]
        for sensor_id, sensor_info in BOIL_SENSOR_TEMPLATES.items():
            # Set default device class based on unit if not specified
            device_class = sensor_info.get("device_class")
            if not device_class and sensor_info.get("unit") == "°C":
                device_class = SensorDeviceClass.TEMPERATURE
            elif not device_class and sensor_info.get("unit") == "W":
                device_class = SensorDeviceClass.POWER
            elif not device_class and sensor_info.get("unit") == "Wh":
                device_class = SensorDeviceClass.ENERGY

            sensors.append(
                LambdaSensor(
                    coordinator=coordinator,
                    entry=entry,
                    sensor_id=f"boil{boil_idx}_{sensor_id}",
                    name=sensor_info["name"].format(boil_idx),
                    unit=sensor_info.get("unit", ""),
                    address=base_address + sensor_info["relative_address"],
                    scale=sensor_info.get("scale", 1.0),
                    state_class=sensor_info.get("state_class", ""),
                    device_class=device_class,
                )
            )

    # Buffer sensors
    for buff_idx in range(1, num_buff + 1):
        base_address = generate_base_addresses('buff', num_buff)[buff_idx]
        for sensor_id, sensor_info in BUFFER_SENSOR_TEMPLATES.items():
            # Set default device class based on unit if not specified
            device_class = sensor_info.get("device_class")
            if not device_class and sensor_info.get("unit") == "°C":
                device_class = SensorDeviceClass.TEMPERATURE
            elif not device_class and sensor_info.get("unit") == "W":
                device_class = SensorDeviceClass.POWER
            elif not device_class and sensor_info.get("unit") == "Wh":
                device_class = SensorDeviceClass.ENERGY

            sensors.append(
                LambdaSensor(
                    coordinator=coordinator,
                    entry=entry,
                    sensor_id=f"buff{buff_idx}_{sensor_id}",
                    name=sensor_info["name"].format(buff_idx),
                    unit=sensor_info.get("unit", ""),
                    address=base_address + sensor_info["relative_address"],
                    scale=sensor_info.get("scale", 1.0),
                    state_class=sensor_info.get("state_class", ""),
                    device_class=device_class,
                )
            )

    # Solar sensors
    for sol_idx in range(1, num_sol + 1):
        base_address = generate_base_addresses('sol', num_sol)[sol_idx]
        for sensor_id, sensor_info in SOLAR_SENSOR_TEMPLATES.items():
            # Set default device class based on unit if not specified
            device_class = sensor_info.get("device_class")
            if not device_class and sensor_info.get("unit") == "°C":
                device_class = SensorDeviceClass.TEMPERATURE
            elif not device_class and sensor_info.get("unit") == "W":
                device_class = SensorDeviceClass.POWER
            elif not device_class and sensor_info.get("unit") == "Wh":
                device_class = SensorDeviceClass.ENERGY

            sensors.append(
                LambdaSensor(
                    coordinator=coordinator,
                    entry=entry,
                    sensor_id=f"sol{sol_idx}_{sensor_id}",
                    name=sensor_info["name"].format(sol_idx),
                    unit=sensor_info.get("unit", ""),
                    address=base_address + sensor_info["relative_address"],
                    scale=sensor_info.get("scale", 1.0),
                    state_class=sensor_info.get("state_class", ""),
                    device_class=device_class,
                )
            )

    # Heating Circuit sensors
    for hc_idx in range(1, num_hc + 1):
        base_address = generate_base_addresses('hc', num_hc)[hc_idx]
        for sensor_id, sensor_info in HC_SENSOR_TEMPLATES.items():
            # Set default device class based on unit if not specified
            device_class = sensor_info.get("device_class")
            if not device_class and sensor_info.get("unit") == "°C":
                device_class = SensorDeviceClass.TEMPERATURE
            elif not device_class and sensor_info.get("unit") == "W":
                device_class = SensorDeviceClass.POWER
            elif not device_class and sensor_info.get("unit") == "Wh":
                device_class = SensorDeviceClass.ENERGY

            sensors.append(
                LambdaSensor(
                    coordinator=coordinator,
                    entry=entry,
                    sensor_id=f"hc{hc_idx}_{sensor_id}",
                    name=sensor_info["name"].format(hc_idx),
                    unit=sensor_info.get("unit", ""),
                    address=base_address + sensor_info["relative_address"],
                    scale=sensor_info.get("scale", 1.0),
                    state_class=sensor_info.get("state_class", ""),
                    device_class=device_class,
                )
            )

    _LOGGER.debug("Created %d sensors", len(sensors))
    async_add_entities(sensors)


class LambdaSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Lambda sensor."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: LambdaDataUpdateCoordinator,
        entry: ConfigEntry,
        sensor_id: str,
        name: str,
        unit: str,
        address: int,
        scale: float,
        state_class: str,
        device_class: SensorDeviceClass,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._sensor_id = sensor_id
        self._attr_name = name
        self._attr_unique_id = sensor_id
        self.entity_id = f"sensor.{sensor_id}"

        _LOGGER.debug(
            "Sensor initialized with ID: %s and config: %s",
            sensor_id,
            {
                "name": name,
                "unit": unit,
                "address": address,
                "scale": scale,
                "state_class": state_class,
                "device_class": device_class,
            },
        )

        # Hole die Sensor-Info aus dem entsprechenden Template
        device_type = sensor_id.split('_')[0][:-1]  # z.B. "hp" aus "hp1_..."
        sensor_key = sensor_id.split('_', 1)[1]  # z.B. "error_state" aus "hp1_error_state"
        
        if device_type == "hp":
            sensor_info = HP_SENSOR_TEMPLATES.get(sensor_key, {})
        elif device_type == "boil":
            sensor_info = BOIL_SENSOR_TEMPLATES.get(sensor_key, {})
        elif device_type == "buff":
            sensor_info = BUFFER_SENSOR_TEMPLATES.get(sensor_key, {})
        elif device_type == "sol":
            sensor_info = SOLAR_SENSOR_TEMPLATES.get(sensor_key, {})
        elif device_type == "hc":
            sensor_info = HC_SENSOR_TEMPLATES.get(sensor_key, {})
        else:
            sensor_info = SENSOR_TYPES.get(sensor_key, {})

        # Bestimme, ob es sich um einen Status-/Mode-Sensor handelt
        self._is_state_sensor = sensor_info.get("txt_mapping", False)

        if self._is_state_sensor:
            # Für Status-/Mode-Sensoren: Keine Metadaten setzen
            self._attr_device_class = None
            self._attr_state_class = None
            self._attr_native_unit_of_measurement = None
            self._attr_suggested_display_precision = None
        else:
            # Für numerische Sensoren: Metadaten aus der Konfiguration übernehmen
            self._attr_native_unit_of_measurement = unit
            if "precision" in sensor_info:
                self._attr_suggested_display_precision = sensor_info["precision"]

            if unit == "°C":
                self._attr_device_class = SensorDeviceClass.TEMPERATURE
            elif unit == "W":
                self._attr_device_class = SensorDeviceClass.POWER
            elif unit == "Wh":
                self._attr_device_class = SensorDeviceClass.ENERGY

            # State-Class nur für numerische Sensoren setzen
            if state_class:
                if state_class == "total":
                    self._attr_state_class = SensorStateClass.TOTAL
                elif state_class == "total_increasing":
                    self._attr_state_class = SensorStateClass.TOTAL_INCREASING
                elif state_class == "measurement":
                    self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | str | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        value = self.coordinator.data.get(self._sensor_id)
        if value is None:
            return None

        if self._is_state_sensor:
            from .const import (
                AMBIENT_OPERATING_STATE,
                EMGR_OPERATING_STATE,
                HP_ERROR_STATE,
                HP_STATE,
                HP_OPERATING_STATE,
                BOIL_OPERATING_STATE,
                HC_OPERATING_STATE,
                HC_OPERATING_MODE,
                CIRCULATION_PUMP_STATE,
                SOLAR_OPERATION_STATE,
                BUFFER_OPERATION_STATE,
                BUFFER_REQUEST_TYPE,
            )

            try:
                numeric_value = int(float(value))  # robust für int/float-Strings
            except (ValueError, TypeError):
                return f"Unknown state ({value})"

            state_mapping = None
            if "ambient_operating_state" in self._sensor_id:
                state_mapping = AMBIENT_OPERATING_STATE
            elif "emgr_operating_state" in self._sensor_id:
                state_mapping = EMGR_OPERATING_STATE
            elif "actual_circulation_pump_state" in self._sensor_id:
                state_mapping = CIRCULATION_PUMP_STATE
            elif (
                "operating_state" in self._sensor_id
                and "solar" in self._sensor_id
            ):
                state_mapping = SOLAR_OPERATION_STATE
            elif (
                "operating_state" in self._sensor_id
                and "buffer" in self._sensor_id
            ):
                state_mapping = BUFFER_OPERATION_STATE
            elif (
                "request_type" in self._sensor_id
                and "buffer" in self._sensor_id
            ):
                state_mapping = BUFFER_REQUEST_TYPE
            elif "error_state" in self._sensor_id:
                state_mapping = HP_ERROR_STATE
            elif "_state" in self._sensor_id:
                if "hp" in self._sensor_id and "operating" not in self._sensor_id:
                    state_mapping = HP_STATE
                elif "hp" in self._sensor_id and "operating" in self._sensor_id:
                    state_mapping = HP_OPERATING_STATE
                elif "boil" in self._sensor_id:
                    state_mapping = BOIL_OPERATING_STATE
                elif "hc" in self._sensor_id:
                    state_mapping = HC_OPERATING_STATE
            elif "operating_mode" in self._sensor_id:
                state_mapping = HC_OPERATING_MODE

            if state_mapping is not None:
                return state_mapping.get(numeric_value, f"Unknown state ({numeric_value})")
            
            # Warnung ausgeben, wenn kein Mapping gefunden wurde
            _LOGGER.warning(
                "No state mapping found for sensor %s with value %s. This sensor is marked as state sensor (txt_mapping=True) but no corresponding mapping dictionary was found.",
                self._sensor_id,
                numeric_value
            )
            return f"Unknown mapping for state ({numeric_value})"

        # Für numerische Sensoren: Float zurückgeben
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @property
    def device_info(self):
        # Versuche Instanztyp und Index aus sensor_id zu extrahieren
        # Beispiel: hp1_..., boil2_..., hc1_..., buff1_..., sol1_...
        import re
        sensor_id = self._sensor_id
        if sensor_id.startswith("hp"):
            m = re.match(r"hp(\d+)_", sensor_id)
            if m:
                return build_device_info(self._entry, "hp", int(m.group(1)))
        elif sensor_id.startswith("boil"):
            m = re.match(r"boil(\d+)_", sensor_id)
            if m:
                return build_device_info(self._entry, "boil", int(m.group(1)))
        elif sensor_id.startswith("hc"):
            m = re.match(r"hc(\d+)_", sensor_id)
            if m:
                return build_device_info(self._entry, "hc", int(m.group(1)))
        elif sensor_id.startswith("buff"):
            m = re.match(r"buff(\d+)_", sensor_id)
            if m:
                return build_device_info(self._entry, "buffer", int(m.group(1)))
        elif sensor_id.startswith("sol"):
            m = re.match(r"sol(\d+)_", sensor_id)
            if m:
                return build_device_info(self._entry, "solar", int(m.group(1)))
        # Fallback: Hauptgerät
        return build_device_info(self._entry, "main")
