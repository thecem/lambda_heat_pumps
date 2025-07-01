"""Template sensor platform for Lambda WP integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.components.template import Template
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.template import TemplateError
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CALCULATED_SENSOR_TEMPLATES,
)
from .coordinator import LambdaDataUpdateCoordinator
from .utils import build_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Lambda Template sensors."""
    _LOGGER.debug("Setting up Lambda template sensors for entry %s", entry.entry_id)

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

    # Hole den Legacy-Modbus-Namen-Switch aus der Config
    use_legacy_modbus_names = entry.data.get("use_legacy_modbus_names", False)
    name_prefix = entry.data.get("name", "").lower().replace(" ", "")

    # Create template sensors for each device type
    template_sensors = []

    # Device type mapping
    DEVICE_COUNTS = {
        "hp": num_hps,
        "boil": num_boil,
        "buff": num_buff,
        "sol": num_sol,
        "hc": num_hc,
    }

    # Create template sensors for each device type
    for device_type, count in DEVICE_COUNTS.items():
        for idx in range(1, count + 1):
            device_prefix = f"{device_type}{idx}"
            
            # Filter template sensors for this device type
            for sensor_id, sensor_info in CALCULATED_SENSOR_TEMPLATES.items():
                if sensor_info.get("device_type") == device_type:
                    # Create device prefix for template
                    template_device_prefix = device_prefix
                    
                    # Handle legacy naming
                    if use_legacy_modbus_names:
                        name = f"{name_prefix.upper()}{idx} {sensor_info['name']}"
                        entity_id = f"sensor.{name_prefix}_{device_prefix}_{sensor_id}"
                        unique_id = f"{name_prefix}_{device_prefix}_{sensor_id}"
                    else:
                        name = f"{device_prefix.upper()} {sensor_info['name']}"
                        entity_id = f"sensor.{device_prefix}_{sensor_id}"
                        unique_id = f"{device_prefix}_{sensor_id}"

                    # Create template with device prefix
                    template_str = sensor_info["template"].format(
                        device_prefix=template_device_prefix
                    )
                    
                    template_sensors.append(
                        LambdaTemplateSensor(
                            coordinator=coordinator,
                            entry=entry,
                            sensor_id=f"{device_prefix}_{sensor_id}",
                            name=name,
                            unit=sensor_info.get("unit", ""),
                            state_class=sensor_info.get("state_class", ""),
                            device_class=sensor_info.get("device_class"),
                            device_type=device_type.upper(),
                            precision=sensor_info.get("precision"),
                            entity_id=entity_id,
                            unique_id=unique_id,
                            template_str=template_str,
                        )
                    )

    if template_sensors:
        async_add_entities(template_sensors)
        _LOGGER.debug("Added %d template sensors", len(template_sensors))


class LambdaTemplateSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Lambda template sensor."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: LambdaDataUpdateCoordinator,
        entry: ConfigEntry,
        sensor_id: str,
        name: str,
        unit: str,
        state_class: str,
        device_class: SensorDeviceClass,
        device_type: str,
        precision: int | float | None = None,
        entity_id: str | None = None,
        unique_id: str | None = None,
        template_str: str = "",
    ) -> None:
        """Initialize the template sensor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._entry = entry
        self._sensor_id = sensor_id
        self._name = name
        self._unit = unit
        self._state_class = state_class
        self._device_class = device_class
        self._device_type = device_type
        self._precision = precision
        self._entity_id = entity_id
        self._unique_id = unique_id
        self._template_str = template_str
        self._template = Template(template_str, self.hass)
        self._state = None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def native_value(self) -> float | str | None:
        """Return the state of the sensor."""
        return self._state

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor."""
        return self._unit

    @property
    def state_class(self) -> SensorStateClass | None:
        """Return the state class of the sensor."""
        if self._state_class == "measurement":
            return SensorStateClass.MEASUREMENT
        elif self._state_class == "total":
            return SensorStateClass.TOTAL
        elif self._state_class == "total_increasing":
            return SensorStateClass.TOTAL_INCREASING
        return None

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the device class of the sensor."""
        if self._device_class == "temperature":
            return SensorDeviceClass.TEMPERATURE
        elif self._device_class == "power":
            return SensorDeviceClass.POWER
        elif self._device_class == "energy":
            return SensorDeviceClass.ENERGY
        return None

    @property
    def device_info(self):
        """Return device info."""
        return build_device_info(
            self._entry,
            self._device_type,
            self._sensor_id,
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        try:
            # Render the template
            self._state = self._template.async_render()
            
            # Convert to float if possible and apply precision
            if self._state is not None and self._state != "unavailable":
                try:
                    float_value = float(self._state)
                    if self._precision is not None:
                        self._state = round(float_value, self._precision)
                    else:
                        self._state = float_value
                except (ValueError, TypeError):
                    # Keep as string if conversion fails
                    pass
                    
        except TemplateError as err:
            _LOGGER.warning(
                "Template error for sensor %s: %s", self._sensor_id, err
            )
            self._state = None

        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update() 