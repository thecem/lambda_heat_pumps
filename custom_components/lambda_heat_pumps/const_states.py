"""
Konstanten für Status, Mapping und Kurzbezeichnungen in der Lambda Heat Pumps Integration.
"""

# Mapping von device_type zu Kurzbezeichnung für Namens- und ID-Generierung
DEVICE_TYPE_SHORT = {
    "heat_pump": "Hp",      # Wärmepumpe
    "boiler": "Boil",       # Boiler
    "heating_circuit": "Hc",# Heizkreis
    "buffer": "Buff",       # Pufferspeicher
    "solar": "Solar",       # Solarmodul
    # Weitere Gerätetypen können hier ergänzt werden
}

#######################
# State Mappings
#######################

# Ambient States
AMBIENT_OPERATING_STATE = {
    0: "Off",
    1: "Automatik",
    2: "Manual",
    3: "Error"
}

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

BUFFER_REQUEST_TYPE = {
    -1: "INVALID REQUEST",
    0: "NO REQUEST",
    1: "FLOW PUMP CIRCULATION",
    2: "CENTRAL HEATING",
    3: "CENTRAL COOLING",
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

SOLAR_OPERATION_STATE = {
    0: "STBY",
    1: "HEATING",
    2: "ERROR",
    3: "OFF"
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

# Pump States
CIRCULATION_PUMP_STATE = {
    0: "OFF",
    1: "ON"
} 