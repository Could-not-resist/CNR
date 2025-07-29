"""Mock implementations of the device drivers for testing without hardware."""

from random import randrange
import tkinter

# Class for communication with the NI-VISA driver to control the power supply
class PowerSupplyControllerMock:
    # Variable to keep the resource name of the power supply
    powerSupplyName = "USB0::0x1698::0x0837::011000000136::INSTR"

    Voltage_limmax = 10
    Current_limmax = 10
    Power_limmax = 10

    # Function that returns the name of connected device
    def checkDeviceConnection(self):
        print("Mock object is connected")

    #### VOLTAGE #### VOLTAGE #### VOLTAGE #### VOLTAGE ####
    # Functions that allow user to set the maximum voltage, current and power for safety
    def setVoltage(self, volts : float):
        self.current_voltage = volts

    def setVoltageLimMax(self, volts : float):
        self.Voltage_limmax = volts

    def setVoltageLimMin(self, volts : float):
        self.Voltage_limmin = volts

    def setVoltageProt(self, volts : float):
        self.Voltage_prot = volts

    def setVoltageSlew(self, volts : float):
        self.Voltage_slew = volts


    #### CURRENT #### CURRENT #### CURRENT #### CURRENT ####
    def setCurrent(self, amps : float):
        self.current_current = amps

    def setCurrentLimMax(self, amps : float):
        self.Current_limmax = amps

    def setCurrentLimMin(self, amps : float):
        self.Current_limmin = amps

    def setCurrentProt(self, amps : float):
        self.Current_prot = amps

    def setCurrentSlew(self, amps : float):
        self.Current_slew = amps

    #### POWER #### POWER #### POWER #### POWER #### POWER ####
    def setPowerProt(self, watts : float):
        self.Power_prot = watts

    def setMaxPower(self, watts : float):
        self.Power_limmax = watts

    # Functions to read realtime VOLTAGE, CURRENT and POWER from the power supply
    def getVoltage(self):
        return randrange(int(self.Voltage_limmax * 10000000)) / 100000000

    def getCurrent(self):
        return randrange(int(self.Current_limmax * 10000000)) / 100000000

    def getPower(self):
        return randrange(int(self.Power_limmax * 10000000)) / 100000000
        

    # Function for constant CURRENT charging, taking in current in ampers
    def chargeCC (self, ampers : float):
        pass

    # Function for constant VOLTAGE charging, taking in voltage in volts
    def chargeCV(self, volts : float):
        pass

    # Function for constant POWER charging, taking in power in watts
    def chargeCP(self, watts : float):
        pass

    # Function for constant POWER charging, taking in power in watts (legacy name)
    def chargePW(self, watts : float):
        pass

    # Function for constant POWER charging, taking in power in watts
    def startOutput(self):
        pass

    def stopOutput(self):
        pass

# Class for communication with the NI-VISA driver to control the electronic load
class ElectronicLoadControllerMock:
    # Variable to keep the resource name of the electronic load
    electronicLoadName = "USB0::0x0A69::0x083E::000000000001::INSTR"

    maxVoltage = 10
    maxCurrent = 10
    maxPower = 10

    # Function that returns the name of the connected device
    def checkDeviceConnection(self):
        print("Mock object is connected")

    def startDischarge(self):
        pass

    def stopDischarge(self):
        pass

    def setCCLmode(self):
        # Switch to CC mode Low Range (max 0.8 amper)
        pass

    def setCCMmode(self):
        # Switch to CC mode Medium Range (max 8 amper)
        pass

    def setCCHmode(self):
        # Switch to CC mode High Range
        pass

    def setCCcurrentL1(self, amper: float):
        # Set the desired current of Channel L1
        self.current_L1 = amper

    def setCCcurrentL1MAX(self, amper: float):
        # Set the maximum current of Channel L1
        self.max_current_L1 = amper

    def getCCcurrentL1MAX(self):
        # Read the maximum amp setting of Channel 1
        return getattr(self, 'max_current_L1', 1.0)

    def setMaxCurrent(self, amps):
        self.maxCurrent = amps

    def getVoltage(self):
        return randrange(int(self.maxVoltage * 10000000)) / 10000000

    def getVolts(self):
        return randrange(int(self.maxVoltage * 10000000)) / 10000000

    def getCurrent(self):
        return randrange(int(self.maxCurrent * 10000000)) / 10000000

    def getPower(self):
        return randrange(int(self.maxPower * 10000000)) / 10000000


    def dischargeCV(self, volts):
        pass

    def dischargeCC(self, amps):
        pass

    def dischargeCP(self, watts):
        pass

# Class for communication with the NI-VISA driver to control the multimeter
class MultimeterControllerMock:
    
    # Variable to keep the resource name of the mutimeter
    multimeterName = "USB0::0x1698::0x083F::TW00014586::INSTR"

    # Function that returns the name of the connected device
    def checkDeviceConnection(self):
        print("Mock object is connected")


    def getTemperature(self):
        return randrange(10000000) / 10000000

    def configure_thermocouple(self, tc_type: str = "K") -> None:
        # Mock method does nothing
        pass

    def getThermocoupleTemp(self):
        return randrange(10000000) / 10000000

    def getVolts(self):
        return randrange(10000000) / 10000000

    def getResistance(self):
        return randrange(10000000) / 10000000

