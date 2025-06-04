"""Constants for Lambda WP integration."""
from __future__ import annotations

# Integration Constants
DOMAIN = "lambda_heat_pumps"
## disable this for production
DEFAULT_NAME = "EU08L"
DEFAULT_HOST = "192.168.178.194"
##DEFAULT_PORT = 502
## enable this for production
## DEFAULT_HOST = "IP_ADDRESS or hostname"
DEFAULT_PORT = 5020
DEFAULT_SLAVE_ID = 1
DEFAULT_FIRMWARE = "V0.0.3-3K"
DEFAULT_ROOM_THERMOSTAT_CONTROL = False

# Default counts for devices
DEFAULT_NUM_HPS = 1
DEFAULT_NUM_BOIL = 1
DEFAULT_NUM_HC = 1
DEFAULT_NUM_BUFFER = 0
DEFAULT_NUM_SOLAR = 0

# Maximum counts for devices (from Modbus documentation)
MAX_NUM_HPS = 3         # Heat pumps
MAX_NUM_BOIL = 5        # Boilers
MAX_NUM_HC = 12         # Heating circuits
MAX_NUM_BUFFER = 5      # Buffers
MAX_NUM_SOLAR = 2       # Solar modules

# Default temperature settings
DEFAULT_HOT_WATER_MIN_TEMP = 40
DEFAULT_HOT_WATER_MAX_TEMP = 60

# Configuration Constants
CONF_SLAVE_ID = "slave_id"
CONF_ROOM_TEMPERATURE_ENTITY = "room_temperature_entity_{0}"
# Format string for room_temperature_entity_1, _2, etc.

# Debug and Logging
DEBUG = False
DEBUG_PREFIX = "lambda_wp"
LOG_LEVELS = {
    "error": "ERROR",
    "warning": "WARNING",
    "info": "INFO",
    "debug": "DEBUG"
}

# Firmware Versions
FIRMWARE_VERSION = {
    "V0.0.3-3K": "1",
    "V0.0.4-3K": "2",
    "V0.0.5-3K": "3",
    "V0.0.6-3K": "4",
    "V0.0.7-3K": "5",
}

#######################
# State Mappings
#######################

# Ambient States
AMBIENT_OPERATING_STATE = {0: "Off", 1: "Automatik", 2: "Manual", 3: "Error"}

# E-Manager States
EMGR_OPERATING_STATE = {
    0: "Off",
    1: "Automatik",
    2: "Manual",
    3: "Error",
    4: "Offline"
}

# Heat Pump States
HP_ERROR_STATE = {
    0: "OK",
    1: "Message",
    2: "Warning",
    3: "Alarm",
    4: "Fault"
}


HP_STATE = {
    0: "Init",
    1: "Reference",
    2: "Restart-Block",
    3: "Ready",
    4: "Start Pumps",
    5: "Start Compressor",
    6: "Pre-Regulation",
    7: "Regulation",
    8: "Not Used",
    9: "Cooling",
    10: "Defrosting",
    31: "Fault-Lock",
    32: "Alarm-Block",
    41: "Error-Reset",
}

HP_OPERATING_STATE = {
    0: "Standby",
    1: "Heizung",
    2: "WW-Bereitung",
    3: "Cold Climate",
    4: "Circulation",
    5: "Defrost",
    6: "Off",
    7: "Frost",
    8: "Standby-Frost",
    9: "Not used",
    10: "Sommer",
    11: "Ferienbetrieb",
    12: "Error",
    13: "Warning",
    14: "Info-Message",
    15: "Time-Block",
    16: "Release-Block",
    17: "Mintemp-Block",
    18: "Firmware-Download",
}

HP_REQUEST_TYPE = {
    0: "No Request",
    1: "Flow Pump Circulation",
    2: "Central Heating",
    3: "Central Cooling",
    4: "Domestic Hot Water",
}

