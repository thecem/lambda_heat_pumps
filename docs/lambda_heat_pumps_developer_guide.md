# Lambda Heat Pumps - Developer Guide

This guide provides information for developers who want to understand, modify, or extend the Lambda Heat Pumps integration for Home Assistant.

## Code Structure

The integration follows the standard Home Assistant custom component structure:

```
lambda_heat_pumps/
├── __init__.py          # Integration initialization
├── climate.py           # Climate entity implementation
├── config_flow.py       # Configuration flow UI
├── const.py             # Constants and configuration
├── coordinator.py       # Data update coordinator
├── disabled_registers.yaml # List of disabled registers
├── manifest.json        # Integration manifest
├── sensor.py            # Sensor implementation
├── services.py          # Custom services
├── services.yaml        # Service definitions
├── utils.py             # Utility functions
├── translations/        # Translation files
```

## Key Classes

### Coordinator (coordinator.py)

The `LambdaDataUpdateCoordinator` is the core of the integration. It:
- Establishes and manages the Modbus connection
- Handles periodic data updates
- Processes the raw data into usable values
- Provides access to the data for all entities

Example of extending the coordinator to add a new data source:

```python
# In coordinator.py
async def _async_update_data(self):
    # Existing code...
    
    # Add new data source
    try:
        # Example: Read new device data
        new_device_data = await self._read_new_device_data()
        data.update(new_device_data)
    except Exception as ex:
        _LOGGER.error("Error reading new device data: %s", ex)
        
    # Continue with existing code...
    
async def _read_new_device_data(self):
    """Read data from a new device type."""
    result = {}
    # Implementation here
    return result
```

### Sensors (sensor.py)

Sensors are implemented using Home Assistant's entity model. The main class is `LambdaSensor` which extends `CoordinatorEntity` and `SensorEntity`.

To add a new sensor type:

1. Define the sensor template in `const.py`:

```python
NEW_SENSOR_TEMPLATES = {
    "new_sensor": {
        "relative_address": 123,
        "name": "New Sensor",
        "unit": "unit",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "new_type",
        "writeable": False,
        "state_class": "measurement",
    },
    # More sensors...
}
```

2. Add the sensor creation logic in `sensor.py` similar to existing sensors.

### Climate Entities (climate.py)

The climate platform provides control interfaces for boilers and heating circuits. They utilize the coordinator for both reading and writing data.

## Key Functions

### Firmware Filtering

```python
def get_compatible_sensors(sensor_templates: dict, fw_version: int) -> dict:
    """Return only sensors compatible with the given firmware version."""
    return {
        k: v
        for k, v in sensor_templates.items()
        if v.get("firmware_version", 1) <= fw_version
    }
```

This function filters sensors based on firmware compatibility, allowing sensors to be tied to specific firmware versions.

### Disabled Registers

```python
def is_register_disabled(address: int, disabled_registers: set[int]) -> bool:
    """Check if a register is disabled."""
    return address in disabled_registers
```

Allows problematic registers to be disabled via configuration.

## Testing

The integration includes a test suite using pytest. Run the tests with:

```bash
pytest tests/
```

To test a specific file:

```bash
pytest tests/test_sensor.py
```

## Adding New Device Types

To add support for a new type of device:

1. Define the base addresses in `const.py`:
```python
NEW_DEVICE_BASE_ADDRESS = {1: 7000, 2: 7100, 3: 7200}
```

2. Define sensor templates for the new device:
```python
NEW_DEVICE_SENSOR_TEMPLATES = {
    "error_number": {
        "relative_address": 0,
        "name": "Error Number",
        # ...other properties
    },
    # ...more sensors
}
```

3. Add the device to the coordinator's update method:
```python
# In _async_update_data
num_new_devices = self.entry.data.get("num_new_devices", 0)
new_device_templates = get_compatible_sensors(NEW_DEVICE_SENSOR_TEMPLATES, fw_version)
for new_device_idx in range(1, num_new_devices + 1):
    # Read sensors for this device
```

