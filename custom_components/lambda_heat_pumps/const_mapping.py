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
    0: "Off",
    1: "Standby",
    2: "Starting",
    3: "Running",
    4: "Stopping",
    5: "Error",
}

HC_OPERATING_MODE = {
    0: "Off",
    1: "Auto",
    2: "Manual",
    3: "Party",
    4: "Holiday",
    5: "Error",
}

# Buffer States
BUFF_OPERATION_STATE = {
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

SOL_OPERATION_STATE = {0: "STBY", 1: "HEATING", 2: "ERROR", 3: "OFF"}

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

