# Lambda Heat Pumps Integration for Home Assistant

The Lambda Heat Pumps integration is a custom component for Home Assistant that establishes a connection to Lambda heat pumps via the Modbus TCP/RTU protocol. This documentation describes the structure and functionality of the integration.

## Table of Contents

1. [Integration Structure](#integration-structure)
2. [Sensor Types](#sensor-types)
3. [Sensor Initialization](#sensor-initialization)
4. [Sensor Data Retrieval](#sensor-data-retrieval)
5. [Configuration](#configuration)
6. [Function Overview](#function-overview)
7. [Modbus Register Services](#modbus-register-services)
8. [Dynamic Entity Creation](#dynamic-entity-creation)
9. [Template-based Climate Entities](#template-based-climate-entities)

## Integration Structure

The integration consists of the following main components:

- **__init__.py**: Main entry point of the integration, registers the component with Home Assistant
- **config_flow.py**: User interface for configuring the integration
- **const.py**: Constants and configuration values, including sensor types and register addresses
- **coordinator.py**: Data coordinator that manages data exchange with the heat pump
- **sensor.py**: Implementation of sensors for various heat pump parameters
- **climate.py**: Implementation of climate entities for heating and hot water
- **services.py**: Service functions, e.g., for room temperature retrieval
- **utils.py**: Helper functions for the entire integration

The integration supports various devices:
- Up to 3 Heat Pumps
- Up to 5 Boilers
- Up to 12 Heating Circuits
- Up to 5 Buffers
- Up to 2 Solar systems

## Sensor Types

The integration supports various sensor types defined in `const.py`:

### General Sensors (SENSOR_TYPES)
- Ambient temperature
- Error numbers
- Operating states
- E-Manager values (power consumption, setpoints)

### Heat Pump Sensors (HP_SENSOR_TEMPLATES)
- Flow and return line temperatures
- Volume flow
- Energy source temperatures
- Compressor power
- COP (Coefficient of Performance)
- Power consumption
- Energy consumption

### Boiler Sensors (BOIL_SENSOR_TEMPLATES)
- Temperatures (high/low)
- Operating states
- Circulation

### Heating Circuit Sensors (HC_SENSOR_TEMPLATES)
- Flow and return line temperatures
- Room temperatures
- Operating modes
- Setpoints

### Buffer Sensors (BUFFER_SENSOR_TEMPLATES)
- Temperatures (high/low)
- Operating states
- Request types

### Solar Sensors (SOLAR_SENSOR_TEMPLATES)
- Collector temperatures
- Storage temperatures
- Power and energy yield

## Sensor Initialization

Sensors are initialized at integration startup in `sensor.py`:

1. The data coordinator is loaded
2. The configured firmware version is determined
3. Sensors are filtered based on their compatibility with the firmware
4. For each sensor category, corresponding objects are created and registered
5. Each sensor receives a unique ID and is connected to the data coordinator

Example from `sensor.py`:
```python
entities = []
name_prefix = entry.data.get("name", "lambda_wp").lower().replace(" ", "")
prefix = f"{name_prefix}_"

compatible_static_sensors = get_compatible_sensors(SENSOR_TYPES, fw_version)
for sensor_id, sensor_config in compatible_static_sensors.items():
    # Check for disabled registers
    if coordinator.is_register_disabled(sensor_config["address"]):
        continue
    
    # Create and add entities
    entities.append(
        LambdaSensor(
            coordinator=coordinator,
            config_entry=entry,
            sensor_id=sensor_id,
            sensor_config=sensor_config_with_name,
            unique_id=f"{entry.entry_id}_{sensor_id}",
        )
    )
```

## Sensor Data Retrieval

Data retrieval is handled by the `LambdaDataUpdateCoordinator` in `coordinator.py`:

1. A Modbus TCP/RTU connection is established to the heat pump
2. Registers are queried according to the configuration
3. The data is processed and converted to a structured format
4. Sensors are updated with the new data

Retrieval occurs regularly at the configured interval (default: 30 seconds).

```python
async def _async_update_data(self):
    """Fetch data from Lambda device."""
    from pymodbus.client import ModbusTcpClient
    
    # Establish connection
    if not self.client:
        self.client = ModbusTcpClient(self.host, port=self.port)
        if not await self.hass.async_add_executor_job(self.client.connect):
            raise ConnectionError("Could not connect to Modbus TCP")
    
    # Retrieve data (Static sensors, HP, Boiler, HC, etc.)
    try:
        data = {}
        # 1. Query static sensors
        for sensor_id, sensor_config in compatible_static_sensors.items():
            if self.is_register_disabled(sensor_config["address"]):
                continue
                
            result = await self.hass.async_add_executor_job(
                self.client.read_holding_registers,
                sensor_config["address"],
                count,
                self.slave_id,
            )
            
            # Process and store data
            # ...
    except Exception as ex:
        _LOGGER.error("Exception during data update: %s", ex)
    
    return data
```

## Configuration

Configuration is done via the Home Assistant user interface with `config_flow.py`:

### Basic Settings
- **Name**: Name of the installation
- **Host**: IP address or hostname of the heat pump
- **Port**: Modbus TCP port (default: 502)
- **Slave ID**: Modbus slave ID (default: 1)
- **Firmware Version**: Firmware of the heat pump (determines available sensors)

### Device Count
- Number of heat pumps (1-3)
- Number of boilers (0-5)
- Number of heating circuits (0-12)
- Number of buffers (0-5)
- Number of solar systems (0-2)

### Temperature Settings
- Hot water temperature range (min/max)
- Heating circuit temperature range (min/max)
- Temperature step size for heating circuits

### Room Temperature Control
- Option to use external temperature sensors for heating circuits

## Function Overview

### __init__.py
- **async_setup**: Initializes the integration in Home Assistant
- **async_setup_entry**: Sets up a configured integration
- **async_unload_entry**: Unloads an integration
- **async_reload_entry**: Reloads an integration after configuration changes

### config_flow.py
- **LambdaConfigFlow**: Configuration flow for initial setup
- **LambdaOptionsFlow**: Configuration flow for options (e.g., temperature settings)
- **async_step_user**: First step of configuration
- **async_step_init**: Management of options
- **async_step_room_sensor**: Configuration of room temperature sensors

### coordinator.py
- **LambdaDataUpdateCoordinator**: Coordinates data retrieval from the heat pump
- **async_init**: Initializes the coordinator
- **_async_update_data**: Retrieves data from the heat pump
- **is_register_disabled**: Checks if a register is disabled

### sensor.py
- **async_setup_entry**: Sets up sensors based on configuration
- **LambdaSensor**: Sensor class for Lambda heat pump data

### climate.py
- **async_setup_entry**: Sets up climate entities
- **LambdaClimateBoiler**: Class for boilers as climate entities
- **LambdaClimateHC**: Class for heating circuits as climate entities

### services.py
- **async_setup_services**: Registers services for the integration
- **async_update_room_temperature**: Service for updating room temperature

### utils.py
- **get_compatible_sensors**: Filters sensors by firmware compatibility
- **build_device_info**: Creates device information for the HA device registry
- **load_disabled_registers**: Loads disabled registers from YAML file
- **is_register_disabled**: Checks if a register is disabled

## Firmware Filtering

The integration supports different firmware versions and filters available sensors accordingly:

```python
def get_compatible_sensors(sensor_templates: dict, fw_version: int) -> dict:
    """Return only sensors compatible with the given firmware version."""
    return {
        k: v
        for k, v in sensor_templates.items()
        if v.get("firmware_version", 1) <= fw_version
    }
```

Each sensor has a `firmware_version` attribute that indicates the minimum version from which the sensor is available.

## Modbus Register Services

The integration provides two Home Assistant services for advanced Modbus access:
- `lambda_heat_pumps.read_modbus_register`: Read any Modbus register from the Lambda controller.
- `lambda_heat_pumps.write_modbus_register`: Write a value to any Modbus register of the Lambda controller.

These services can be used via the Developer Tools. See the documentation for details.

## Dynamic Entity Creation

- Heating circuit climate entities are only created if a room thermostat sensor is configured for the respective circuit in the integration options.
- Boiler and other device entities are created based on the configured device count.

## Template-based Climate Entities

- All climate entities (boiler, heating circuit) are now defined by templates in `const.py`.
- This makes it easy to extend or adjust entity properties centrally.
