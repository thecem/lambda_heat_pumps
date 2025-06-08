"""Climate platform for Lambda integration (template-basiert)."""
from __future__ import annotations
import logging

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CLIMATE_TEMPLATES
from .utils import generate_base_addresses, build_device_info
from .coordinator import LambdaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class LambdaClimateEntity(CoordinatorEntity, ClimateEntity):
    """Template-basierte Lambda Climate Entity."""

    _attr_should_poll = False
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

    def __init__(self, coordinator, entry, device_type, idx, base_address):
        super().__init__(coordinator)
        self._entry = entry
        self._device_type = device_type  # "hot_water" oder "heating_circuit"
        self._idx = idx
        self._base_address = base_address
        self._template = CLIMATE_TEMPLATES[device_type]

        # Dynamische Namen und IDs
        self._attr_name = f"{self._template['name']} {idx}"
        self._attr_unique_id = f"{DOMAIN}_{device_type}_{idx}"
        self.entity_id = f"climate.{DOMAIN}_{device_type}_{idx}"

        # Temperaturbereich und Schrittweite
        self._attr_min_temp = 40 if device_type == "hot_water" else 20
        self._attr_max_temp = 60 if device_type == "hot_water" else 45
        self._attr_target_temperature_step = self._template.get("precision", 0.5)
        self._attr_temperature_unit = self._template.get("unit", "°C")
        self._attr_hvac_modes = [HVACMode.HEAT]
        self._attr_hvac_mode = HVACMode.HEAT

    @property
    def current_temperature(self):
        key = (
            f"boil{self._idx}_actual_high_temperature"
            if self._device_type == "hot_water"
            else f"hc{self._idx}_room_device_temperature"
        )
        return self.coordinator.data.get(key)

    @property
    def target_temperature(self):
        key = (
            f"boil{self._idx}_target_high_temperature"
            if self._device_type == "hot_water"
            else f"hc{self._idx}_target_room_temperature"
        )
        return self.coordinator.data.get(key)

    @property
    def state_class(self):
        return self._template.get("state_class")

    @property
    def device_info(self):
        return build_device_info(self._entry, "main")

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get("temperature")
        if temperature is None:
            return
        reg_addr = self._base_address + self._template["relative_set_address"]
        scale = self._template["scale"]
        raw_value = int(temperature / scale)
        _LOGGER.debug(
            "[Climate] Write target temperature: entity=%s, address=%s, value(raw)=%s, value(temp)=%s",
            self.entity_id, reg_addr, raw_value, temperature
        )
        result = await self.hass.async_add_executor_job(
            self.coordinator.client.write_registers,
            reg_addr,
            [raw_value],
            self._entry.data.get("slave_id", 1)
        )
        if hasattr(result, "isError") and result.isError():
            _LOGGER.error("Failed to write target temperature: %s", result)
            return
        key = (
            f"boil{self._idx}_target_high_temperature"
            if self._device_type == "hot_water"
            else f"hc{self._idx}_target_room_temperature"
        )
        self.coordinator.data[key] = temperature
        await self.coordinator.async_refresh()
        self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Lambda Heat Pumps climate entities (template-basiert)."""
    _LOGGER.debug("Setting up Lambda climate entities for entry %s", entry.entry_id)
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    num_boil = entry.data.get("num_boil", 1)
    num_hc = entry.data.get("num_hc", 1)
    entities = []

    # Boiler
    boil_addresses = generate_base_addresses("boil", num_boil)
    for idx in range(1, num_boil + 1):
        entities.append(
            LambdaClimateEntity(
                coordinator,
                entry,
                "hot_water",
                idx,
                boil_addresses[idx]
            )
        )

    # Heating Circuits
    hc_addresses = generate_base_addresses("hc", num_hc)
    for idx in range(1, num_hc + 1):
        entity_key = f"room_temperature_entity_{idx}"
        if not entry.options.get(entity_key):
            _LOGGER.debug(
                "No room temperature entity configured for heating circuit %s in entry %s, skipping entity creation.",
                idx, entry.entry_id
            )
            continue
        entities.append(
            LambdaClimateEntity(
                coordinator,
                entry,
                "heating_circuit",
                idx,
                hc_addresses[idx]
            )
        )

    async_add_entities(entities)
