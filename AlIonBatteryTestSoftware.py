from math import floor
import string
import time
import matplotlib.pyplot as plt
import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
import threading
from AlIonTestSoftwareDeviceDrivers import PowerSupplyController, ElectronicLoadController, MultimeterController
from AlIonTestSoftwareDeviceDriversMock import PowerSupplyControllerMock, ElectronicLoadControllerMock, MultimeterControllerMock
from AlIonTestSoftwareDataManagement import DataStorage
import os
import pandas as pd


# Class used to control test procedures
class TestController:
    # Indicates the number of seconds between each measurement
    timeInterval = 0.2
    # Variable for keeping track of the open circuit voltage of a full battery
    OCVFull = 0.0
    # Variable for keeping track of the open circuit voltage of an empty battery
    OCVEmpty = 0.0
    # Variable for keeping track of the C-rate of the battery
    C_rate = 0.0

    # Initiating function
    def __init__(self) -> None:
        try:
            # Trying to connect to the real device controllers
            self.powerSupplyController = PowerSupplyController()
            print("Testcontroller succesfully connected to Power Supply")
            self.electronicLoadController = ElectronicLoadController()
            print("Testcontroller succesfully connected to Electronic Load")
            # self.multimeterController = MultimeterController()
            # print("Testcontroller succesfully connected to Multimeter")
        except:
            # Connecting to the mock device controllers
            print("Connection not successful, using mock objects")
            exit(1)  # Exit if the real devices are not connected
            self.powerSupplyController = PowerSupplyControllerMock()
            self.electronicLoadController = ElectronicLoadControllerMock()
            self.multimeterController = MultimeterControllerMock()

        # Create an event to indicate if test is running
        self.event = threading.Event()

    # Defining basic functionality of all remote devices through the device controller
    #####  62000P Power supply #####
    # Function for constant CURRENT charging, taking in current in ampers
    def chargeCC(self, ampers):
        self.powerSupplyController.chargeCC(ampers)

    # Function for constant VOLTAGE charging, taking in voltage in volts
    def chargeCV(self, volts):
        self.powerSupplyController.chargeCV(volts)

    # Function for constant POWER charging, taking in power in watts
    def chargeCP(self, watts):
        self.powerSupplyController.chargeCP(watts)

    # def startCharge(self):
    #     self.powerSupplyController.st
    # Functions to START/STOP the powersupply from charging
    def startPSOutput(self):
        self.powerSupplyController.startOutput()

    def stopPSOutput(self):
        self.powerSupplyController.stopOutput()

    # Functions that allow user to set the maximum voltage, current and power for safety
    #### VOLTAGE #### VOLTAGE #### VOLTAGE #### VOLTAGE ####
    def setVoltage(self, volts: float):
        self.powerSupplyController.setVoltage(volts)

    def setVoltageLimMax(self, volts: float):
        self.powerSupplyController.setVoltageLimMax(volts)

    def setVoltageLimMin(self, volts: float):
        self.powerSupplyController.setVoltageLimMin(volts)

    def setVoltageProt(self, volts: float):
        self.powerSupplyController.setVoltageProt(volts)

    def setVoltageSlew(self, volts: float):
        self.powerSupplyController.setVoltageSlew(volts)

    # def setMaxVoltageMax(self):
    #     self.powerSupplyController.setVoltageMax()

    #### CURRENT #### CURRENT #### CURRENT #### CURRENT ####
    def setCurrent(self, amps: float):
        self.powerSupplyController.setCurrent(amps)

    def setCurrentLimMax(self, amps: float):
        self.powerSupplyController.setCurrentLimMax(amps)

    def setCurrentLimMin(self, amps: float):
        self.powerSupplyController.setCurrentLimMin(amps)

    def setCurrentProt(self, amps: float):
        self.powerSupplyController.setCurrentProt(amps)

    def setCurrentSlew(self, amps: float):
        self.powerSupplyController.setCurrentSlew(amps)

    # def setMaxCurrentMax(self):
    #     self.powerSupplyController.setCurrentMax()

    #### POWER #### POWER #### POWER #### POWER #### POWER ####
    def setPowerProt(self, watts: float):
        self.powerSupplyController.setPowerProt(watts)

    # def setMaxPowerMax(self):
    #     self.powerSupplyController.setPowerMax()

    # DISCHARGE functions ###### DC LOAD 63600-5

    def startDischarge(self):
        self.electronicLoadController.startDischarge()  # Activates the electronic load

    def stopDischarge(self):
        self.electronicLoadController.stopDischarge()  # Inactivates the electronic load

    def setCCLmode(self):
        # Switch to CC mode Low Range (max 0.8 amper)
        self.electronicLoadController.setCCLmode()

    def setCCMmode(self):
        # Switch to CC mode Medium Range (max 8 amper)
        self.electronicLoadController.setCCMmode()

    def setCCcurrentL1(self, amper: float):
        self.electronicLoadController.setCCcurrentL1(
            amper)  # Set the desired current of Channel L1

    def setCCcurrentL1MAX(self, amper: float):
        self.electronicLoadController.setCCcurrentL1MAX(
            amper)  # Set the desired current of Channel L1

    def getCCcurrentL1MAX(self):
        # Read the maximum amp setting of Channel 1
        return self.electronicLoadController.getCCcurrentL1MAX()

    ###### ###### á eftir að taka til fyrir neðan ###### ######

    def dischargeCC(self, amper):
        self.electronicLoadController.dischargeCC(amper)

    def dischargeCV(self, volts):
        self.electronicLoadController.dischargeCV(volts)

    def dischargeCP(self, watts):
        self.electronicLoadController.dischargeCP(watts)

    def getVoltageELC(self):
        x = self.electronicLoadController.getVoltage()
        return float(x)

    def getCurrentELC(self):
        x = self.electronicLoadController.getCurrent()
        return float(x)

    def getVoltagePSC(self):
        x = self.powerSupplyController.getVoltage()
        return float(x)

    def getCurrentPSC(self):
        x = self.powerSupplyController.getCurrent()
        return float(x)

    # def stopDischarge(self):
    #     self.electronicLoadController.stopDischarge()

    # Functions to read realtime VOLTAGE, CURRENT and POWER from the power supply

    # Test protocal for testing the capacity of a battery

