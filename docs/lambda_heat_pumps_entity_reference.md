# Lambda Heat Pumps - Entity Reference

This document provides a detailed reference of all entities created by the Lambda Heat Pumps integration, organized by device type.

## General Sensors

| Entity ID | Name | Description | Unit | Data Type |
|-----------|------|-------------|------|-----------|
| sensor.[name]_ambient_error_number | Ambient Error Number | Error code for ambient module | - | int16 |
| sensor.[name]_ambient_operating_state | Ambient Operating State | Operating state of ambient module | - | uint16 |
| sensor.[name]_ambient_temperature | Ambient Temperature | External ambient temperature | °C | int16 |
| sensor.[name]_ambient_temperature_1h | Ambient Temperature 1h | 1-hour average ambient temperature | °C | int16 |
| sensor.[name]_ambient_temperature_calculated | Ambient Temperature Calculated | Calculated ambient temperature for heating systems | °C | int16 |
| sensor.[name]_emgr_error_number | E-Manager Error Number | Error code for energy manager | - | int16 |
| sensor.[name]_emgr_operating_state | E-Manager Operating State | Operating state of energy manager | - | uint16 |
| sensor.[name]_emgr_actual_power | E-Manager Actual Power | Current power consumption or input | W | int16 |
| sensor.[name]_emgr_actual_power_consumption | E-Manager Power Consumption | Actual power consumption of all heat pumps | W | int16 |
| sensor.[name]_emgr_power_consumption_setpoint | E-Manager Power Consumption Setpoint | Target power consumption for all heat pumps | W | int16 |

## Heat Pump Sensors (for each heat pump X)

| Entity ID | Name | Description | Unit | Data Type |
|-----------|------|-------------|------|-----------|
| sensor.[name]_hpX_error_state | Error State | Current error state of heat pump | - | uint16 |
| sensor.[name]_hpX_error_number | Error Number | Error code number | - | int16 |
| sensor.[name]_hpX_state | State | Operating state of heat pump | - | uint16 |
| sensor.[name]_hpX_operating_state | Operating State | Functional state of heat pump | - | uint16 |
| sensor.[name]_hpX_flow_line_temperature | Flow Line Temperature | Temperature of outgoing water | °C | int16 |
| sensor.[name]_hpX_return_line_temperature | Return Line Temperature | Temperature of returning water | °C | int16 |
| sensor.[name]_hpX_volume_flow_heat_sink | Volume Flow Heat Sink | Water flow rate in the heating circuit | l/h | int16 |
| sensor.[name]_hpX_energy_source_inlet_temperature | Energy Source Inlet Temperature | Temperature of incoming energy source | °C | int16 |
| sensor.[name]_hpX_energy_source_outlet_temperature | Energy Source Outlet Temperature | Temperature of outgoing energy source | °C | int16 |
| sensor.[name]_hpX_volume_flow_energy_source | Volume Flow Energy Source | Flow rate of energy source | l/min | int16 |
| sensor.[name]_hpX_compressor_unit_rating | Compressor Unit Rating | Power rating of the compressor | % | uint16 |
| sensor.[name]_hpX_actual_heating_capacity | Actual Heating Capacity | Current heating output | kW | int16 |
| sensor.[name]_hpX_inverter_power_consumption | Inverter Power Consumption | Power used by the frequency inverter | W | int16 |
| sensor.[name]_hpX_cop | COP | Coefficient of Performance | - | int16 |
| sensor.[name]_hpX_request_type | Request-Type | Type of current operation request | - | int16 |
| sensor.[name]_hpX_requested_flow_line_temperature | Requested Flow Line Temperature | Target flow line temperature | °C | int16 |
| sensor.[name]_hpX_requested_return_line_temperature | Requested Return Line Temperature | Target return line temperature | °C | int16 |
| sensor.[name]_hpX_requested_flow_to_return_line_temperature_difference | Requested Flow to Return Line Temperature Difference | Target temperature difference | °C | int16 |
| sensor.[name]_hpX_relais_state_2nd_heating_stage | Relais State 2nd Heating Stage | Status of the second heating stage | - | int16 |
| sensor.[name]_hpX_compressor_power_consumption_accumulated | Compressor Power Consumption Accumulated | Total power consumed by compressor | Wh | int32 |
| sensor.[name]_hpX_compressor_thermal_energy_output_accumulated | Compressor Thermal Energy Output Accumulated | Total thermal energy produced | Wh | int32 |

## Boiler Sensors (for each boiler X)

| Entity ID | Name | Description | Unit | Data Type |
|-----------|------|-------------|------|-----------|
| sensor.[name]_boilX_error_number | Error Number | Error code for boiler | - | int16 |
| sensor.[name]_boilX_operating_state | Operating State | Current operating state | - | uint16 |
| sensor.[name]_boilX_actual_high_temperature | Actual High Temperature | Temperature at top of boiler | °C | int16 |
| sensor.[name]_boilX_actual_low_temperature | Actual Low Temperature | Temperature at bottom of boiler | °C | int16 |
| sensor.[name]_boilX_target_high_temperature | Target High Temperature | Target temperature for top of boiler | °C | int16 |
| sensor.[name]_boilX_actual_circulation_temp | Actual Circulation Temperature | Temperature in circulation line | °C | int16 |
| sensor.[name]_boilX_actual_circulation_pump_state | Circulation Pump State | Status of circulation pump | - | int16 |
| sensor.[name]_boilX_maximum_boiler_temp | Maximum Temperature | Maximum allowed boiler temperature | °C | int16 |