4. Add the device to the sensor and/or climate setup:
```python
# In sensor.py async_setup_entry
num_new_devices = entry.data.get("num_new_devices", 0)
for new_device_idx in range(1, num_new_devices + 1):
    # Create sensor entities
```

5. Update the configuration UI in `config_flow.py` to allow configuring the number of devices:
```python
vol.Required(
    "num_new_devices",
    default=int(
        user_input.get(
            "num_new_devices",
            existing_data.get(
                "num_new_devices",
                DEFAULT_NUM_NEW_DEVICES
            ),
        )
    ),
): selector.NumberSelector(
    selector.NumberSelectorConfig(
        min=0,
        max=MAX_NUM_NEW_DEVICES,
        step=1,
        mode=selector.NumberSelectorMode.BOX,
    )
)
```

## Modbus Communication

The integration uses the `pymodbus` library to communicate with the Lambda controller. The basic pattern is:

```python
# Connect to device
client = ModbusTcpClient(host, port=port)
if not client.connect():
    raise ConnectionError("Could not connect to Modbus TCP")

# Read registers
result = client.read_holding_registers(address, count, slave_id)
if result.isError():
    # Handle error
else:
    # Process data
    if data_type == "int32":
        value = (result.registers[0] << 16) | result.registers[1]
    else:
        value = result.registers[0]
    
    # Scale value
    scaled_value = value * scale_factor

# Write to registers
values = [int_value]
result = client.write_registers(address, values, slave_id)
if result.isError():
    # Handle error
```

## Common Development Tasks

### Adding a New Entity Attribute

1. Add a new key to the sensor template in `const.py`
2. Update the `LambdaSensor` class in `sensor.py` to handle the new attribute
3. Add tests for the new attribute in `tests/test_sensor.py`

### Adding a Service

1. Define the service in `services.yaml`
2. Implement the service function in `services.py`
3. Register the service in `async_setup_services`
4. Add tests for the service in `tests/test_services.py`

### Supporting New Firmware

1. Add the new firmware version to `FIRMWARE_VERSION` in `const.py`
2. Add firmware-specific sensors with the appropriate `firmware_version` value
3. Test with both the new and existing firmware versions

## Best Practices

1. **Error Handling**: Always catch and log exceptions to prevent crashes
2. **Typing**: Use Python type hints for better code quality
3. **Logging**: Use appropriate log levels (`debug`, `info`, `warning`, `error`)
4. **Configuration**: Make features configurable when possible
5. **Tests**: Write tests for new functionality
6. **Documentation**: Update docs when adding features or changing behavior
7. **Backwards Compatibility**: Maintain compatibility with existing configurations

## Contributing

When contributing to the project:

1. Create a feature branch for your changes
2. Run the test suite to ensure everything works
3. Document your changes
4. Submit a pull request with a clear description of the changes

## Debugging Tips

- Enable debug logging in Home Assistant configuration:
  ```yaml
  logger:
    default: info
    logs:
      custom_components.lambda_heat_pumps: debug
      pymodbus: debug
  ```

- Use the Home Assistant Developer Tools to inspect entity states and attributes

- For Modbus debugging, use a tool like mbpoll or modpoll to test register access directly:
  ```bash
  mbpoll -a 1 -r 1000 -c 10 -t 3 -1 192.168.1.100 502
  ```

## Modbus Register Services

The integration provides two Home Assistant services for advanced Modbus access:
- `lambda_heat_pumps.read_modbus_register`: Read any Modbus register from the Lambda controller.
- `lambda_heat_pumps.write_modbus_register`: Write a value to any Modbus register of the Lambda controller.

These services are defined in `services.py` and documented in `services.yaml`.

## Template-based Climate Entities

All climate entities (boiler, heating circuit) are now defined by templates in `const.py`. This allows for easy extension and central management of entity properties.

## Dynamic Entity Creation

Heating circuit climate entities are only created if a room thermostat sensor is configured for the respective circuit in the integration options.
