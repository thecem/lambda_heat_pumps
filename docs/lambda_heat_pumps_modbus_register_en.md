# Lambda Heat Pumps - Modbus Register Description

This documentation describes the Modbus registers and addresses used by the Lambda Heat Pumps integration, based on the Modbus protocol.

## Register Structure

The Modbus register address is structured as follows:
```
X _ _ _ ->  First digit:    Index (defined by module type)
_ X _ _ ->  Second digit:   Subindex (defined by module number)
_ _ X X ->  Last 2 digits:  Number (defined by data point)
```

### Index (Module)
- General = 0
- Heatpump = 1
- Boiler = 2
- Buffer = 3
- Solar = 4
- Heating circuit = 5

### Subindex (Device Number)
- The module number results from the order of modules in the configuration module
- Modules with lower numbers have a lower subindex

### Example
Register to read the flow line temperature of heat pump 2:
```
1    1    04
│    │    │
Index Subindex Number
```
= 1104 (Modbus address)

## Module: General Ambient (Index 0, Subindex 0)

| Number | Name | R/W | Data Type | Unit | Description |
|--------|------|-----|-----------|------|-------------|
| 00 | Error number | RO | INT16 | [No] | 0 = No error |
| 01 | Operating state | RO | UINT16 | [No] | 0 = OFF, 1 = AUTOMATIC, 2 = MANUAL, 3 = ERROR |
| 02 | Actual ambient temp. | RW | INT16 | [0.1°C] | Current ambient temperature (min = -50.0°C; max = 80.0°C) |
| 03 | Average ambient temp. 1h | RO | INT16 | [0.1°C] | Average temperature of the last 60 minutes |
| 04 | Calculated ambient temp. | RO | INT16 | [0.1°C] | Calculated temperature for heat distribution modules |

## Module: General E-Manager (Index 0, Subindex 1)

| Number | Name | R/W | Data Type | Unit | Description |
|--------|------|-----|-----------|------|-------------|
| 00 | Error number | RO | INT16 | [No] | 0 = No error |
| 01 | Operating state | RO | UINT16 | [No] | 0 = OFF, 1 = AUTOMATIC, 2 = MANUAL, 3 = ERROR, 4 = OFFLINE |
| 02 | Actual power | RW | UINT16/INT16 | [Watt] | Current input power or surplus power |
| 03 | Actual power consumption | RO | INT16 | [Watt] | Current power consumption of all heat pumps |
| 04 | Power consumption setpoint | RO | INT16 | [Watt] | Setpoint for the total power consumption of all heat pumps |

## Module: Heat Pump (Index 1, Subindex 0-2)

| Number | Name | R/W | Data Type | Unit | Description |
|--------|------|-----|-----------|------|-------------|
| 00 | Hp Error state | RO | UINT16 | [No] | 0=NONE, 1=MESSAGE, 2=WARNING, 3=ALARM, 4=FAULT |
| 01 | Hp Error number | RO | INT16 | [No] | Error number |
| 02 | Hp State | RO | UINT16 | [No] | 0=INIT, 1=REFERENCE, 2=RESTART-BLOCK, ... |
| 03 | Operating state | RO | UINT16 | [No] | 0=STBY, 1=CH, 2=DHW, 3=CC, ... |
| 04 | T-flow | RO | INT16 | [0.01°C] | Flow line temperature |
| 05 | T-return | RO | INT16 | [0.01°C] | Return line temperature |
| 06 | Vol. sink | RO | INT16 | [0.01l/min] | Volume flow heat sink |
| 07 | T-EQin | RO | INT16 | [0.01°C] | Energy source inlet temperature |
| 08 | T-EQout | RO | INT16 | [0.01°C] | Energy source outlet temperature |
| 09 | Vol. source | RO | INT16 | [0.01l/min] | Volume flow energy source |
| 10 | Compressor-Rating | RO | UINT16 | [0.01%] | Compressor power rating |
| 11 | Qp heating | RO | INT16 | [0.1kW] | Current heating power |
| 12 | FI power consumption | RO | INT16 | [Watt] | Frequency inverter power consumption |
| 13 | COP | RO | INT16 | [0.01] | Coefficient of Performance |
| 14 | Modbus request release password | RW | UINT16 | [No] | Password register for Modbus requests |
| 15 | Request type | RW | INT16 | [No] | 0=NO REQUEST, 1=CIRCULATION PUMP, 2=HEATING, ... |
| 16 | Request flow line temp | RW | INT16 | [0.1°C] | Requested flow line temperature (min=0.0°C, max=70.0°C) |
| 17 | Request return line temp | RW | INT16 | [0.1°C] | Requested return line temperature (min=0.0°C, max=65.0°C) |
| 18 | Request heat sink temp. diff | RW | INT16 | [0.1K] | Requested temperature difference (min=0.0K, max=35.0K) |
| 19 | Relais state for 2nd heating stage | RO | INT16 | 0/1 | 1 = NO-relay for 2nd heating stage is activated |
| 20-21 | Statistic VdA E since last reset | RO | INT32 | [Wh] | Electric energy consumption of the compressor since last reset |
| 22-23 | Statistic VdA Q since last reset | RO | INT32 | [Wh] | Thermal energy output of the compressor since last reset |

## Module: Boiler (Index 2, Subindex 0-4)

| Number | Name | R/W | Data Type | Unit | Description |
|--------|------|-----|-----------|------|-------------|
| 00 | Error number | RO | INT16 | [No] | 0 = No error |
| 01 | Operating state | RO | UINT16 | [No] | 0=STBY, 1=DHW, 2=LEGIO, 3=SUMMER, ... |
| 02 | Actual high temp. | RO | INT16 | [0.1°C] | Current temperature upper sensor |
| 03 | Actual low temp. | RO | INT16 | [0.1°C] | Current temperature lower sensor |
| 04 | Actual circulation temp. | RO | INT16 | [0.1°C] | Current temperature circulation sensor |
| 05 | Actual circulation pump state | RO | INT16 | 0/1 | Current state of circulation pump [0=OFF, 1=ON] |
| 50 | Set.: Maximum boiler temp. | RW | INT16 | [0.1°C] | Setting for maximum boiler temperature (min=25.0°C, max=65.0°C) |