## Heating Circuit Sensors (for each heating circuit X)

| Entity ID | Name | Description | Unit | Data Type |
|-----------|------|-------------|------|-----------|
| sensor.[name]_hcX_error_number | Error Number | Error code for heating circuit | - | int16 |
| sensor.[name]_hcX_operating_state | Operating State | Current operating state | - | uint16 |
| sensor.[name]_hcX_flow_line_temperature | Flow Line Temperature | Temperature of outgoing water | °C | int16 |
| sensor.[name]_hcX_return_line_temperature | Return Line Temperature | Temperature of returning water | °C | int16 |
| sensor.[name]_hcX_room_device_temperature | Room Device Temperature | Current room temperature | °C | int16 |
| sensor.[name]_hcX_set_flow_line_temperature | Set Flow Line Temperature | Target flow line temperature | °C | int16 |
| sensor.[name]_hcX_operating_mode | Operating Mode | Current mode of operation | - | int16 |
| sensor.[name]_hcX_set_flow_line_offset_temperature | Set Flow Line Offset Temperature | Offset for flow temperature | °C | int16 |
| sensor.[name]_hcX_target_room_temperature | Target Room Temperature | Target room temperature | °C | int16 |
| sensor.[name]_hcX_set_cooling_mode_room_temperature | Set Cooling Mode Room Temperature | Target temperature for cooling | °C | int16 |
| sensor.[name]_hcX_target_temp_flow_line | Target Flow Line Temperature | Calculated target flow temperature | °C | int16 |

## Buffer Sensors (for each buffer X)

| Entity ID | Name | Description | Unit | Data Type |
|-----------|------|-------------|------|-----------|
| sensor.[name]_buffX_error_number | Error Number | Error code for buffer | - | int16 |
| sensor.[name]_buffX_operating_state | Operating State | Current operating state | - | uint16 |
| sensor.[name]_buffX_actual_high_temp | Actual High Temperature | Temperature at top of buffer | °C | int16 |
| sensor.[name]_buffX_actual_low_temp | Actual Low Temperature | Temperature at bottom of buffer | °C | int16 |
| sensor.[name]_buffX_modbus_buffer_temp_high | High Temperature (Modbus) | Target high temperature via Modbus | °C | int16 |
| sensor.[name]_buffX_request_type | Request Type | Type of current request | - | int16 |
| sensor.[name]_buffX_request_flow_line_temp_setpoint | Flow Line Temperature Setpoint | Target flow line temperature | °C | int16 |
| sensor.[name]_buffX_request_return_line_temp_setpoint | Return Line Temperature Setpoint | Target return line temperature | °C | int16 |
| sensor.[name]_buffX_request_heat_sink_temp_diff_setpoint | Heat Sink Temperature Difference Setpoint | Target temperature difference | K | int16 |
| sensor.[name]_buffX_modbus_request_heating_capacity | Requested Heating Capacity | Requested heating power | kW | int16 |
| sensor.[name]_buffX_maximum_buffer_temp | Maximum Temperature | Maximum allowed buffer temperature | °C | int16 |

## Solar Sensors (for each solar system X)

| Entity ID | Name | Description | Unit | Data Type |
|-----------|------|-------------|------|-----------|
| sensor.[name]_solX_error_number | Error Number | Error code for solar system | - | int16 |
| sensor.[name]_solX_operating_state | Operating State | Current operating state | - | uint16 |
| sensor.[name]_solX_collector_temperature | Collector Temperature | Temperature at solar collector | °C | int16 |
| sensor.[name]_solX_storage_temperature | Storage Temperature | Temperature in storage tank | °C | int16 |
| sensor.[name]_solX_power_current | Power Current | Current power output | kW | int16 |
| sensor.[name]_solX_energy_total | Energy Total | Total energy produced | kWh | int32 |

## Climate Entities

| Entity ID | Name | Description | Features |
|-----------|------|-------------|----------|
| climate.[name]_boilX | [Name] Boiler X | Hot water boiler control | Temperature setting, Operation modes |
| climate.[name]_hcX | [Name] Heating Circuit X | Heating circuit control | Temperature setting, Operation modes |

*Note: Replace [name] with your configured integration name and X with the device number (1, 2, 3, etc.).*

## State Values

### Operating States

#### Heat Pump Operating States
- 0: Standby
- 1: Heating
- 2: Hot Water
- 3: Cold Climate
- 4: Circulation
- 5: Defrost
- 6: Off
- 7: Frost
- 8: Standby-Frost
- 10: Summer
- 11: Holiday
- 12: Error
- 13: Warning
- 14: Info-Message
- And more...

#### Boiler Operating States
- 0: Standby
- 1: Domestic Hot Water
- 2: Legio
- 3: Summer
- 4: Frost
- 5: Holiday
- 6: Prio-Stop
- 7: Error
- 8: Off
- And more...

#### Heating Circuit Operating States
- 0: Heating
- 1: Eco
- 2: Cooling
- 3: Floor-dry
- 4: Frost
- 5: Max-Temp
- 6: Error
- 7: Service
- And more...

## Additional Notes

- Firmware-specific entities may not be available on all controllers
- State sensors return mapped text values rather than raw numbers
- Some entities are read-only, while others (especially climate entities) allow control
- Energy measurement entities use the "total_increasing" state class for proper energy statistics