# Boiler States
BOIL_OPERATING_STATE = {
    0: "Standby",
    1: "Domestic Hot Water",
    2: "Legio",
    3: "Summer",
    4: "Frost",
    5: "Holiday",
    6: "Prio-Stop",
    7: "Error",
    8: "Off",
    9: "Prompt-DHW",
    10: "Trailing-Stop",
    11: "Temp-Lock",
    12: "Standby-Frost",
}

# Buffer States
BUFFER_OPERATION_STATE = {
    0: "STBY",
    1: "HEATING",
    2: "COOLING",
    3: "SUMMER",
    4: "FROST",
    5: "HOLIDAY",
    6: "PRIO-STOP",
    7: "ERROR",
    8: "OFF",
    9: "STBY-FROST",
}

# Solar States
SOLAR_OPERATING_STATE = {
    0: "Off",
    1: "Active",
    2: "Standby",
    3: "Error",
    4: "Frost Protection",
    5: "Overheating Protection",
}

# Heating Circuit States
HC_OPERATING_STATE = {
    0: "Heating",
    1: "Eco",
    2: "Cooling",
    3: "Floor-dry",
    4: "Frost",
    5: "Max-Temp",
    6: "Error",
    7: "Service",
    8: "Holiday",
    9: "Central Heating Summer",
    10: "Central Cooling Winter",
    11: "Prio-Stop",
    12: "Off",
    13: "Release-Off",
    14: "Time-Off",
    15: "Standby",
    16: "Standby-Heating",
    17: "Standby-Eco",
    18: "Standby-Cooling",
    19: "Standby-Frost",
    20: "Standby-Floor-dry",
}

HC_OPERATING_MODE = {
    0: "Off",
    1: "Manual",
    2: "Automatik",
    3: "Auto-Heating",
    4: "Auto-Cooling",
    5: "Frost",
    6: "Summer",
    7: "Floor-dry",
}

#######################
# Sensor Templates
#######################

# Heat Pump Sensors
HP_SENSOR_TEMPLATES = {
    "error_state": {
        "relative_address": 0,
        "name": "Error State",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "total",
    },
    "error_number": {
        "relative_address": 1,
        "name": "Error Number",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "total",
    },
    "state": {
        "relative_address": 2,
        "name": "State",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "total",
    },
    "operating_state": {
        "relative_address": 3,
        "name": "Operating State",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "total",
    },
    "flow_line_temperature": {
        "relative_address": 4,
        "name": "Flow Line Temperature",
        "unit": "°C",
        "scale": 0.01,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
    },
    "return_line_temperature": {
        "relative_address": 5,
        "name": "Return Line Temperature",
        "unit": "°C",
        "scale": 0.01,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
    },
    "volume_flow_heat_sink": {
        "relative_address": 6,
        "name": "Volume Flow Heat Sink",
        "unit": "l/h",
        "scale": 1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "total",
    },
    "energy_source_inlet_temperature": {
        "relative_address": 7,
        "name": "Energy Source Inlet Temperature",
        "unit": "°C",
        "scale": 0.01,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
    },
    "energy_source_outlet_temperature": {
        "relative_address": 8,
        "name": "Energy Source Outlet Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
    },
    "volume_flow_energy_source": {
        "relative_address": 9,
        "name": "Volume Flow Energy Source",
        "unit": "l/min",
        "scale": 0.01,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "total",
    },
    "compressor_unit_rating": {
        "relative_address": 10,
        "name": "Compressor Unit Rating",
        "unit": "%",
        "scale": 0.01,
        "precision": 0,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "total",
    },
    "actual_heating_capacity": {
        "relative_address": 11,
        "name": "Actual Heating Capacity",
        "unit": "kW",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "total",
    },
    "inverter_power_consumption": {
        "relative_address": 12,
        "name": "Inverter Power Consumption",
        "unit": "W",
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
    },
    "cop": {
        "relative_address": 13,
        "name": "COP",
        "unit": None,
        "scale": 0.01,
        "precision": 2,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "total",
    },
    "request_type": {
        "relative_address": 15,
        "name": "Request-Type",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "total",
    },
    "requested_flow_line_temperature": {
        "relative_address": 16,
        "name": "Requested Flow Line Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
    },
    "requested_return_line_temperature": {
        "relative_address": 17,
        "name": "Requested Return Line Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
    },
    "requested_flow_to_return_line_temperature_difference": {
        "relative_address": 18,
        "name": "Requested Flow to Return Line Temperature Difference",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
    },
    "relais_state_2nd_heating_stage": {
        "relative_address": 19,
        "name": "Relais State 2nd Heating Stage",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "total",
    },
    "compressor_power_consumption_accumulated": {
        "relative_address": 20,
        "name": "Compressor Power Consumption Accumulated",
        "unit": "Wh",
        "scale": 1,
        "precision": 0,
        "data_type": "int32",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "total_increasing",
    },
    "compressor_thermal_energy_output_accumulated": {
        "relative_address": 22,
        "name": "Compressor Thermal Energy Output Accumulated",
        "unit": "Wh",
        "scale": 1,
        "precision": 0,
        "data_type": "int32",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "total_increasing",
    },
}

