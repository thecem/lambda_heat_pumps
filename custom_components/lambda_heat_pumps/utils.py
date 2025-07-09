"""Utility functions for Lambda Heat Pumps integration."""

import logging
import os
import yaml
import aiofiles
from homeassistant.core import HomeAssistant
from .const import (
    BASE_ADDRESSES,
)

_LOGGER = logging.getLogger(__name__)


def get_compatible_sensors(sensor_templates: dict, fw_version: int) -> dict:
    """Return only sensors compatible with the given firmware version.
    Args:
       sensor_templates: Dictionary of sensor templates
       fw_version: The firmware version to check against
    Returns:
       Filtered dictionary of compatible sensors
    """
    return {
        k: v
        for k, v in sensor_templates.items()
        if v.get("firmware_version", 1) <= fw_version
    }


def build_device_info(entry, device_type, idx=None, sensor_id=None):
    """
    Build device_info dict for Home Assistant device registry.
    device_type: wird ignoriert, alle Entities gehören zum Main-Device
    """
    DOMAIN = entry.domain if hasattr(entry, "domain") else "lambda_heat_pumps"
    entry_id = entry.entry_id
    fw_version = entry.data.get("firmware_version", "unknown")
    host = entry.data.get("host")
    return {
        "identifiers": {(DOMAIN, entry_id)},
        "name": entry.data.get("name", "Lambda WP"),
        "manufacturer": "Lambda",
        "model": fw_version,
        "configuration_url": f"http://{host}",
        "sw_version": fw_version,
        "entry_type": None,
        "suggested_area": None,
        "via_device": None,
        "hw_version": None,
        "serial_number": None,
    }


async def migrate_lambda_config(hass: HomeAssistant) -> bool:
    """Migrate existing lambda_wp_config.yaml to include cycling_offsets.
    
    Returns:
        bool: True if migration was performed, False otherwise
    """
    config_dir = hass.config.config_dir
    lambda_config_path = os.path.join(config_dir, "lambda_wp_config.yaml")
    
    if not os.path.exists(lambda_config_path):
        _LOGGER.debug("No existing lambda_wp_config.yaml found, no migration needed")
        return False
    
    try:
        # Read current config
        async with aiofiles.open(lambda_config_path, "r") as file:
            content = await file.read()
            current_config = yaml.safe_load(content)
        
        if not current_config:
            _LOGGER.debug("Empty config file, no migration needed")
            return False
        
        # Check if cycling_offsets already exists
        if "cycling_offsets" in current_config:
            _LOGGER.info(
                "lambda_wp_config.yaml already contains cycling_offsets - "
                "no migration needed"
            )
            return False
        
        _LOGGER.info("Migrating lambda_wp_config.yaml to include cycling_offsets")
        
        # Create backup
        backup_path = lambda_config_path + ".backup"
        async with aiofiles.open(backup_path, "w") as backup_file:
            await backup_file.write(content)
        _LOGGER.info("Created backup at %s", backup_path)
        
        # Add cycling_offsets section
        current_config["cycling_offsets"] = {
            "hp1": {
                "heating_cycling_total": 0,
                "hot_water_cycling_total": 0,
                "cooling_cycling_total": 0,
                "defrost_cycling_total": 0
            }
        }
        
        # Add documentation comment
        if "# Cycling counter offsets" not in content:
            # Insert cycling_offsets documentation before the existing sections
            cycling_docs = """# Cycling counter offsets for total sensors
# These offsets are added to the calculated cycling counts
# Useful when replacing heat pumps or resetting counters
# Example:
#cycling_offsets:
#  hp1:
#    heating_cycling_total: 0      # Offset for HP1 heating total cycles
#    hot_water_cycling_total: 0    # Offset for HP1 hot water total cycles
#    cooling_cycling_total: 0      # Offset for HP1 cooling total cycles
#  hp2:
#    heating_cycling_total: 1500   # Example: HP2 already had 1500 heating cycles
#    hot_water_cycling_total: 800  # Example: HP2 already had 800 hot water cycles
#    cooling_cycling_total: 200    # Example: HP2 already had 200 cooling cycles

"""
            # Find a good place to insert the documentation
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('disabled_registers:'):
                    insert_pos = i
                    break
            
            lines.insert(insert_pos, cycling_docs.rstrip())
            content = '\n'.join(lines)
        
        # Write updated config
        async with aiofiles.open(lambda_config_path, "w") as file:
            await file.write(content)
        
        _LOGGER.info(
            "Successfully migrated lambda_wp_config.yaml to version 1.1.0 - "
            "Added cycling_offsets section with default values for hp1. "
            "Backup created at %s.backup", lambda_config_path
        )
        return True
        
    except Exception as e:
        _LOGGER.error("Error during config migration: %s", e)
        return False


