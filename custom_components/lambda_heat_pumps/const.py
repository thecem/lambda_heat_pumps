# PV Surplus mode options
PV_SURPLUS_MODE_OPTIONS = {
    "entry": "E-Eintrag (nur positiv, UINT16)",
    "pos": "Pos. E-Überschuss (nur positiv, UINT16)",
    "neg": "Neg. E-Überschuss (positiv/negativ, INT16)",
}
DEFAULT_PV_SURPLUS_MODE = "pos"
"""Constants for Lambda WP integration."""

from __future__ import annotations

# Integration Constants
DOMAIN = "lambda_heat_pumps"
DEFAULT_NAME = "EU08L"
DEFAULT_HOST = "192.168.178.194"
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1
DEFAULT_FIRMWARE = "V0.0.8-3K"  # Updated to match current hardware
DEFAULT_ROOM_THERMOSTAT_CONTROL = False
DEFAULT_PV_SURPLUS = False

# Default counts for devices
DEFAULT_NUM_HPS = 1
DEFAULT_NUM_BOIL = 1
DEFAULT_NUM_HC = 1
DEFAULT_NUM_BUFFER = 0
DEFAULT_NUM_SOLAR = 0

# Maximum counts for devices (from Modbus documentation)
MAX_NUM_HPS = 3  # Heat pumps
MAX_NUM_BOIL = 5  # Boilers
MAX_NUM_HC = 12  # Heating circuits
MAX_NUM_BUFFER = 5  # Buffers
MAX_NUM_SOLAR = 2  # Solar modules

# Default temperature settings
DEFAULT_HOT_WATER_MIN_TEMP = 40
DEFAULT_HOT_WATER_MAX_TEMP = 60

# Configuration Constants
CONF_SLAVE_ID = "slave_id"
CONF_ROOM_TEMPERATURE_ENTITY = "room_temperature_entity_{0}"
CONF_PV_POWER_SENSOR_ENTITY = "pv_power_sensor_entity"
CONF_FIRMWARE_VERSION = "firmware_version"
CONF_HOST = "host"
CONF_NAME = "name"
CONF_PORT = "port"
# Format string for room_temperature_entity_1, _2, etc.
# Format string for pv_power_sensor_entity_1, _2, etc.

# Debug and Logging
DEBUG = False
DEBUG_PREFIX = "lambda_wp"
LOG_LEVELS = {"error": "ERROR", "warning": "WARNING", "info": "INFO", "debug": "DEBUG"}

# Firmware Versions
FIRMWARE_VERSION = {
    "V0.0.8-3K": 6,  # Current firmware - most common
    "V0.0.7-3K": 5,
    "V0.0.6-3K": 4,
    "V0.0.5-3K": 3,
    "V0.0.4-3K": 2,
    "V0.0.3-3K": 1,
}

# State Mappings
# are outsourced to const_mapping.py