# Boiler Sensors
BOIL_SENSOR_TEMPLATES = {
    "error_number": {
        "relative_address": 0,
        "name": "Error Number",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "boil",
        "writeable": False,
        "state_class": "total",
    },
    "operating_state": {
        "relative_address": 1,
        "name": "Operating State",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "boil",
        "writeable": False,
        "state_class": "total",
    },
    "actual_high_temperature": {
        "relative_address": 2,
        "name": "Actual High Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "boil",
        "writeable": False,
        "state_class": "measurement",
    },
    "actual_low_temperature": {
        "relative_address": 3,
        "name": "Actual Low Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "boil",
        "writeable": False,
        "state_class": "measurement",
    },
    "target_high_temperature": {
        "relative_address": 50,
        "name": "Target High Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "boil",
        "writeable": True,
        "state_class": "measurement",
    },
    "actual_circulation_temp": {
        "relative_address": 4,
        "name": "Actual Circulation Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "boil",
        "writeable": False,
        "state_class": "measurement",
    },
    "actual_circulation_pump_state": {
        "relative_address": 5,
        "name": "Circulation Pump State",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "boil",
        "writeable": False,
        "state_class": "total",
    },
    "maximum_boiler_temp": {
        "relative_address": 50,
        "name": "Maximum Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "boil",
        "writeable": False,
        "state_class": "measurement",
    },
    "dummy_fw2": {
        "relative_address": 99,
        "name": "Dummy Boiler FW2",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 2,
        "device_type": "boil",
        "writeable": False,
        "state_class": "total",
    },
}

# Buffer Sensors
BUFFER_SENSOR_TEMPLATES = {
    "error_number": {
        "relative_address": 0,
        "name": "Error Number",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "buff",
        "writeable": False,
    },
    "operating_state": {
        "relative_address": 1,
        "name": "Operating State",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "buff",
        "writeable": False,
    },
    "actual_high_temp": {
        "relative_address": 2,
        "name": "Actual High Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "buff",
        "writeable": False,
    },
    "actual_low_temp": {
        "relative_address": 3,
        "name": "Actual Low Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "buff",
        "writeable": False,
    },
    "modbus_buffer_temp_high": {
        "relative_address": 4,
        "name": "High Temperature (Modbus)",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "buff",
        "writeable": False,
    },
    "request_type": {
        "relative_address": 5,
        "name": "Request Type",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "buff",
        "writeable": False,
    },
    "request_flow_line_temp_setpoint": {
        "relative_address": 6,
        "name": "Flow Line Temperature Setpoint",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "buff",
        "writeable": False,
    },
    "request_return_line_temp_setpoint": {
        "relative_address": 7,
        "name": "Return Line Temperature Setpoint",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "buff",
        "writeable": False,
    },
    "request_heat_sink_temp_diff_setpoint": {
        "relative_address": 8,
        "name": "Heat Sink Temperature Difference Setpoint",
        "unit": "K",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "buff",
        "writeable": False,
    },
    "modbus_request_heating_capacity": {
        "relative_address": 9,
        "name": "Requested Heating Capacity",
        "unit": "kW",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "buff",
        "writeable": False,
    },
    "maximum_buffer_temp": {
        "relative_address": 50,
        "name": "Maximum Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "buff",
        "writeable": False,
    },
}

