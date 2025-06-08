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
    BUFF_SENSOR_TEMPLATES,
    SOL_SENSOR_TEMPLATES,
)
from .const_mapping import *  # Import all state mappings
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

    # Create sensors for each device type using a generic loop
    sensors = []

    TEMPLATES = [
        ("hp", num_hps, HP_SENSOR_TEMPLATES),
        ("boil", num_boil, BOIL_SENSOR_TEMPLATES),
        ("buff", num_buff, BUFF_SENSOR_TEMPLATES),
        ("sol", num_sol, SOL_SENSOR_TEMPLATES),
        ("hc", num_hc, HC_SENSOR_TEMPLATES),
    ]

    for prefix, count, template in TEMPLATES:
        for idx in range(1, count + 1):
            base_address = generate_base_addresses(prefix, count)[idx]
            for sensor_id, sensor_info in template.items():
                address = base_address + sensor_info["relative_address"]
                if coordinator.is_register_disabled(address):
                    _LOGGER.debug("Skipping sensor %s (address %d) because register is disabled", f"{prefix}{idx}_{sensor_id}", address)
                    continue
                device_class = sensor_info.get("device_class")
                if not device_class and sensor_info.get("unit") == "°C":
                    device_class = SensorDeviceClass.TEMPERATURE
                elif not device_class and sensor_info.get("unit") == "W":
                    device_class = SensorDeviceClass.POWER
                elif not device_class and sensor_info.get("unit") == "Wh":
                    device_class = SensorDeviceClass.ENERGY

                # Generate name based on prefix and sensor info
                prefix_upper = prefix.upper()
                if prefix == "hc" and sensor_info.get("device_type") == "Climate":
                    # Climate sensors keep original name format
                    name = sensor_info["name"].format(idx)
                else:
                    # Other sensors include prefix in name
                    name = f"{prefix_upper}{idx} {sensor_info['name']}"

                # Ensure correct device_type based on prefix
                device_type = prefix.upper() if prefix in ["hp", "boil", "hc", "buff", "sol"] else sensor_info.get("device_type", "main")

                sensors.append(
                    LambdaSensor(
                        coordinator=coordinator,
                        entry=entry,
                        sensor_id=f"{prefix}{idx}_{sensor_id}",
                        name=name,
                        unit=sensor_info.get("unit", ""),
                        address=address,
                        scale=sensor_info.get("scale", 1.0),
                        state_class=sensor_info.get("state_class", ""),
                        device_class=device_class,
                        relative_address=sensor_info.get("relative_address", 0),
                        data_type=sensor_info.get("data_type", None),
                        device_type=device_type,
                        txt_mapping=sensor_info.get("txt_mapping", False),
                        precision=sensor_info.get("precision", None),
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
        relative_address: int,
        data_type: str,
        device_type: str,
        txt_mapping: bool = False,
        precision: int | float | None = None,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._sensor_id = sensor_id
        self._attr_name = name
        self._attr_unique_id = sensor_id
        self.entity_id = f"sensor.{sensor_id}"
        self._unit = unit
        self._address = address
        self._scale = scale
        self._state_class = state_class
        self._device_class = device_class
        self._relative_address = relative_address
        self._data_type = data_type
        self._device_type = device_type
        self._txt_mapping = txt_mapping
        self._precision = precision

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
                "relative_address": relative_address,
                "data_type": data_type,
                "device_type": device_type,
                "txt_mapping": txt_mapping,
                "precision": precision,
            },
        )

        self._is_state_sensor = txt_mapping

        if self._is_state_sensor:
            self._attr_device_class = None
            self._attr_state_class = None
            self._attr_native_unit_of_measurement = None
            self._attr_suggested_display_precision = None
        else:
            self._attr_native_unit_of_measurement = unit
            if precision is not None:
                self._attr_suggested_display_precision = precision
            if unit == "°C":
                self._attr_device_class = SensorDeviceClass.TEMPERATURE
            elif unit == "W":
                self._attr_device_class = SensorDeviceClass.POWER
            elif unit == "Wh":
                self._attr_device_class = SensorDeviceClass.ENERGY
            if state_class:
                if state_class == "total":
                    self._attr_state_class = SensorStateClass.TOTAL
                elif state_class == "total_increasing":
                    self._attr_state_class = SensorStateClass.TOTAL_INCREASING
                elif state_class == "measurement":
                    self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | str | None:
        if not self.coordinator.data:
            return None
        value = self.coordinator.data.get(self._sensor_id)
        if value is None:
            return None
        if self._is_state_sensor:
            try:
                numeric_value = int(float(value))
            except (ValueError, TypeError):
                return f"Unknown state ({value})"
            
            # Extract base name without index (e.g. "HP1 Operating State" -> "Operating State")
            base_name = self._attr_name
            if self._device_type and self._device_type.upper() in base_name:
                # Remove prefix and index (e.g. "HP1 " or "BOIL2 ")
                base_name = ' '.join(base_name.split()[1:])
            
            mapping_name = f"{self._device_type.upper()}_{base_name.upper().replace(' ', '_')}"
            try:
                state_mapping = globals().get(mapping_name)
                if state_mapping is not None:
                    return state_mapping.get(numeric_value, f"Unknown state ({numeric_value})")
                _LOGGER.warning(
                    "No state mapping found for sensor '%s' (tried mapping name: %s) with value %s. "
                    "Sensor details: device_type=%s, register=%d, data_type=%s. "
                    "This sensor is marked as state sensor (txt_mapping=True) but no corresponding mapping dictionary was found.",
                    self._attr_name,
                    mapping_name,
                    numeric_value,
                    self._device_type,
                    self._relative_address,
                    self._data_type
                )
                return f"Unknown mapping for state ({numeric_value})"
            except Exception as e:
                _LOGGER.error("Error accessing mapping dictionary: %s", str(e))
                return f"Error loading mappings ({numeric_value})"
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @property
    def device_info(self):
        """Return device info for this sensor."""
        # Use device_type from sensor template, defaulting to "main" if not set
        device_type = self._device_type.lower() if self._device_type else "main"
        
        # Extract index from sensor_id if it exists
        idx = None
        if self._sensor_id:
            parts = self._sensor_id.split('_')
            if len(parts) > 0:
                # Extract number from prefix (e.g., "hp1" -> 1)
                import re
                match = re.search(r'\d+', parts[0])
                if match:
                    idx = int(match.group())
        
        return build_device_info(self._entry, device_type, idx)