## Module: Buffer (Index 3, Subindex 0-4)

| Number | Name | R/W | Data Type | Unit | Description |
|--------|------|-----|-----------|------|-------------|
| 00 | Error number | RO | INT16 | [No] | 0 = No error |
| 01 | Operating state | RO | UINT16 | [No] | 0=STBY, 1=HEATING, 2=COOLING, 3=SUMMER, ... |
| 02 | Actual high temp. | RO | INT16 | [0.1°C] | Current temperature upper sensor |
| 03 | Actual low temp. | RO | INT16 | [0.1°C] | Current temperature lower sensor |
| 04 | Modbus buffer temp. High | RW | INT16 | [0.1°C] | Buffer temperature set via Modbus (min=0°C, max=90°C) |
| 05 | Request type | RW | INT16 | [Enum] | -1=INVALID REQUEST, 0=NO REQUEST, ... |
| 06 | Request flow line temp. setpoint | RW | INT16 | [0.1°C] | Requested flow line temperature (min=0.0°C, max=65.0°C) |
| 07 | Request return line temp. Setpoint | RW | INT16 | [0.1°C] | Requested return line temperature (min=0.0°C, max=60.0°C) |
| 08 | Request heat sink temp. Diff setpoint | RW | INT16 | [0.1°K] | Requested temperature difference (min=0.0K, max=35.0K) |
| 09 | Modbus request heating capacity | RW | INT16 | [0.1kW] | Requested power (min=0.0kW, max=25.5kW) |
| 50 | Set.: Maximum buffer temp. | RW | INT16 | [0.1°C] | Setting for maximum buffer temperature (min=25.0°C, max=65.0°C) |

## Module: Solar (Index 4, Subindex 0-1)

| Number | Name | R/W | Data Type | Unit | Description |
|--------|------|-----|-----------|------|-------------|
| 00 | Error number | RO | INT16 | [No] | 0 = No error |
| 01 | Operating state | RO | UINT16 | [No] | 0=STBY, 1=HEATING, 2=ERROR, 3=OFF |
| 02 | Collector temp. | RO | INT16 | [0.1°C] | Current temperature collector sensor |
| 03 | Buffer 1 temp. | RO | INT16 | [0.1°C] | Current temperature buffer 1 sensor |
| 04 | Buffer 2 temp. | RO | INT16 | [0.1°C] | Current temperature buffer 2 sensor |
| 50 | Set.: Maximum buffer temp. | RW | INT16 | [0.1°C] | Setting for maximum buffer temperature (min=25.0°C, max=90.0°C) |
| 51 | Set.: Buffer changeover temp. | RW | INT16 | [0.1°C] | Setting for buffer changeover temperature (min=25.0°C, max=90.0°C) |

## Module: Heating Circuit (Index 5, Subindex 0-11)

| Number | Name | R/W | Data Type | Unit | Description |
|--------|------|-----|-----------|------|-------------|
| 00 | Error number | RO | INT16 | [No] | 0 = No error |
| 01 | Operating state | RO | UINT16 | [No] | 0=HEATING, 1=ECO, 2=COOLING, ... |
| 02 | Flow line temp. | RO | INT16 | [0.1°C] | Current temperature flow line sensor |
| 03 | Return line temp. | RO | INT16 | [0.1°C] | Current temperature return line sensor |
| 04 | Room device temp. | RW | INT16 | [0.1°C] | Current temperature room device sensor (min=-29.9°C, max=99.9°C) |
| 05 | Setpoint flow line temp. | RW | INT16 | [0.1°C] | Setpoint temperature flow line (min=15.0°C, max=65.0°C) |
| 06 | Operating mode | RW | INT16 | [No] | 0=OFF(RW), 1=MANUAL(R), 2=AUTOMATIC(RW), ... |
| 07 | Target temp. flow line | RO | INT16 | [0.1°C] | Target temperature flow line |
| 50 | Set.: Offset flow line temp. setpoint | RW | INT16 | [0.1°C] | Setting for flow line temperature setpoint offset (min=-10.0K, max=10.0K) |
| 51 | Set.: Setpoint room heating temp. | RW | INT16 | [0.1°C] | Setting for room temperature setpoint heating mode (min=15.0°C, max=40.0°C) |
| 52 | Set.: Setpoint room cooling temp. | RW | INT16 | [0.1°C] | Setting for room temperature setpoint cooling mode (min=15.0°C, max=40.0°C) |

## Communication Notes

- Communication is via Modbus TCP and/or RTU
- The time for a communication timeout is 1 minute
- Read function uses Modbus function code 0x03 (read multiple holding registers)
- Write function uses Modbus function code 0x10 (write multiple holding registers)
- Unit ID is 1 by default
- TCP communication is via port 502
- Up to 16 communication channels (16 masters) can be served

### Special Considerations for Write Access

- Data points between 00-49 that are written to must be regularly updated (timeout after 5 minutes)
- Data points above 50 can be written once and are permanently stored

## Modbus Register Services

The integration provides two Home Assistant services for direct Modbus register access:
- `lambda_heat_pumps.read_modbus_register`: Reads any Modbus register value.
- `lambda_heat_pumps.write_modbus_register`: Writes a value to any Modbus register.

These services can be used via the Developer Tools. Register addresses are calculated dynamically and must be specified according to the Modbus documentation.