# Solar Sensors
SOLAR_SENSOR_TEMPLATES = {
    "error_number": {
        "relative_address": 0,
        "name": "Error Number",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "sol",
        "writeable": False,
    },
    "operating_state": {
        "relative_address": 1,
        "name": "Operating State",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "sol",
        "writeable": False,
    },
    "collector_temperature": {
        "relative_address": 2,
        "name": "Collector Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "sol",
        "writeable": False,
    },
    "storage_temperature": {
        "relative_address": 3,
        "name": "Storage Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "sol",
        "writeable": False,
    },
    "power_current": {
        "relative_address": 4,
        "name": "Power Current",
        "unit": "kW",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "sol",
        "writeable": False,
    },
    "energy_total": {
        "relative_address": 5,
        "name": "Energy Total",
        "unit": "kWh",
        "scale": 1,
        "precision": 0,
        "data_type": "int32",
        "firmware_version": 1,
        "device_type": "sol",
        "writeable": False,
    },
}

# Heating Circuit Sensors
HC_SENSOR_TEMPLATES = {
    "error_number": {
        "relative_address": 0,
        "name": "Error Number",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "heating_circuit",
        "writeable": False,
        "state_class": "total",
    },
    "operating_state": {
        "relative_address": 1,
        "name": "Operating State",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "heating_circuit",
        "writeable": False,
        "state_class": "total",
    },
    "flow_line_temperature": {
        "relative_address": 2,
        "name": "Flow Line Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "heating_circuit",
        "writeable": False,
        "state_class": "measurement",
    },
    "return_line_temperature": {
        "relative_address": 3,
        "name": "Return Line Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "heating_circuit",
        "writeable": False,
        "state_class": "measurement",
    },
    "room_device_temperature": {
        "relative_address": 4,
        "name": "Room Device Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "heating_circuit",
        "writeable": False,
        "state_class": "measurement",
    },
    "set_flow_line_temperature": {
        "relative_address": 5,
        "name": "Set Flow Line Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "heating_circuit",
        "writeable": False,
        "state_class": "measurement",
    },
    "operating_mode": {
        "relative_address": 6,
        "name": "Operating Mode",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "heating_circuit",
        "writeable": False,
        "state_class": "total",
    },
    "set_flow_line_offset_temperature": {
        "relative_address": 50,
        "name": "Set Flow Line Offset Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "heating_circuit",
        "writeable": False,
        "state_class": "measurement",
    },
    "target_room_temperature": {
        "relative_address": 51,
        "name": "Target Room Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "heating_circuit",
        "writeable": True,
        "state_class": "measurement",
    },
    "set_cooling_mode_room_temperature": {
        "relative_address": 52,
        "name": "Set Cooling Mode Room Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "heating_circuit",
        "writeable": False,
        "state_class": "measurement",
    },
    "target_temp_flow_line": {
        "relative_address": 7,
        "name": "Target Flow Line Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 3,
        "device_type": "heating_circuit",
        "writeable": False,
        "state_class": "measurement",
    },
}