async def load_lambda_config(hass: HomeAssistant) -> dict:
    """Load complete Lambda configuration from lambda_wp_config.yaml."""
    # First, try to migrate if needed
    await migrate_lambda_config(hass)
    
    config_dir = hass.config.config_dir
    lambda_config_path = os.path.join(config_dir, "lambda_wp_config.yaml")
    
    default_config = {
        "disabled_registers": set(),
        "sensors_names_override": {},
        "cycling_offsets": {}
    }
    
    if not os.path.exists(lambda_config_path):
        _LOGGER.warning(
            "lambda_wp_config.yaml not found, using default configuration"
        )
        return default_config
    
    try:
        async with aiofiles.open(lambda_config_path, "r") as file:
            content = await file.read()
            config = yaml.safe_load(content)
            
            if not config:
                _LOGGER.warning(
                    "lambda_wp_config.yaml is empty, using default configuration"
                )
                return default_config
            
            # Load disabled registers
            disabled_registers = set()
            if "disabled_registers" in config:
                try:
                    disabled_registers = set(int(x) for x in config["disabled_registers"])
                except (ValueError, TypeError) as e:
                    _LOGGER.error(
                        "Invalid disabled_registers format: %s", e
                    )
                    disabled_registers = set()
            
            # Load sensor overrides
            sensors_names_override = {}
            if "sensors_names_override" in config:
                try:
                    for override in config["sensors_names_override"]:
                        if "id" in override and "override_name" in override:
                            sensors_names_override[override["id"]] = (
                                override["override_name"]
                            )
                except (TypeError, KeyError) as e:
                    _LOGGER.error(
                        "Invalid sensors_names_override format: %s", e
                    )
                    sensors_names_override = {}
            
            # Load cycling offsets
            cycling_offsets = {}
            if "cycling_offsets" in config:
                try:
                    cycling_offsets = config["cycling_offsets"]
                    # Validate cycling offsets structure
                    for device, offsets in cycling_offsets.items():
                        if not isinstance(offsets, dict):
                            _LOGGER.warning(
                                "Invalid cycling_offsets format for device %s", 
                                device
                            )
                            continue
                        for offset_type, value in offsets.items():
                            if not isinstance(value, (int, float)):
                                _LOGGER.warning(
                                    "Invalid cycling offset value for %s.%s: %s", 
                                    device, offset_type, value
                                )
                                cycling_offsets[device][offset_type] = 0
                except (TypeError, KeyError) as e:
                    _LOGGER.error(
                        "Invalid cycling_offsets format: %s", e
                    )
                    cycling_offsets = {}
            
            _LOGGER.debug(
                "Loaded Lambda config: %d disabled registers, %d sensor "
                "overrides, %d device offsets",
                len(disabled_registers),
                len(sensors_names_override),
                len(cycling_offsets)
            )
            
            return {
                "disabled_registers": disabled_registers,
                "sensors_names_override": sensors_names_override,
                "cycling_offsets": cycling_offsets
            }
            
    except Exception as e:
        _LOGGER.error(
            "Error loading configuration from lambda_wp_config.yaml: %s",
            str(e),
        )
        return default_config


# Keep the old function for backward compatibility
async def load_disabled_registers(hass: HomeAssistant) -> set[int]:
    """Load disabled registers from lambda_wp_config in config directory.
    
    DEPRECATED: Use load_lambda_config() instead.
    """
    config = await load_lambda_config(hass)
    return config["disabled_registers"]