# This function is called from the TestTypes class to run a UPS test
    def NEWupsTest(self, Test_Name: str, 
                   Temperature: float, 
                   Charge_volt_prot: int, 
                   Charge_current_prot: int,
                   Charge_power_prot: int, 
                   Charge_Volt_start: float, 
                   Charge_volt_end: float,
                   Charge_current_max: float, 
                   DCharge_volt_min: float,
                   DCharge_current_max: float, 
                   Slew_volt: float, 
                   Slew_current: float,
                   LeadinTime: int, 
                   Charge_time: int, 
                   DCharge_time: int, 
                   numCycles: int):
        TotstartTime = datetime.now()
        # Setting parameters and limits
        self.powerSupplyController.stopOutput()
        print(f"Stopping output from Power Supply")

#        self.powerSupplyController.setVoltage(Charge_Volt_start)
#        print(f"Set the initial voltage to {Charge_Volt_start}")

        print("===========================")
        print(f"Charge time {Charge_time}")
        self.setVoltageLimMax((Charge_volt_end-0.01))
        print(f"Set the final Charge voltage to {(Charge_volt_end-0.01)}")

        self.setVoltageProt(Charge_volt_prot)
        print(
            f"Set the Charging Over Voltage Protection to {Charge_volt_prot}")

        self.setCurrentLimMax(Charge_current_max-0.01)
        print(f"Set the max Charge Current to {Charge_current_max-0.01}")

        self.setCurrentProt(Charge_current_prot)
        print(f"Set the Over Current Protection to {Charge_current_prot}")

        self.setVoltageSlew(Slew_volt)
        print(f"Set the Charging Voltage Slew rate to {Slew_volt}")

        self.setCurrentSlew(Slew_current)
        print(f"Set the Charging Current Slew rate to {Slew_current}")

        self.setPowerProt(Charge_power_prot)
        print(f"Set the Charging Over Power Protection  {Charge_power_prot}")
        print("===========================")

        print(f"Discharge time {DCharge_time}")
        print(f"Max Discharge Current {DCharge_current_max}")
        print(f"Max allowable discharge current {self.getCCcurrentL1MAX()}")
        print("===========================")

        # Charge each cycle for Charge_time seconds
        Cduration = timedelta(seconds=Charge_time)
        # Discharge each cycle for DCharge_time seconds
        Dduration = timedelta(seconds=DCharge_time)
        Lduration = timedelta(seconds=LeadinTime)     # Leadin time in seconds
        # the amount to increase the start Volt to get to end Volt
        DeltaV = Charge_volt_end-Charge_Volt_start

        # Charging/Discharging loop starts
        for cycleNumber in range(int(numCycles)):
            # dataStorage object to keep track of test data
            dataStorage = DataStorage()  # one for each cycle
            Cend_time = datetime.now() + Cduration  # set the time when to stop charging
            ChargestartTime = datetime.now()

            xx = 2  # temp variable used to bypass the charging part

            if (xx > 1):

                # Charging loop
                self.startPSOutput()
                self.chargeCC(Charge_current_max)
                self.setVoltage(Charge_Volt_start)
                print('Charging')
                while (datetime.now() < Cend_time):
                    # while Charging do the following
                    time.sleep(self.timeInterval)  # Wait between measurements
                    tmp = datetime.now()-ChargestartTime
                    # increases output voltage from Charge_Volt_start to Charge_volt_end in LeadinTime sec.
                    # if (tmp.total_seconds() < Lduration.seconds):
                    #    Lratio = tmp.total_seconds()/float(Lduration.seconds)
                    #    currentVolt=Charge_Volt_start+DeltaV*Lratio
                    #    if (currentVolt>Charge_volt_end):
                    #        currentVolt=Charge_volt_end
                    #    self.setVoltage(currentVolt)
                    #    print(currentVolt)

                    # print(tmp.total_seconds())
                    # read the voltage from Power Supply - this is the applied voltage
                    v_ps = self.getVoltagePSC()
                    # read voltage from electronic load - this is the voltage of the cell
                    v = self.getVoltageELC()
                    c = self.getCurrentPSC()  # read the current from Power Supply
                    print(f"{cycleNumber} of {numCycles} -CHARGING- {tmp.total_seconds():03.2f} s of {Cduration.total_seconds():.1f} s - V_PS:{v_ps:.4f} V:{v:.4f} C:{c:.4f}")

                    dataStorage.addTime(float(tmp.total_seconds()))
                    dataStorage.addVoltage(v)
                    dataStorage.addCurrent(c)
                self.stopPSOutput()  # stop the output from the power supply
                # Charging loop ends

                # # for finding where charging ends and discharging starts
                # dataStorage.addTime(9.9999)
                # # for finding where charging ends and discharging starts
                # dataStorage.addVoltage(9.9999)
                # # for finding where charging ends and discharging starts
                # dataStorage.addCurrent(9.9999)

            # set the time when to stop Discharging
            Dend_time = datetime.now() + Dduration
            # Discharging loop

            self.stopDischarge()
            self.setCCLmode()  # set the DC to CC low range mode

            # if (DCharge_current_max>float(self.getCCcurrentL1MAX())):
            #    self.setCCcurrentL1MAX(DCharge_current_max)
            #    print(self.getCCcurrentL1MAX())

            # Set the desired current of channel L1&L2
            self.setCCcurrentL1(DCharge_current_max)
            self.startDischarge()  # turn on DC load

            # self.dischargeCC(DCharge_current_max)

            DischargestartTime = datetime.now()
            print('Discharging')
            while (datetime.now() < Dend_time):
                # while Discharging do the following
                time.sleep(self.timeInterval)  # Wait between measurements
                tmp = datetime.now()-DischargestartTime
                # v = self.getVoltage()  # read the voltage from multimeter 12061
                v = self.getVoltageELC()  # read voltage from electronic load
                c = self.getCurrentELC()  # read the current from electronic load
                print(f"{cycleNumber} of {numCycles} -DISCHARGING- {tmp.total_seconds():03.2f} s of {Dduration.total_seconds():.1f} s - V:{v:.4f} C:{c:.4f}")
                dataStorage.addTime(float(tmp.total_seconds()))
                dataStorage.addVoltage(v)
                dataStorage.addCurrent(c)
                if (v < DCharge_volt_min):  # Breaking out if minimum voltage has been reached
                    print(f"below {DCharge_volt_min} volts")
                    break
            self.stopDischarge()  # Inactivate the electronic load
            # Discharging loop ends

            # Create a table from the measurements made in this cycle (27.0 is the temperature - now kept fixed)
            dataStorage.createTable(
                Test_Name, DCharge_current_max, cycleNumber, Temperature, self.timeInterval, Charge_time)

        # Set the event to indicate that testing is finished
        self.event.set()


    def Capacity_Test(self, Test_Name: str, 
                   Temperature: float, 
                   Charge_volt_prot: int, 
                   Charge_current_prot: int,
                   Charge_power_prot: int, 
                   Charge_Volt_start: float, 
                   Charge_volt_end: float,
                   Charge_current_max: float, 
                   DCharge_volt_min: float,
                   DCharge_current_max: float, 
                   Slew_volt: float, 
                   Slew_current: float,
                   LeadinTime: int, 
                   Charge_time: int, 
                   DCharge_time: int, 
                   numCycles: int):
        # Setting parameters and limits
        self.powerSupplyController.stopOutput()
        print(f"Stopping output from Power Supply")

        print("===========================")
        print(f"Charge time {Charge_time}")
        self.setVoltageLimMax((Charge_volt_end-0.01))
        print(f"Set the final Charge voltage to {(Charge_volt_end-0.01)}")

        self.setVoltageProt(Charge_volt_prot)
        print(
            f"Set the Charging Over Voltage Protection to {Charge_volt_prot}")

        self.setCurrentLimMax(Charge_current_max-0.01)
        print(f"Set the max Charge Current to {Charge_current_max-0.01}")

        self.setCurrentProt(Charge_current_prot)
        print(f"Set the Over Current Protection to {Charge_current_prot}")

        self.setVoltageSlew(Slew_volt)
        print(f"Set the Charging Voltage Slew rate to {Slew_volt}")

        self.setCurrentSlew(Slew_current)
        print(f"Set the Charging Current Slew rate to {Slew_current}")

        self.setPowerProt(Charge_power_prot)
        print(f"Set the Charging Over Power Protection  {Charge_power_prot}")
        print("===========================")

        print(f"Discharge time {DCharge_time}")
        print(f"Max Discharge Current {DCharge_current_max}")
        print(f"Max allowable discharge current {self.getCCcurrentL1MAX()}")
        print("===========================")

        # Charge each cycle for Charge_time seconds
        Cduration = timedelta(seconds=Charge_time)
        # Discharge each cycle for DCharge_time seconds
        Dduration = timedelta(seconds=DCharge_time)
        Lduration = timedelta(seconds=LeadinTime)     # Leadin time in seconds
        # the amount to increase the start Volt to get to end Volt
        DeltaV = Charge_volt_end-Charge_Volt_start

        # Charging/Discharging loop starts
        for cycleNumber in range(int(numCycles)):
            # dataStorage object to keep track of test data
            dataStorage = DataStorage()  # one for each cycle
            Cend_time = datetime.now() + Cduration  # set the time when to stop charging
            ChargestartTime = datetime.now()

            xx = 2  # temp variable used to bypass the charging part

            if (xx > 1):

                # Charging loop
                self.startPSOutput()
                self.chargeCC(Charge_current_max)
                self.setVoltage(Charge_Volt_start)
                print('Charging')
                while (datetime.now() < Cend_time):
                    # while Charging do the following
                    time.sleep(self.timeInterval)  # Wait between measurements
                    tmp = datetime.now()-ChargestartTime

                    # read the voltage from Power Supply - this is the applied voltage
                    v_ps = self.getVoltagePSC()
                    # read voltage from electronic load - this is the voltage of the cell
                    v = self.getVoltageELC()
                    c = self.getCurrentPSC()  # read the current from Power Supply
                    print(f"{cycleNumber} of {numCycles} -CHARGING- {tmp.total_seconds():03.2f} s of {Cduration.total_seconds():.1f} s - V_PS:{v_ps:.4f} V:{v:.4f} C:{c:.4f}")

                    dataStorage.addTime(float(tmp.total_seconds()))
                    dataStorage.addVoltage(v)
                    dataStorage.addCurrent(c)
                self.stopPSOutput()  # stop the output from the power supply
                # Charging loop ends

            # set the time when to stop Discharging
            Dend_time = datetime.now() + Dduration
            # Discharging loop

            self.stopDischarge()
            self.setCCLmode()  # set the DC to CC low range mode

            # Set the desired current of channel L1&L2
            self.setCCcurrentL1(DCharge_current_max)
            self.startDischarge()  # turn on DC load

            # self.dischargeCC(DCharge_current_max)

            DischargestartTime = datetime.now()
            print('Discharging')
            while (datetime.now() < Dend_time):
                # while Discharging do the following
                time.sleep(self.timeInterval)  # Wait between measurements
                tmp = datetime.now()-DischargestartTime
                # v = self.getVoltage()  # read the voltage from multimeter 12061
                v = self.getVoltageELC()  # read voltage from electronic load
                c = self.getCurrentELC()  # read the current from electronic load
                print(f"{cycleNumber} of {numCycles} -DISCHARGING- {tmp.total_seconds():03.2f} s of {Dduration.total_seconds():.1f} s - V:{v:.4f} C:{c:.4f}")
                dataStorage.addTime(float(tmp.total_seconds()))
                dataStorage.addVoltage(v)
                dataStorage.addCurrent(c)
                if (v < DCharge_volt_min):  # Breaking out if minimum voltage has been reached
                    print(f"below {DCharge_volt_min} volts")
                    break
            self.stopDischarge()  # Inactivate the electronic load
            # Discharging loop ends

            # Create a table from the measurements made in this cycle (27.0 is the temperature - now kept fixed)
            dataStorage.createTable(
                Test_Name, DCharge_current_max, cycleNumber, Temperature, self.timeInterval, Charge_time)

        # Set the event to indicate that testing is finished
        self.event.set()