"""State mappings for Lambda WP sensors."""

# Heat Pump States
HP_ERROR_STATE = {
    0: "No Error",
    1: "Error 1",
    2: "Error 2",
    3: "Error 3",
    4: "Error 4",
    5: "Error 5",
    6: "Error 6",
    7: "Error 7",
    8: "Error 8",
    9: "Error 9",
    10: "Error 10",
}

HP_STATE = {
    0: "Off",
    1: "Standby",
    2: "Starting",
    3: "Running",
    4: "Stopping",
    5: "Error",
}

HP_RELAIS_STATE_2ND_HEATING_STAGE = {
    0: "Off",
    1: "On",
}

HP_OPERATING_STATE = {
    0: "Off",
    1: "Standby",
    2: "Starting",
    3: "Running",
    4: "Stopping",
    5: "Error",
}

HP_REQUEST_TYPE = {
    0: "No Request",
    1: "Flow Pump Circulation",
    2: "Central Heating",
    3: "Central Cooling",
    4: "Domestic Hot Water",
}

# Boiler States
BOIL_CIRCULATION_PUMP_STATE = {
    0: "Off",
    1: "On",
}

BOIL_OPERATING_STATE = {
    0: "Off",
    1: "Standby",
    2: "Starting",
    3: "Running",
    4: "Stopping",
    5: "Error",
}

# Heating Circuit States
HC_OPERATING_STATE = {
    0: "HEATING",
    1: "ECO",
    2: "COOLING",
    3: "FLOORDRY",
    4: "FROST",
    5: "MAX-TEMP",
    6: "ERROR",
    7: "SERVICE",
    8: "HOLIDAY",
    9: "CH-SUMMER",
    10: "CC-WINTER",
    11: "PRIO-STOP",
    12: "OFF",
    13: "RELEASE-OFF",
    14: "TIME-OFF",
    15: "STBY",
    16: "STBY-HEATING",
    17: "STBY-ECO",
    18: "STBY-COOLING",
    19: "STBY-FROST",
    20: "STBY-FLOORDRY",
}

HC_OPERATING_MODE = {
    0: "Off",
    1: "Manual",
    2: "Automatik",
    3: "AUTO-HEATING",
    4: "AUTO-COOLING",
    5: "FROST",
    6: "SUMMER",
    7: "FLOOR-DRY",
    65535: "Unknown",
}

# Buffer States
BUFF_OPERATING_STATE = {
    0: "Off",
    1: "Standby",
    2: "Starting",
    3: "Running",
    4: "Stopping",
    5: "Error",
}

BUFF_REQUEST_TYPE = {
    0: "None",
    1: "Heating",
    2: "Cooling",
    3: "DHW",
    4: "Error",
}

# Solar States

SOL_OPERATING_STATE = {0: "STBY", 1: "HEATING", 2: "ERROR", 3: "OFF"}

# Circulation Pump States
MAIN_CIRCULATION_PUMP_STATE = {
    0: "Off",
    1: "On",
    2: "Error",
}

# Ambient States
MAIN_AMBIENT_OPERATING_STATE = {
    0: "Off",
    1: "Standby",
    2: "Starting",
    3: "Running",
    4: "Stopping",
    5: "Error",
}

# E-Manager States
MAIN_EMGR_OPERATING_STATE = {
    0: "Off",
    1: "Standby",
    2: "Starting",
    3: "Running",
    4: "Stopping",
    5: "Error",
} 