# General Sensors
SENSOR_TYPES = {
    # General Ambient
    "ambient_error_number": {
        "address": 0,
        "name": "Ambient Error Number",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "main",
        "writeable": False,
        "state_class": "total",
    },
    "ambient_operating_state": {
        "address": 1,
        "name": "Ambient Operating State",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "main",
        "writeable": False,
        "state_class": "total",
    },
    "ambient_temperature": {
        "address": 2,
        "name": "Ambient Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "main",
        "writeable": False,
        "state_class": "measurement",
    },
    "ambient_temperature_1h": {
        "address": 3,
        "name": "Ambient Temperature 1h",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "main",
        "writeable": False,
        "state_class": "measurement",
    },
    "ambient_temperature_calculated": {
        "address": 4,
        "name": "Ambient Temperature Calculated",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "main",
        "writeable": False,
        "state_class": "measurement",
    },
    "emgr_error_number": {
        "address": 100,
        "name": "E-Manager Error Number",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "main",
        "writeable": False,
        "state_class": "total",
    },
    "emgr_operating_state": {
        "address": 101,
        "name": "E-Manager Operating State",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "main",
        "writeable": False,
        "state_class": "total",
    },
    "emgr_actual_power": {
        "address": 102,
        "name": "E-Manager Actual Power",
        "unit": "W",
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "main",
        "writeable": False,
        "state_class": "measurement",
    },
    "emgr_actual_power_consumption": {
        "address": 103,
        "name": "E-Manager Power Consumption",
        "unit": "W",
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "main",
        "writeable": False,
        "state_class": "measurement",
    },
    "emgr_power_consumption_setpoint": {
        "address": 104,
        "name": "E-Manager Power Consumption Setpoint",
        "unit": "W",
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "main",
        "writeable": False,
        "state_class": "measurement",
    },
    "dummy_general_fw2": {
        "address": 999,
        "name": "Dummy General FW2",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "int16",
        "firmware_version": 2,
        "device_type": "main",
        "writeable": False,
        "state_class": "total",
    },
}

# Climate Sensors
CLIMATE_TEMPLATES = {
    "hot_water": {
        "relative_address": 2,
        "relative_set_address": 50,
        "name": "HOT Water",
        "unit": "°C",
        "scale": 0.1,
        "precision": 0.5,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "boil",
        "writeable": True,
        "hvac_mode": "heat", 
        "state_class": "measurement",
    },
    "heating_circuit": {
        "relative_address": 4,
        "relative_set_address": 51,
        "name": "Heating Circuit",
        "unit": "°C",
        "scale": 0.1,
        "precision": 0.1,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "hc",
        "writeable": True,
        "hvac_mode": "heat", 
        "state_class": "measurement",
    },
}



# Room Temperature Settings
# Register offset for room temperature within a HC
ROOM_TEMPERATURE_UPDATE_INTERVAL = (
    1  # Update interval for room temperature (in minutes)
)

DEFAULT_HEATING_CIRCUIT_MIN_TEMP = 15
DEFAULT_HEATING_CIRCUIT_MAX_TEMP = 35
DEFAULT_HEATING_CIRCUIT_TEMP_STEP = 0.5

CIRCULATION_PUMP_STATE = {0: "OFF", 1: "ON"}

SOLAR_OPERATION_STATE = {0: "STBY", 1: "HEATING", 2: "ERROR", 3: "OFF"}

BUFFER_REQUEST_TYPE = {
    -1: "INVALID REQUEST",
    0: "NO REQUEST",
    1: "FLOW PUMP CIRCULATION",
    2: "CENTRAL HEATING",
    3: "CENTRAL COOLING",
}

# Patterns zur Erkennung von Status-/Mode-Sensoren
STATE_SENSOR_PATTERNS = [
    "_operating_state",
    "_error_state",
    "_operating_mode",
    "ambient_state",
    "hp_state",
    "request_type",
    "_state",
    "_mode",
    "mode",
    "state",
]

#######################
# Base Addresses
#######################
# Base addresses for all device types (HP, Boil, Buffer, Solar, HC) are now generated dynamically
# using the generate_base_addresses(device_type, count) function in utils.py.

BASE_ADDRESSES = {
        'hp': 1000,    # Heat pumps start at 1000
        'boil': 2000,  # Boilers start at 2000
        'buff': 3000,  # Buffers start at 3000
        'sol': 4000,   # Solar starts at 4000
        'hc': 5000     # Heating circuits start at 5000
}
  