def is_register_disabled(address: int, disabled_registers: set[int]) -> bool:
    """Check if a register is disabled.

    Args:
        address: The register address to check
        disabled_registers: Set of disabled register addresses

    Returns:
        bool: True if the register is disabled, False otherwise
    """
    is_disabled = address in disabled_registers
    if is_disabled:
        _LOGGER.debug(
            "Register %d is disabled (in set: %s)",
            address,
            disabled_registers,
        )
    return is_disabled


def generate_base_addresses(device_type: str, count: int) -> dict:
    """Generate base addresses for a given device type and count.

    Args:
        device_type: Type of device (hp, boil, buff, sol, hc)
        count: Number of devices

    Returns:
        dict: Dictionary with device numbers as keys
        and base addresses as values
    """
    base_addresses = BASE_ADDRESSES

    start_address = base_addresses.get(device_type, 0)
    if start_address == 0:
        return {}

    return {i: start_address + (i - 1) * 100 for i in range(1, count + 1)}


def to_signed_16bit(val):
    """Wandelt einen 16-Bit-Wert in signed um."""
    return val - 0x10000 if val >= 0x8000 else val


def to_signed_32bit(val):
    """Wandelt einen 32-Bit-Wert in signed um."""
    return val - 0x100000000 if val >= 0x80000000 else val


def clamp_to_int16(value: float, context: str = "value") -> int:
    """Clamp a value to int16 range (-32768 to 32767).

    Args:
        value: The value to clamp
        context: Context string for logging (e.g., "temperature", "power")

    Returns:
        int: The clamped value in int16 range
    """
    raw_value = int(value)
    if raw_value < -32768:
        _LOGGER.warning(
            "%s value %d is below int16 minimum (-32768), clamping to -32768",
            context.capitalize(), raw_value
        )
        return -32768
    elif raw_value > 32767:
        _LOGGER.warning(
            "%s value %d is above int16 maximum (32767), clamping to 32767",
            context.capitalize(), raw_value
        )
        return 32767
    else:
        return raw_value


def generate_sensor_names(
    device_prefix: str,
    sensor_name: str,
    sensor_id: str,
    name_prefix: str,
    use_legacy_modbus_names: bool
) -> dict:
    """Generate consistent sensor names, entity IDs, and unique IDs.
    
    Args:
        device_prefix: Device prefix like "hp1", "boil1", etc.
        sensor_name: Human readable sensor name like "COP Calculated"
        sensor_id: Sensor identifier like "cop_calc"
        name_prefix: Name prefix like "eu08l" (used in legacy mode)
        use_legacy_modbus_names: Whether to use legacy naming convention
        
    Returns:
        dict: Contains 'name', 'entity_id', and 'unique_id'
    """
    # Display name logic - identical to sensor.py
    # Both legacy and standard modes use the same display name format
    # The name_prefix will be added automatically by Home Assistant's device naming
    display_name = f"{device_prefix.upper()} {sensor_name}"
    
    # Entity ID logic - only this differs between modes
    if use_legacy_modbus_names:
        entity_id = f"sensor.{name_prefix}_{device_prefix}_{sensor_id}"
        unique_id = f"{name_prefix}_{device_prefix}_{sensor_id}"
    else:
        entity_id = f"sensor.{device_prefix}_{sensor_id}"
        unique_id = f"{device_prefix}_{sensor_id}"
    
    return {
        "name": display_name,
        "entity_id": entity_id,
        "unique_id": unique_id
    }


def generate_template_entity_prefix(
    device_prefix: str,
    name_prefix: str,
    use_legacy_modbus_names: bool
) -> str:
    """Generate entity prefix for templates based on naming mode.
    
    Args:
        device_prefix: Device prefix like "hp1", "boil1", etc.
        name_prefix: Name prefix like "eu08l" (used in legacy mode)
        use_legacy_modbus_names: Whether to use legacy naming convention
        
    Returns:
        str: Entity prefix for use in templates
    """
    if use_legacy_modbus_names:
        return f"{name_prefix}_{device_prefix}"
    else:
        return device_prefix