# Sensor Templates

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
        "txt_mapping": True,
        "options": {"register": True},
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
        "txt_mapping": True,
        "options": {"register": True},
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
        "txt_mapping": True,
        "options": {"register": True},
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
        "txt_mapping": True,
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
    # Undocumented registers discovered on hardware - Always enabled
    "config_parameter_24": {
        "relative_address": 24,
        "name": "Unknown Parameter (R1024)",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
    },
    "vda_rating": {
        "relative_address": 25,
        "name": "VdA Rating",
        "unit": "%",
        "scale": 0.01,
        "precision": 2,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
    },
    "hot_gas_temperature": {
        "relative_address": 26,
        "name": "Hot Gas Temperature",
        "unit": "°C",
        "scale": 0.01,
        "precision": 2,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
        "device_class": "temperature",
    },
    "subcooling_temperature": {
        "relative_address": 27,
        "name": "Subcooling Temperature",
        "unit": "°C",
        "scale": 0.01,
        "precision": 2,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
        "device_class": "temperature",
    },
    "suction_gas_temperature": {
        "relative_address": 28,
        "name": "Suction Gas Temperature",
        "unit": "°C",
        "scale": 0.01,
        "precision": 2,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
        "device_class": "temperature",
    },
    "condensation_temperature": {
        "relative_address": 29,
        "name": "Condensation Temperature",
        "unit": "°C",
        "scale": 0.01,
        "precision": 2,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
        "device_class": "temperature",
    },
    "evaporation_temperature": {
        "relative_address": 30,
        "name": "Evaporation Temperature",
        "unit": "°C",
        "scale": 0.01,
        "precision": 2,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
        "device_class": "temperature",
    },
    "eqm_rating": {
        "relative_address": 31,
        "name": "EqM Rating",
        "unit": "%",
        "scale": 0.01,
        "precision": 2,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
    },
    "expansion_valve_opening_angle": {
        "relative_address": 32,
        "name": "Expansion Valve Opening Angle",
        "unit": "%",
        "scale": 0.01,
        "precision": 2,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
    },
    "config_parameter_50": {
        "relative_address": 50,
        "name": "Unknown Parameter (R1050)",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
    },
    "dhw_output_power_15c": {
        "relative_address": 51,
        "name": "DHW Output Power at 15°C",
        "unit": "kW",
        "scale": 0.1,
        "precision": 1,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
        "device_class": "power",
    },
    "heating_min_output_power_15c": {
        "relative_address": 52,
        "name": "Heating Min Output Power at 15°C",
        "unit": "kW",
        "scale": 0.1,
        "precision": 1,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
        "device_class": "power",
    },
    "heating_max_output_power_15c": {
        "relative_address": 53,
        "name": "Heating Max Output Power at 15°C",
        "unit": "kW",
        "scale": 0.1,
        "precision": 1,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
        "device_class": "power",
    },
    "heating_min_output_power_0c": {
        "relative_address": 54,
        "name": "Heating Min Output Power at 0°C",
        "unit": "kW",
        "scale": 0.1,
        "precision": 1,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
        "device_class": "power",
    },
    "heating_max_output_power_0c": {
        "relative_address": 55,
        "name": "Heating Max Output Power at 0°C",
        "unit": "kW",
        "scale": 0.1,
        "precision": 1,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
        "device_class": "power",
    },
    "heating_min_output_power_minus15c": {
        "relative_address": 56,
        "name": "Heating Min Output Power at -15°C",
        "unit": "kW",
        "scale": 0.1,
        "precision": 1,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
        "device_class": "power",
    },
    "heating_max_output_power_minus15c": {
        "relative_address": 57,
        "name": "Heating Max Output Power at -15°C",
        "unit": "kW",
        "scale": 0.1,
        "precision": 1,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
        "device_class": "power",
    },
    "cooling_min_output_power": {
        "relative_address": 58,
        "name": "Cooling Min Output Power",
        "unit": "kW",
        "scale": 0.1,
        "precision": 1,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
        "device_class": "power",
    },
    "cooling_max_output_power": {
        "relative_address": 59,
        "name": "Cooling Max Output Power",
        "unit": "kW",
        "scale": 0.1,
        "precision": 1,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
        "device_class": "power",
    },
    "config_parameter_60": {
        "relative_address": 60,
        "name": "Unknown Parameter (R1060)",
        "unit": None,
        "scale": 1,
        "precision": 0,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "Hp",
        "writeable": False,
        "state_class": "measurement",
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
        "txt_mapping": True,
        "options": {"register": True},
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
    "actual_circulation_temperature": {
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
        "txt_mapping": True,
    },
    "maximum_boiler_temperature": {
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
BUFF_SENSOR_TEMPLATES = {
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
        "txt_mapping": True,
    },
    "actual_high_temperature": {
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
    "actual_low_temperature": {
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
    "buffer_temperature_high_setpoint": {
        "relative_address": 4,
        "name": "Buffer High Temperature Setpoint",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "buff",
        "writeable": True,
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
        "txt_mapping": True,
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
SOL_SENSOR_TEMPLATES = {
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
        "txt_mapping": True,
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
        "device_type": "hc",
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
        "device_type": "hc",
        "writeable": False,
        "txt_mapping": True,
    },
    "flow_line_temperature": {
        "relative_address": 2,
        "name": "Flow Line Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "hc",
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
        "device_type": "hc",
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
        "device_type": "hc",
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
        "device_type": "hc",
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
        "device_type": "hc",
        "writeable": False,
        "txt_mapping": True,
    },
    "set_flow_line_offset_temperature": {
        "relative_address": 50,
        "name": "Set Flow Line Offset Temperature",
        "unit": "°C",
        "scale": 0.1,
        "precision": 1,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "hc",
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
        "device_type": "hc",
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
        "device_type": "hc",
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
        "device_type": "hc",
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
        "options": {"register": True},
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
        "txt_mapping": True,
        "options": {"register": True},
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
        "txt_mapping": True,
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
        "name": "Hot Water",
        "unit": "°C",
        "scale": 0.1,
        "precision": 0.5,
        "data_type": "int16",
        "firmware_version": 1,
        "device_type": "boil",
        "writeable": True,
        "hvac_mode": {"heat"},
        "state_class": "measurement",
    },
    "heating_circuit": {
        "relative_address": 4,  # room_device_temperature
        "relative_set_address": 51,  # target_room_temperature
        "name": "Heating Circuit",
        "unit": "°C",
        "scale": 0.1,
        "precision": 0.1,
        "data_type": "uint16",
        "firmware_version": 1,
        "device_type": "hc",
        "writeable": True,
        "hvac_mode": {"heat"},
        "state_class": "measurement",
    },
}

# Default update interval for Modbus communication (in seconds)
DEFAULT_UPDATE_INTERVAL = 10

# Default interval for writing room temperature and PV surplus (in seconds)
DEFAULT_WRITE_INTERVAL = 30

DEFAULT_HEATING_CIRCUIT_MIN_TEMP = 15
DEFAULT_HEATING_CIRCUIT_MAX_TEMP = 35
DEFAULT_HEATING_CIRCUIT_TEMP_STEP = 0.5

# Base addresses for all device types
BASE_ADDRESSES = {
    "hp": 1000,  # Heat pumps start at 1000
    "boil": 2000,  # Boilers start at 2000
    "buff": 3000,  # Buffers start at 3000
    "sol": 4000,  # Solar starts at 4000
    "hc": 5000,  # Heating circuits start at 5000
}

# Calculated Sensor Templates
CALCULATED_SENSOR_TEMPLATES = {
    # Beispiel für einen berechneten Sensor: COP
    "cop_calc": {
        "name": "COP Calculated",
        "unit": None,
        "precision": 2,
        "data_type": "calculated",
        "firmware_version": 1,
        "device_type": "hp",
        "writeable": False,
        "state_class": "measurement",
        "device_class": None,
        "template": (
            "{{% set thermal = states('sensor.{full_entity_prefix}_compressor_thermal_energy_output_accumulated') | float(0) %}}"
            "{{% set power = states('sensor.{full_entity_prefix}_compressor_power_consumption_accumulated') | float(1) %}}"
            "{{{{ (thermal / power) | round(2) if power > 0 else 0 }}}}"
        ),
    },
    # Statuswechsel-Sensoren (Flankenerkennung) - TOTAL
    # Diese Sensoren werden dynamisch für jede HP (und ggf. andere Geräte) erzeugt
    # und zählen, wie oft in einen bestimmten Modus gewechselt wurde (z.B. CH, DHW, CC, DEFROST)
    # Die Namensgebung und Indizierung erfolgt dynamisch je nach Konfiguration (legacy_name, HP-Index)
    # Die Logik zur Erkennung und Zählung erfolgt später im Code (z.B. im Coordinator)
    "heating_cycling_total": {
        "name": "Heating Cycling Total",
        "unit": "cycles",
        "precision": 0,
        "data_type": "calculated",
        "firmware_version": 1,
        "device_type": "hp",
        "writeable": False,
        "state_class": "total_increasing",
        "device_class": None,
        "mode_value": 1,  # CH
        "description": "Zählt, wie oft in den Modus Heizen (CH) gewechselt wurde.",
    },
    "hot_water_cycling_total": {
        "name": "Hot Water Cycling Total",
        "unit": "cycles",
        "precision": 0,
        "data_type": "calculated",
        "firmware_version": 1,
        "device_type": "hp",
        "writeable": False,
        "state_class": "total_increasing",
        "device_class": None,
        "mode_value": 2,  # DHW
        "description": "Zählt, wie oft in den Modus Warmwasser (DHW) gewechselt wurde.",
    },
    "cooling_cycling_total": {
        "name": "Cooling Cycling Total",
        "unit": "cycles",
        "precision": 0,
        "data_type": "calculated",
        "firmware_version": 1,
        "device_type": "hp",
        "writeable": False,
        "state_class": "total_increasing",
        "device_class": None,
        "mode_value": 3,  # CC
        "description": "Zählt, wie oft in den Modus Kühlen (CC) gewechselt wurde.",
    },
    "defrost_cycling_total": {
        "name": "Defrost Cycling Total",
        "unit": "cycles",
        "precision": 0,
        "data_type": "calculated",
        "firmware_version": 1,
        "device_type": "hp",
        "writeable": False,
        "state_class": "total_increasing",
        "device_class": None,
        "mode_value": 5,  # DEFROST
        "description": "Zählt, wie oft in den Modus Abtauen (DEFROST) gewechselt wurde.",
    },
    # Yesterday Cycling Sensoren (echte Entities für Daily-Berechnung)
    "heating_cycling_yesterday": {
        "name": "Heating Cycling Yesterday",
        "unit": "cycles",
        "precision": 0,
        "data_type": "calculated",
        "firmware_version": 1,
        "device_type": "hp",
        "writeable": False,
        "state_class": "total",
        "device_class": None,
        "description": "Speichert den Total-Wert von gestern für Daily-Berechnung.",
    },
    "hot_water_cycling_yesterday": {
        "name": "Hot Water Cycling Yesterday",
        "unit": "cycles",
        "precision": 0,
        "data_type": "calculated",
        "firmware_version": 1,
        "device_type": "hp",
        "writeable": False,
        "state_class": "total",
        "device_class": None,
        "description": "Speichert den Total-Wert von gestern für Daily-Berechnung.",
    },
    "cooling_cycling_yesterday": {
        "name": "Cooling Cycling Yesterday",
        "unit": "cycles",
        "precision": 0,
        "data_type": "calculated",
        "firmware_version": 1,
        "device_type": "hp",
        "writeable": False,
        "state_class": "total",
        "device_class": None,
        "description": "Speichert den Total-Wert von gestern für Daily-Berechnung.",
    },
    "defrost_cycling_yesterday": {
        "name": "Defrost Cycling Yesterday",
        "unit": "cycles",
        "precision": 0,
        "data_type": "calculated",
        "firmware_version": 1,
        "device_type": "hp",
        "writeable": False,
        "state_class": "total",
        "device_class": None,
        "description": "Speichert den Total-Wert von gestern für Daily-Berechnung.",
    },
    # Daily Cycling Sensoren - Template-basiert
    # Diese Sensoren berechnen die täglichen Cycling-Werte basierend auf den Total-Sensoren
    "heating_cycling_daily": {
        "name": "Heating Cycling Daily",
        "unit": "cycles",
        "precision": 0,
        "data_type": "calculated",
        "firmware_version": 1,
        "device_type": "hp",
        "writeable": False,
        "state_class": "total",
        "device_class": None,
        "template": (
            "{{% set total = states('sensor.{full_entity_prefix}_heating_cycling_total') | float(0) %}}"
            "{{% set yesterday = states('sensor.{full_entity_prefix}_heating_cycling_yesterday') | float(0) %}}"
            "{{{{ ((total - yesterday) | round(0)) | int }}}}"
        ),
        "description": "Tägliche Cycling-Zähler für Heizen, berechnet aus Total minus gestrigem Wert.",
    },
    "hot_water_cycling_daily": {
        "name": "Hot Water Cycling Daily",
        "unit": "cycles",
        "precision": 0,
        "data_type": "calculated",
        "firmware_version": 1,
        "device_type": "hp",
        "writeable": False,
        "state_class": "total",
        "device_class": None,
        "template": (
            "{{% set total = states('sensor.{full_entity_prefix}_hot_water_cycling_total') | float(0) %}}"
            "{{% set yesterday = states('sensor.{full_entity_prefix}_hot_water_cycling_yesterday') | float(0) %}}"
            "{{{{ ((total - yesterday) | round(0)) | int }}}}"
        ),
        "description": "Tägliche Cycling-Zähler für Warmwasser, berechnet aus Total minus gestrigem Wert.",
    },
    "cooling_cycling_daily": {
        "name": "Cooling Cycling Daily",
        "unit": "cycles",
        "precision": 0,
        "data_type": "calculated",
        "firmware_version": 1,
        "device_type": "hp",
        "writeable": False,
        "state_class": "total",
        "device_class": None,
        "template": (
            "{{% set total = states('sensor.{full_entity_prefix}_cooling_cycling_total') | float(0) %}}"
            "{{% set yesterday = states('sensor.{full_entity_prefix}_cooling_cycling_yesterday') | float(0) %}}"
            "{{{{ ((total - yesterday) | round(0)) | int }}}}"
        ),
        "description": "Tägliche Cycling-Zähler für Kühlen, berechnet aus Total minus gestrigem Wert.",
    },
    "defrost_cycling_daily": {
        "name": "Defrost Cycling Daily",
        "unit": "cycles",
        "precision": 0,
        "data_type": "calculated",
        "firmware_version": 1,
        "device_type": "hp",
        "writeable": False,
        "state_class": "total",
        "device_class": None,
        "template": (
            "{{% set total = states('sensor.{full_entity_prefix}_defrost_cycling_total') | float(0) %}}"
            "{{% set yesterday = states('sensor.{full_entity_prefix}_defrost_cycling_yesterday') | float(0) %}}"
            "{{{{ ((total - yesterday) | round(0)) | int }}}}"
        ),
        "description": "Tägliche Cycling-Zähler für Abtauen, berechnet aus Total minus gestrigem Wert.",
    },
    # Weitere Modi können nach Bedarf ergänzt werden (siehe Statusmapping unten)
}

# Statusmapping für operating_state (nur zur Referenz, nicht direkt im Template genutzt)
OPERATING_STATE_MAP = {
    0: "STBY",
    1: "CH",
    2: "DHW",
    3: "CC",
    4: "CIRCULATE",
    5: "DEFROST",
    6: "OFF",
    7: "FROST",
    8: "STBY-FROST",
    9: "Not used",
    10: "SUMMER",
    11: "HOLIDAY",
    12: "ERROR",
    13: "WARNING",
    14: "INFO-MESSAGE",
    15: "TIME-BLOCK",
    16: "RELEASE-BLOCK",
    17: "MINTEMP-BLOCK",
    18: "FIRMWARE-DOWNLOAD",
}

# Default update interval for Modbus communication (in seconds)
DEFAULT_UPDATE_INTERVAL = 10

# Default interval for writing room temperature and PV surplus (in seconds)
DEFAULT_WRITE_INTERVAL = 30

# Lambda WP Configuration Template
LAMBDA_WP_CONFIG_TEMPLATE = """# Lambda WP configuration
# This file is used by Lambda WP Integration to define the configuration of
# Lambda WP.
# The file is created during the installation of the Lambda WP Integration and
# can then be edited with the file editor or visual studio code.

# Modbus registrations that are not required can be deactivated here.
# Disabled registrations as an example:
#disabled_registers:
# - 2004 # boil1_actual_circulation_temp

# Override sensor names (only works if use_legacy_modbus_names is true)
# sensors_names_override does only functions if use_legacy_modbus_names is
# set to true!!!
#sensors_names_override:
#- id: name_of_the_sensor_to_override_example
#  override_name: new_name_of_the_sensor_example

# Cycling counter offsets for total sensors
# These offsets are added to the calculated cycling counts
# Useful when replacing heat pumps or resetting counters
# Example:
#cycling_offsets:
#  hp1:
#    heating_cycling_total: 0      # Offset for HP1 heating total cycles
#    hot_water_cycling_total: 0    # Offset for HP1 hot water total cycles
#    cooling_cycling_total: 0      # Offset for HP1 cooling total cycles
#    defrost_cycling_total: 0      # Offset for HP1 defrost total cycles
#  hp2:
#    heating_cycling_total: 1500   # Example: HP2 already had 1500 heating cycles
#    hot_water_cycling_total: 800  # Example: HP2 already had 800 hot water cycles
#    cooling_cycling_total: 200    # Example: HP2 already had 200 cooling cycles
#    defrost_cycling_total: 50     # Example: HP2 already had 50 defrost cycles

disabled_registers:
 - 100000 # this sensor does not exits, this is just an example

sensors_names_override:
- id: name_of_the_sensor_to_override_example
  override_name: new_name_of_the_sensor_example

cycling_offsets:
  hp1:
    heating_cycling_total: 0
    hot_water_cycling_total: 0
    cooling_cycling_total: 0
    defrost_cycling_total: 0
"""
