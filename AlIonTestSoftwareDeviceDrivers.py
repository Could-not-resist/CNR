import pyvisa

# Class for communication with the NI-VISA driver to control the power supply
class PowerSupplyController:
    # Variable to keep the resource name of the power supply
    powerSupplyName = "USB0::0x1698::0x0837::011000000136::INSTR"

    # Constructor that establishes connection to the power supply
    def __init__(self) -> None:
        self.resourceManager = pyvisa.ResourceManager()
        self.powerSupply = self.resourceManager.open_resource(self.powerSupplyName)
        

    # Function that returns the name of connected device
    def checkDeviceConnection(self):
        print(self.powerSupply.query("*IDN?"))

    # Functions that allow user to set the maximum voltage, current and power for safety
    #### VOLTAGE #### VOLTAGE #### VOLTAGE #### VOLTAGE ####
    def setVoltage(self, *volts):
        self.powerSupply.write("SOUR:VOLT " + str((volts[0])))

    def setVoltageLimMax(self, *volts):
        self.powerSupply.write("SOUR:VOLT:LIMIT:HIGH " + str((volts[0])))

    def setVoltageLimMin(self, *volts):
        self.powerSupply.write("SOUR:VOLT:LIMIT:LOW " + str((volts[0])))

    def setVoltageProt(self, *volts):
        self.powerSupply.write("SOUR:VOLT:PROT:HIGH " + str((volts[0])))

    def setVoltageSlew(self, *volts):
        self.powerSupply.write("SOUR:VOLT:SLEW " + str((volts[0])))

    # def setVoltageMax(self):
    #     self.powerSupply.write("SOUR:VOLT:LIMIT:HIGH MAX")  # Could not find MAX command in manual

    #### CURRENT #### CURRENT #### CURRENT #### CURRENT ####
    def setCurrent(self, amps):
        self.powerSupply.write("SOUR:CURR " + str(amps))

    def setCurrentLimMax(self, amps):
        self.powerSupply.write("SOUR:CURR:LIMIT:HIGH " + str(amps))

    def setCurrentLimMin(self, *amps):
        self.powerSupply.write("SOUR:CURR:LIMIT:LOW " + str(amps[0]))

    def setCurrentProt(self, *amps):
        self.powerSupply.write("SOUR:CURR:PROT:HIGH " + str(amps[0]))

    def setCurrentSlew(self, amps):
        self.powerSupply.write("SOUR:CURR:SLEW " + str(amps))

    # def setCurrentMax(self):
    #     self.powerSupply.write("SOUR:CURR:LIMIT:HIGH MAX")  # Could not find MAX command in manual

    #### POWER #### POWER #### POWER #### POWER #### POWER ####
    def setPowerProt(self, *watt):
        self.powerSupply.write("SOUR:POW:PROT:HIGH " + str(watt[0]))

    # def setPowerMax(self):
    #     self.powerSupply.write("SOUR:POW:PROT:HIGH MAX")  # Could not find MAX command in manual

    #### DC RISE/FALL #### DC RISE/FALL #### DC RISE/FALL ####
    def setDC_Rise(self, *volts):
        self.powerSupply.write("SOUR:POW:PROT:HIGH " + str(volts[0]))

    def setDC_Fall(self, *volts):
        self.powerSupply.write("SOUR:POW:PROT:HIGH " + str(volts[0]))

    # Functions to read realtime VOLTAGE, CURRENT and POWER from the power supply
    def getVoltage(self):
        return self.powerSupply.query("FETCH:VOLT?")

    def getCurrent(self):
        return self.powerSupply.query("FETCH:CURR?")

    def getPower(self):
        return self.powerSupply.query("FETCH:POW?")
        

    # Function for constant CURRENT charging, taking in current in amps
    def chargeCC (self, amps : int):
        # Turn of all output
        self.powerSupply.write("CONF:OUTP OFF")
        # Set the voltage amount to max
        self.powerSupply.write("SOUR:VOLT MAX")
        # Set desired current
        self.powerSupply.write("SOUR:CURR " + str(amps))
        # Turn on output
        self.powerSupply.write("CONF:OUTP ON")

    # Function for constant VOLTAGE charging, taking in voltage in volts
    def chargeCV(self, volts : int):
        # Turn of all output
        self.powerSupply.write("CONF:OUTP OFF")
        # Set desired voltage
        self.powerSupply.write("SOUR:VOLT " + str(volts))
        # Turn on output
        self.powerSupply.write("CONF:OUTP ON")

    # Function for constant POWER charging, taking in power in watts
    def chargeCP(self, watts : int):
        # Turn of all output
        self.powerSupply.write("CONF:OUTP OFF")
        # Set desired voltage
        self.powerSupply.write("PROG:CP:POW " + str(watts))
        # Turn on output
        self.powerSupply.write("CONF:OUTP ON")


    # Functions to START/STOP the powersupply from charging
    def startOutput(self):
        self.powerSupply.write("CONF:OUTP ON")

    def stopOutput(self):
        self.powerSupply.write("CONF:OUTP OFF")

