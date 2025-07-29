# scpi_commands.py
# Support file providing SCPI command mappings for device driver methods.
# Designed for use by OpenAI Codex for code completion and reference.

# PowerSupplyController SCPI mappings
POWER_SUPPLY_COMMANDS = {
    "checkDeviceConnection": "*IDN?",
    "setVoltage": "SOUR:VOLT {volts}",
    "setVoltageLimMax": "SOUR:VOLT:LIMIT:HIGH {volts}",
    "setVoltageLimMin": "SOUR:VOLT:LIMIT:LOW {volts}",
    "setVoltageProt": "SOUR:VOLT:PROT:HIGH {volts}",
    "setVoltageSlew": "SOUR:VOLT:SLEW {volts}",
    "setCurrent": "SOUR:CURR {amps}",
    "setCurrentLimMax": "SOUR:CURR:LIMIT:HIGH {amps}",
    "setCurrentLimMin": "SOUR:CURR:LIMIT:LOW {amps}",
    "setCurrentProt": "SOUR:CURR:PROT:HIGH {amps}",
    "setCurrentSlew": "SOUR:CURR:SLEW {amps}",
    "setPowerProt": "SOUR:POW:PROT:HIGH {watts}",
    "getVoltage": "FETCH:VOLT?",
    "getCurrent": "FETCH:CURR?",
    "getPower": "FETCH:POW?",
    "startOutput": "CONF:OUTP ON",
    "stopOutput": "CONF:OUTP OFF",
    "chargeCC": [
        "CONF:OUTP OFF",
        "SOUR:VOLT MAX",
        "SOUR:CURR {amps}",
        "CONF:OUTP ON"
    ],
    "chargeCV": [
        "CONF:OUTP OFF",
        "SOUR:VOLT {volts}",
        "CONF:OUTP ON"
    ],
    "chargeCP": [
        "CONF:OUTP OFF",
        "PROG:CP:POW {watts}",
        "CONF:OUTP ON"
    ],
}

# ElectronicLoadController SCPI mappings
ELECTRONIC_LOAD_COMMANDS = {
    "__init__": [
        "CHAN 1",
        "CHAN:ACT 1"
    ],
    "startDischarge": "LOAD ON",
    "stopDischarge": "LOAD OFF",
    "setCCLmode": "MODE CCL",
    "setCCMmode": "MODE CCM",
    "setCCHmode": "MODE CCH",
    "setCCcurrentL1": "CURR:STAT:L1 {amps}",
    "setCCcurrentL1MAX": "CURR:STAT:L1 MAX {amps}",
    "getCCcurrentL1MAX": "CURR:STAT:L1? MAX",
    "getVoltage": "FETCH:VOLT?",
    "getCurrent": "FETCH:CURR?",
    "getPower": "FETCH:POW?",
    "checkDeviceConnection": "*IDN?",
    "setMaxCurrent": "VOLT:STAT:ILIM {amps}",
    "dischargeCV": [
        "LOAD:STAT:OFF",
        "MODE CVH",
        "VOLT:STAT:L1 {volts}",
        "LOAD:STAT ON"
    ],
    "dischargeCC": [
        "LOAD:STAT:OFF",
        "MODE CCL",
        "CURR:STAT:L1 {amps}",
        "LOAD:STAT ON"
    ],
    "dischargeCP": [
        "LOAD:STAT:OFF",
        "MODE CPH",
        "POW:STAT:L1 {watts}",
        "LOAD:STAT ON"
    ],
}

# MultimeterController SCPI mappings
MULTIMETER_COMMANDS = {
    "checkDeviceConnection": "*IDN?",
    "configure_thermocouple": [
        'SENSe:FUNCtion "TCOUple"',
        'SENSe:TCOUple:TYPE {type}',
        'SENSe:TCOUple:RANGe DEF, DEF',
    ],
    "getTemperature": "MEASure:TCOUple?",
    "getVolts": "MEAS:VOLT:DC?",
    "getResistance": "MEAS:RES?",
}

# Instrument resource strings
INSTRUMENT_RESOURCES = {
    "power_supply": "USB0::0x1698::0x0837::011000000136::INSTR",
    "electronic_load": "USB0::0x0A69::0x083E::000000000001::INSTR",
    "multimeter": "USB0::0x1698::0x083F::TW00014586::INSTR",
}

# End of scpi_commands.py
