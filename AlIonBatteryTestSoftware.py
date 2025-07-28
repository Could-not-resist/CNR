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
        except Exception:
            # Connecting to the mock device controllers when the real devices
            # are not available.  The previous implementation exited before the
            # mock controllers were created which made running the software
            # without hardware impossible.
            print("Connection not successful, using mock objects")
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
    def NEWupsTest(
        self,
        test_name: str,
        temperature: float,
        charge_volt_prot: int,
        charge_current_prot: int,
        charge_power_prot: int,
        charge_volt_start: float,
        charge_volt_end: float,
        charge_current_max: float,
        dcharge_volt_min: float,
        dcharge_current_max: float,
        slew_volt: float,
        slew_current: float,
        leadin_time: int,
        charge_time: int,
        dcharge_time: int,
        num_cycles: int,
    ):
        TotstartTime = datetime.now()
        # Setting parameters and limits
        self.powerSupplyController.stopOutput()
        print(f"Stopping output from Power Supply")

#        self.powerSupplyController.setVoltage(charge_volt_start)
#        print(f"Set the initial voltage to {charge_volt_start}")

        print("===========================")
        print(f"Charge time {charge_time}")
        self.setVoltageLimMax((charge_volt_end-0.01))
        print(f"Set the final Charge voltage to {(charge_volt_end-0.01)}")

        self.setVoltageProt(charge_volt_prot)
        print(
            f"Set the Charging Over Voltage Protection to {charge_volt_prot}")

        self.setCurrentLimMax(charge_current_max-0.01)
        print(f"Set the max Charge Current to {charge_current_max-0.01}")

        self.setCurrentProt(charge_current_prot)
        print(f"Set the Over Current Protection to {charge_current_prot}")

        self.setVoltageSlew(slew_volt)
        print(f"Set the Charging Voltage Slew rate to {slew_volt}")

        self.setCurrentSlew(slew_current)
        print(f"Set the Charging Current Slew rate to {slew_current}")

        self.setPowerProt(charge_power_prot)
        print(f"Set the Charging Over Power Protection  {charge_power_prot}")
        print("===========================")

        print(f"Discharge time {dcharge_time}")
        print(f"Max Discharge Current {dcharge_current_max}")
        print(f"Max allowable discharge current {self.getCCcurrentL1MAX()}")
        print("===========================")

        # Charge each cycle for charge_time seconds
        Cduration = timedelta(seconds=charge_time)
        # Discharge each cycle for dcharge_time seconds
        Dduration = timedelta(seconds=dcharge_time)
        Lduration = timedelta(seconds=leadin_time)     # Leadin time in seconds
        # the amount to increase the start Volt to get to end Volt
        DeltaV = charge_volt_end-charge_volt_start

        # Charging/Discharging loop starts
        for cycleNumber in range(int(num_cycles)):
            # dataStorage object to keep track of test data
            dataStorage = DataStorage()  # one for each cycle
            Cend_time = datetime.now() + Cduration  # set the time when to stop charging
            ChargestartTime = datetime.now()

            xx = 2  # temp variable used to bypass the charging part

            if (xx > 1):

                # Charging loop
                self.startPSOutput()
                self.chargeCC(charge_current_max)
                self.setVoltage(charge_volt_start)
                print('Charging')
                while (datetime.now() < Cend_time):
                    # while Charging do the following
                    time.sleep(self.timeInterval)  # Wait between measurements
                    tmp = datetime.now()-ChargestartTime
                    # increases output voltage from charge_volt_start to charge_volt_end in leadin_time sec.
                    # if (tmp.total_seconds() < Lduration.seconds):
                    #    Lratio = tmp.total_seconds()/float(Lduration.seconds)
                    #    currentVolt=charge_volt_start+DeltaV*Lratio
                    #    if (currentVolt>charge_volt_end):
                    #        currentVolt=charge_volt_end
                    #    self.setVoltage(currentVolt)
                    #    print(currentVolt)

                    # print(tmp.total_seconds())
                    # read the voltage from Power Supply - this is the applied voltage
                    v_ps = self.getVoltagePSC()
                    # read voltage from electronic load - this is the voltage of the cell
                    v = self.getVoltageELC()
                    c = self.getCurrentPSC()  # read the current from Power Supply
                    print(f"{cycleNumber} of {num_cycles} -CHARGING- {tmp.total_seconds():03.2f} s of {Cduration.total_seconds():.1f} s - V_PS:{v_ps:.4f} V:{v:.4f} C:{c:.4f}")

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

            # if (dcharge_current_max>float(self.getCCcurrentL1MAX())):
            #    self.setCCcurrentL1MAX(dcharge_current_max)
            #    print(self.getCCcurrentL1MAX())

            # Set the desired current of channel L1&L2
            self.setCCcurrentL1(dcharge_current_max)
            self.startDischarge()  # turn on DC load

            # self.dischargeCC(dcharge_current_max)

            DischargestartTime = datetime.now()
            print('Discharging')
            while (datetime.now() < Dend_time):
                # while Discharging do the following
                time.sleep(self.timeInterval)  # Wait between measurements
                tmp = datetime.now()-DischargestartTime
                # v = self.getVoltage()  # read the voltage from multimeter 12061
                v = self.getVoltageELC()  # read voltage from electronic load
                c = self.getCurrentELC()  # read the current from electronic load
                print(f"{cycleNumber} of {num_cycles} -DISCHARGING- {tmp.total_seconds():03.2f} s of {Dduration.total_seconds():.1f} s - V:{v:.4f} C:{c:.4f}")
                dataStorage.addTime(float(tmp.total_seconds()))
                dataStorage.addVoltage(v)
                dataStorage.addCurrent(c)
                if (v < dcharge_volt_min):  # Breaking out if minimum voltage has been reached
                    print(f"below {dcharge_volt_min} volts")
                    break
            self.stopDischarge()  # Inactivate the electronic load
            # Discharging loop ends

            # Create a table from the measurements made in this cycle (27.0 is the temperature - now kept fixed)
            dataStorage.createTable(
                test_name, dcharge_current_max, cycleNumber, temperature, self.timeInterval, charge_time)

        # Set the event to indicate that testing is finished
        self.event.set()

    def efficiency_test(self, c_rate: float, num_cycles: int = 3):
        """Run a simple efficiency test.

        The battery is charged using a CC‑CV method to 4.1 V. Charging
        switches from constant current at ``c_rate`` amps to constant voltage
        at 4.1 V once the cell reaches that voltage. Charging stops when the
        current drops below ``c_rate/25``. After charging the cell is
        discharged at ``c_rate`` amps until 2.75 V.

        Charge and discharge amp‑hours and watt‑hours are logged for each
        cycle and the coulombic and energy efficiencies are calculated.  The
        results from the third cycle are printed to stdout.
        """

        results = []
        for cycle in range(1, num_cycles + 1):
            ch_Ah = ch_Wh = 0.0
            d_Ah = d_Wh = 0.0

            # --- Charge (CC‑CV) ---
            self.startPSOutput()
            self.chargeCC(c_rate)
            self.setVoltage(4.1)
            in_cv = False
            while True:
                time.sleep(self.timeInterval)
                v = self.getVoltagePSC()
                c = self.getCurrentPSC()
                ch_Ah += c * self.timeInterval / 3600.0
                ch_Wh += v * c * self.timeInterval / 3600.0
                if not in_cv and v >= 4.1:
                    self.chargeCV(4.1)
                    in_cv = True
                if in_cv and c <= c_rate / 25.0:
                    break
            self.stopPSOutput()

            # --- Discharge (1C) ---
            self.stopDischarge()
            self.setCCLmode()
            self.setCCcurrentL1(c_rate)
            self.startDischarge()
            while True:
                time.sleep(self.timeInterval)
                v = self.getVoltageELC()
                c = self.getCurrentELC()
                d_Ah += c * self.timeInterval / 3600.0
                d_Wh += v * c * self.timeInterval / 3600.0
                if v <= 2.75:
                    break
            self.stopDischarge()

            coul_eff = d_Ah / ch_Ah if ch_Ah else 0.0
            en_eff = d_Wh / ch_Wh if ch_Wh else 0.0
            cycle_res = {
                "cycle": cycle,
                "charge_Ah": ch_Ah,
                "charge_Wh": ch_Wh,
                "discharge_Ah": d_Ah,
                "discharge_Wh": d_Wh,
                "coulombic_eff": coul_eff,
                "energy_eff": en_eff,
            }
            results.append(cycle_res)
            print(
                f"Cycle {cycle} - Charged: {ch_Ah:.4f} Ah {ch_Wh:.4f} Wh, "
                f"Discharged: {d_Ah:.4f} Ah {d_Wh:.4f} Wh, "
                f"Coulombic eff.: {coul_eff:.4f}, Energy eff.: {en_eff:.4f}"
            )

        if len(results) >= 3:
            res = results[2]
            print(
                "Third cycle summary - "
                f"Charged: {res['charge_Ah']:.4f} Ah {res['charge_Wh']:.4f} Wh, "
                f"Discharged: {res['discharge_Ah']:.4f} Ah {res['discharge_Wh']:.4f} Wh, "
                f"Coulombic eff.: {res['coulombic_eff']:.4f}, "
                f"Energy eff.: {res['energy_eff']:.4f}"
            )

        return results


    def actual_capacity_test(self, current_1c: float, temperature: float = 20.0):
        """Perform an actual capacity test.

        The procedure charges the cell at 1C to 4.1 V, rests for one hour and
        then discharges at 1C down to 2.75 V while logging the cumulative
        capacity.
        """

        dataStorage = DataStorage()
        self.event.clear()

        # ----- Charge step -----
        self.startPSOutput()
        self.chargeCC(current_1c)
        self.setVoltage(4.1)

        elapsed = 0.0
        capacity = 0.0
        print("Charging to 4.1 V at 1C")
        while True:
            time.sleep(self.timeInterval)
            elapsed += self.timeInterval
            v = self.getVoltageELC()
            c = self.getCurrentPSC()
            dataStorage.addTime(elapsed)
            dataStorage.addVoltage(v)
            dataStorage.addCurrent(c)
            dataStorage.addCapacity(capacity)
            if v >= 4.1:
                break

        self.stopPSOutput()

        # ----- Rest step -----
        print("Resting for 1 hour")
        time.sleep(3600)

        # ----- Discharge step -----
        self.stopDischarge()
        self.setCCLmode()
        self.setCCcurrentL1(current_1c)
        self.startDischarge()

        print("Discharging to 2.75 V at 1C")
        while True:
            time.sleep(self.timeInterval)
            elapsed += self.timeInterval
            v = self.getVoltageELC()
            c = self.getCurrentELC()
            capacity += c * self.timeInterval / 3600.0
            dataStorage.addTime(elapsed)
            dataStorage.addVoltage(v)
            dataStorage.addCurrent(c)
            dataStorage.addCapacity(capacity)
            if v <= 2.75:
                break

        self.stopDischarge()
        dataStorage.createTable(
            "actual_capacity_test", current_1c, 0, temperature, self.timeInterval
        )

        self.event.set()



    def Capacity_Test(self, test_name: str, 
                   temperature: float, 
                   charge_volt_prot: int, 
                   charge_current_prot: int,
                   charge_power_prot: int, 
                   charge_volt_start: float, 
                   charge_volt_end: float,
                   charge_current_max: float, 
                   dcharge_volt_min: float,
                   dcharge_current_max: float, 
                   slew_volt: float, 
                   slew_current: float,
                   leadin_time: int, 
                   charge_time: int, 
                   dcharge_time: int, 
                   num_cycles: int):
        # Setting parameters and limits
        self.powerSupplyController.stopOutput()
        print(f"Stopping output from Power Supply")

        print("===========================")
        print(f"Charge time {charge_time}")
        self.setVoltageLimMax((charge_volt_end-0.01))
        print(f"Set the final Charge voltage to {(charge_volt_end-0.01)}")

        self.setVoltageProt(charge_volt_prot)
        print(
            f"Set the Charging Over Voltage Protection to {charge_volt_prot}")

        self.setCurrentLimMax(charge_current_max-0.01)
        print(f"Set the max Charge Current to {charge_current_max-0.01}")

        self.setCurrentProt(charge_current_prot)
        print(f"Set the Over Current Protection to {charge_current_prot}")

        self.setVoltageSlew(slew_volt)
        print(f"Set the Charging Voltage Slew rate to {slew_volt}")

        self.setCurrentSlew(slew_current)
        print(f"Set the Charging Current Slew rate to {slew_current}")

        self.setPowerProt(charge_power_prot)
        print(f"Set the Charging Over Power Protection  {charge_power_prot}")
        print("===========================")

        print(f"Discharge time {dcharge_time}")
        print(f"Max Discharge Current {dcharge_current_max}")
        print(f"Max allowable discharge current {self.getCCcurrentL1MAX()}")
        print("===========================")

        # Charge each cycle for charge_time seconds
        Cduration = timedelta(seconds=charge_time)
        # Discharge each cycle for dcharge_time seconds
        Dduration = timedelta(seconds=dcharge_time)
        Lduration = timedelta(seconds=leadin_time)     # Leadin time in seconds
        # the amount to increase the start Volt to get to end Volt
        DeltaV = charge_volt_end-charge_volt_start

        # Charging/Discharging loop starts
        for cycleNumber in range(int(num_cycles)):
            # dataStorage object to keep track of test data
            dataStorage = DataStorage()  # one for each cycle
            Cend_time = datetime.now() + Cduration  # set the time when to stop charging
            ChargestartTime = datetime.now()

            bypassCharging = True  # Set to True to bypass the charging part

            if bypassCharging:

                # Charging loop
                self.startPSOutput()
                self.chargeCC(charge_current_max)
                self.setVoltage(charge_volt_start)
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
                    print(f"{cycleNumber} of {num_cycles} -CHARGING- {tmp.total_seconds():03.2f} s of {Cduration.total_seconds():.1f} s - V_PS:{v_ps:.4f} V:{v:.4f} C:{c:.4f}")

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
            self.setCCcurrentL1(dcharge_current_max)
            self.startDischarge()  # turn on DC load

            # self.dischargeCC(dcharge_current_max)

            DischargestartTime = datetime.now()
            print('Discharging')
            while (datetime.now() < Dend_time):
                # while Discharging do the following
                time.sleep(self.timeInterval)  # Wait between measurements
                tmp = datetime.now()-DischargestartTime
                # v = self.getVoltage()  # read the voltage from multimeter 12061
                v = self.getVoltageELC()  # read voltage from electronic load
                c = self.getCurrentELC()  # read the current from electronic load
                print(f"{cycleNumber} of {num_cycles} -DISCHARGING- {tmp.total_seconds():03.2f} s of {Dduration.total_seconds():.1f} s - V:{v:.4f} C:{c:.4f}")
                dataStorage.addTime(float(tmp.total_seconds()))
                dataStorage.addVoltage(v)
                dataStorage.addCurrent(c)
                if (v < dcharge_volt_min):  # Breaking out if minimum voltage has been reached
                    print(f"below {dcharge_volt_min} volts")
                    break
            self.stopDischarge()  # Inactivate the electronic load
            # Discharging loop ends

            # Create a table from the measurements made in this cycle (27.0 is the temperature - now kept fixed)
            dataStorage.createTable(
                test_name, dcharge_current_max, cycleNumber, temperature, self.timeInterval, charge_time)

        # Set the event to indicate that testing is finished
        self.event.set()