# Class for communication with the NI-VISA driver to control the electronic load
class ElectronicLoadController:
    # Variable to keep the resource name of the electronic load
    electronicLoadName = "USB0::0x0A69::0x083E::000000000001::INSTR"

    # Constructor that establishes connection to the electronic load
    def __init__(self) -> None:
        self.resourceManager = pyvisa.ResourceManager()
        self.electronicLoad = self.resourceManager.open_resource(self.electronicLoadName)

        # Set and activate the channel that will be used for testing
        self.electronicLoad.write("CHAN 1")
        self.electronicLoad.write("CHAN:ACT 1")

    # Functions to START/STOP the DC load from Discharging
    def startDischarge(self):
        self.electronicLoad.write("LOAD ON") # Activates the electronic load

    def stopDischarge(self):
        self.electronicLoad.write("LOAD OFF") # Inactivates the electronic load

    def setCCLmode(self):
        self.electronicLoad.write("MODE CCL") # Switch to CC mode Low Range

    def setCCMmode(self):
        self.electronicLoad.write("MODE CCM") # Switch to CC mode Medium Range

    def setCCHmode(self):
        self.electronicLoad.write("MODE CCH") # Switch to CC mode High Range

    def setCCcurrentL1(self, amps):
        self.electronicLoad.write("CURR:STAT:L1 " + str(amps))  # Set the desired current of Channel L1

    def setCCcurrentL1MAX(self, amps):
        self.electronicLoad.write("CURR:STAT:L1 MAX " + str(amps))  # Set the MAX current of Channel L1

    def getCCcurrentL1MAX(self):
        return  self.electronicLoad.query("CURR:STAT:L1? MAX")

    def getVoltage(self):
        return self.electronicLoad.query("FETCH:VOLT?")  # Volt reading from electronic load

    def getCurrent(self):
        return self.electronicLoad.query("FETCH:CURR?") # Current reading from electronic load

    def getPower(self):
        return self.electronicLoad.query("FETCH:POW?") # Power reading from electronic load

    def checkDeviceConnection(self):
        print(self.electronicLoad.query("*IDN?")) # Read the name of the connected device

    #### #### #### #### eftir að taka til fyrir neðan #### #### #### ####

    # Function that sets the maximum current for the electronic load
    def setMaxCurrent(self, amps):
        self.electronicLoad.write("VOLT:STAT:ILIM " + str(amps))

    def dischargeCV(self, volts):
        # Turn output off
        self.electronicLoad.write("LOAD:STAT:OFF")
        # Switch to CV mode
        self.electronicLoad.write("MODE CVH")
        # Set the constant voltage
        self.electronicLoad.write("VOLT:STAT:L1 " + str(volts))
        # Turn on output for connected channel
        self.electronicLoad.write("LOAD:STAT ON")

    def dischargeCC(self, amps):
        # Turn output off
        self.electronicLoad.write("LOAD:STAT:OFF")
        # Switch to CC mode
        self.electronicLoad.write("MODE CCL")
        # Set the desired current
        self.electronicLoad.write("CURR:STAT:L1 " + str(amps))
        # Turn on the output
        self.electronicLoad.write("LOAD:STAT ON")

    def dischargeCP(self, watts):
        # Turn output off
        self.electronicLoad.write("LOAD:STAT:OFF")
        # Switch to CP mode
        self.electronicLoad.write("MODE CPH")
        # Set the desired power
        self.electronicLoad.write("POW:STAT:L1 " + str(watts))
        # Turn output on
        self.electronicLoad.write("LOAD:STAT ON")

    # # Function to stop the electronic load from discharging the battery
    # def stopDischarge(self):
    #     self.electronicLoad.write("LOAD:STAT OFF")

# Class for communication with the NI-VISA driver to control the multimeter
class MultimeterController:
    
    # Variable to keep the resource name of the mutimeter
    multimeterName = "USB0::0x1698::0x083F::TW00014586::INSTR"

    # Constructor that establishes connection to the multimeter
    def __init__(self) -> None:
        self.resourceManager = pyvisa.ResourceManager()
        self.multimeter = self.resourceManager.open_resource(self.multimeterName)

    # Function that returns the name of the connected device
    def checkDeviceConnection(self):
        print(self.multimeter.query("*IDN?"))

    # Function that returns the temperature from the multimeter. This uses the
    # thermocouple measurement mode which must be configured with
    # ``configure_thermocouple`` beforehand.
    def getTemperature(self):
        return self.multimeter.query("MEASure:TCOUple?")

    # Function that returns the voltage from the multimeter
    def getVolts(self):
        return self.multimeter.query("MEAS:VOLT:DC?")

    # Function that returns the resistance from the multimeter
    def getResistance(self):
        return self.multimeter.query("MEAS:RES?")

    # Configure thermocouple measurement mode. The commands match the
    # manufacturer's SCPI specification. This avoids hard coding the
    # measurement function elsewhere in the code.
    def configure_thermocouple(self, tc_type: str = "K") -> None:
        self.multimeter.write('SENSe:FUNCtion "TCOUple"')
        self.multimeter.write(f'SENSe:TCOUple:TYPE {tc_type}')
        # Use default range/resolution
        self.multimeter.write('SENSe:TCOUple:RANGe DEF, DEF')

    # Read the temperature using the thermocouple input
    def getThermocoupleTemp(self):
        return self.multimeter.query('MEASure:TCOUple?')
