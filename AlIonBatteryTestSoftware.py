"""Core routines for controlling UPS battery test sequences."""

import time
from datetime import datetime
from datetime import timedelta
import threading
from AlIonTestSoftwareDeviceDrivers import PowerSupplyController, ElectronicLoadController, MultimeterController
from AlIonTestSoftwareDeviceDriversMock import PowerSupplyControllerMock, ElectronicLoadControllerMock, MultimeterControllerMock
from AlIonTestSoftwareDataManagement import DataStorage


# Class used to control test procedures
class TestController:
    """Coordinate power supply, load and measurement devices for tests."""
    # Indicates the number of seconds between each measurement
    timeInterval = 0.2
    # Variable for keeping track of the open circuit voltage of a full battery
    OCVFull = 0.0
    # Variable for keeping track of the open circuit voltage of an empty battery
    OCVEmpty = 0.0
    # Variable for keeping track of the C-rate of the battery
    C_rate = 0.0

    # Initiating function
    def __init__(self, multimeter_mode: str | None = None) -> None:
        self.multimeter_mode = multimeter_mode
        try:
            # Trying to connect to the real device controllers
            self.powerSupplyController = PowerSupplyController()
            print("Testcontroller succesfully connected to Power Supply")
            self.electronicLoadController = ElectronicLoadController()
            print("Testcontroller succesfully connected to Electronic Load")
            if multimeter_mode:
                self.multimeterController = MultimeterController()
                print("Testcontroller succesfully connected to Multimeter")
                if multimeter_mode == "tcouple":
                    self.multimeterController.configure_thermocouple()
            else:
                self.multimeterController = MultimeterControllerMock()
        except Exception:
            # Connecting to the mock device controllers when the real devices
            # are not available.  The previous implementation exited before the
            # mock controllers were created which made running the software
            # without hardware impossible.
            print("Connection not successful.")
            answer = input(
                "Devices not detected. Continue with mock drivers? [y/N]: "
            ).strip().lower()
            if answer not in ("y", "yes"):
                raise SystemExit(
                    "Aborting: no connection to hardware and user declined mock drivers"
                )
            print("Using mock objects")
            self.powerSupplyController = PowerSupplyControllerMock()
            self.electronicLoadController = ElectronicLoadControllerMock()
            self.multimeterController = MultimeterControllerMock()

        # Create an event to indicate if test is running
        self.event = threading.Event()

    # Defining basic functionality of all remote devices through the device controller
    #####  62000P Power supply #####
    # Function for constant CURRENT charging, taking in current in amps
    def chargeCC(self, amps):
        self.powerSupplyController.chargeCC(amps)

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

    def setCCHmode(self):
        # Switch to CC mode High Range
        self.electronicLoadController.setCCHmode()

    def setCCcurrentL1(self, amper: float):
        self.electronicLoadController.setCCcurrentL1(
            amper)  # Set the desired current of Channel L1

    def setCCcurrentL1MAX(self, amper: float):
        self.electronicLoadController.setCCcurrentL1MAX(
            amper)  # Set the desired current of Channel L1

    def getCCcurrentL1MAX(self):
        # Read the maximum amp setting of Channel 1
        return self.electronicLoadController.getCCcurrentL1MAX()

    # Helper methods for discharging and reading instrument values

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

    def getVoltageMM(self):
        return float(self.multimeterController.getVolts())

    def getTemperatureMM(self):
        return float(self.multimeterController.getThermocoupleTemp())

    # def stopDischarge(self):
    #     self.electronicLoadController.stopDischarge()

    # Functions to read realtime VOLTAGE, CURRENT and POWER from the power supply

    def apply_safety_limits(
        self,
        charge_volt_prot: int | None = None,
        charge_current_prot: int | None = None,
        charge_power_prot: int | None = None,
        charge_volt_end: float | None = None,
        charge_current_max: float | None = None,
        slew_volt: float | None = None,
        slew_current: float | None = None,
    ) -> None:
        """Disable outputs and configure protection limits.

        If parameters are omitted, values are loaded from ``MAIN`` or fall back
        to the defaults in ``cell_profiles.json``.
        """

        try:
            from MAIN import (
                CHARGE_VOLT_PROT,
                CHARGE_CURRENT_PROT,
                CHARGE_POWER_PROT,
                CHARGE_VOLT_END,
                CHARGE_CURRENT_MAX,
                SLEW_VOLT,
                SLEW_CURRENT,
            )
        except Exception:
            CHARGE_VOLT_PROT = 10
            CHARGE_CURRENT_PROT = 10
            CHARGE_POWER_PROT = 2000
            CHARGE_VOLT_END = 4.1
            CHARGE_CURRENT_MAX = 5.0
            SLEW_VOLT = 0.1
            SLEW_CURRENT = 0.1

        charge_volt_prot = CHARGE_VOLT_PROT if charge_volt_prot is None else charge_volt_prot
        charge_current_prot = CHARGE_CURRENT_PROT if charge_current_prot is None else charge_current_prot
        charge_power_prot = CHARGE_POWER_PROT if charge_power_prot is None else charge_power_prot
        charge_volt_end = CHARGE_VOLT_END if charge_volt_end is None else charge_volt_end
        charge_current_max = CHARGE_CURRENT_MAX if charge_current_max is None else charge_current_max
        slew_volt = SLEW_VOLT if slew_volt is None else slew_volt
        slew_current = SLEW_CURRENT if slew_current is None else slew_current

        self.stopPSOutput()
        self.stopDischarge()
        self.setVoltageLimMax(charge_volt_end - 0.01)
        self.setVoltageProt(charge_volt_prot)
        self.setCurrentLimMax(charge_current_max - 0.01)
        self.setCurrentProt(charge_current_prot)
        self.setVoltageSlew(slew_volt)
        self.setCurrentSlew(slew_current)
        self.setPowerProt(charge_power_prot)

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
        multimeter_mode: str | None = None,
    ):
        TotstartTime = datetime.now()
        # Configure safety limits before running
        if multimeter_mode:
            self.multimeterController.checkDeviceConnection()
            if multimeter_mode == "tcouple":
                self.multimeterController.configure_thermocouple()

        print("===========================")
        print(f"Charge time {charge_time}")
        self.apply_safety_limits(
            charge_volt_prot,
            charge_current_prot,
            charge_power_prot,
            charge_volt_end,
            charge_current_max,
            slew_volt,
            slew_current,
        )
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

            # Charging loop
            self.startPSOutput()
            self.chargeCC(charge_current_max)
            self.setVoltage(charge_volt_start)
            print('Charging')
            while (datetime.now() < Cend_time):
                # while Charging do the following
                time.sleep(self.timeInterval)  # Wait between measurements
                tmp = datetime.now() - ChargestartTime
                # gradually ramp voltage from charge_volt_start to
                # charge_volt_end during the lead-in period
                if leadin_time > 0:
                    ratio = min(tmp.total_seconds() / float(leadin_time), 1.0)
                else:
                    ratio = 1.0
                currentVolt = charge_volt_start + DeltaV * ratio
                if currentVolt > charge_volt_end:
                    currentVolt = charge_volt_end
                self.setVoltage(currentVolt)

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
                if multimeter_mode == "voltage":
                    dataStorage.addMMVoltage(self.getVoltageMM())
                elif multimeter_mode == "tcouple":
                    dataStorage.addMMTemperature(self.getTemperatureMM())
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
            # self.setCCLmode()  # set the DC to CC low range mode
            self.setCCMmode()

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
                if multimeter_mode == "voltage":
                    dataStorage.addMMVoltage(self.getVoltageMM())
                elif multimeter_mode == "tcouple":
                    dataStorage.addMMTemperature(self.getTemperatureMM())
                if (v < dcharge_volt_min):  # Breaking out if minimum voltage has been reached
                    print(f"below {dcharge_volt_min} volts")
                    break
            self.stopDischarge()  # Inactivate the electronic load
            # Discharging loop ends

            # Use multimeter temperature in filename when available
            dataStorage.createTable(
                test_name,
                dcharge_current_max,
                cycleNumber,
                temperature,
                self.timeInterval,
                charge_time,
            )

        # Set the event to indicate that testing is finished
        self.event.set()

    def efficiency_test(
        self,
        charge_current: float,
        discharge_current: float,
        charge_voltage: float = 4.1,
        discharge_voltage: float = 2.75,
        temperature: float = 20.0,
    ) -> None:
        """Perform a round trip efficiency test using a CC–CV charge and CC
        discharge as described in IEC standards."""

        dataStorage = DataStorage()
        self.event.clear()
        self.apply_safety_limits(
            charge_volt_end=charge_voltage,
            charge_current_max=charge_current,
        )

        energy_in = 0.0
        energy_out = 0.0
        elapsed = 0.0

        # ----- CC step -----
        print("Charging (CC stage)")
        self.startPSOutput()
        self.chargeCC(charge_current)
        self.setVoltage(charge_voltage)
        while True:
            time.sleep(self.timeInterval)
            elapsed += self.timeInterval
            v = self.getVoltagePSC()
            c = self.getCurrentPSC()
            energy_in += v * c * self.timeInterval / 3600.0
            dataStorage.addTime(elapsed)
            dataStorage.addVoltage(v)
            dataStorage.addCurrent(c)
            if v >= charge_voltage:
                break

        # ----- CV step -----
        print("Charging (CV stage)")
        self.chargeCV(charge_voltage)
        while True:
            time.sleep(self.timeInterval)
            elapsed += self.timeInterval
            v = self.getVoltagePSC()
            c = self.getCurrentPSC()
            energy_in += v * c * self.timeInterval / 3600.0
            dataStorage.addTime(elapsed)
            dataStorage.addVoltage(v)
            dataStorage.addCurrent(c)
            if c <= 0.05 * charge_current:
                break

        self.stopPSOutput()

        print("Resting for 10 minutes")
        time.sleep(600)

        # ----- Discharge step -----
        print("Discharging")
        self.stopDischarge()
        self.setCCLmode()
        self.setCCcurrentL1(discharge_current)
        self.startDischarge()
        while True:
            time.sleep(self.timeInterval)
            elapsed += self.timeInterval
            v = self.getVoltageELC()
            c = self.getCurrentELC()
            energy_out += v * c * self.timeInterval / 3600.0
            dataStorage.addTime(elapsed)
            dataStorage.addVoltage(v)
            dataStorage.addCurrent(c)
            if v <= discharge_voltage:
                break

        self.stopDischarge()
        efficiency = 0.0
        if energy_in > 0:
            efficiency = (energy_out / energy_in) * 100.0
        print(f"Efficiency: {efficiency:.2f}%")
        dataStorage.createTable(
            "efficiency_test", discharge_current, 0, temperature, self.timeInterval
        )

        self.event.set()

    def rate_characteristic_test(
        self,
        discharge_currents,
        charge_current: float,
        charge_voltage: float = 4.1,
        discharge_voltage: float = 2.75,
        temperature: float = 20.0,
    ) -> None:
        """Measure capacity at multiple discharge rates."""

        self.event.clear()
        self.apply_safety_limits(
            charge_volt_end=charge_voltage,
            charge_current_max=charge_current,
        )
        for i, d_current in enumerate(discharge_currents):
            dataStorage = DataStorage()
            elapsed = 0.0

            # -- charge cell using CC–CV --
            self.startPSOutput()
            self.chargeCC(charge_current)
            self.setVoltage(charge_voltage)
            while True:
                time.sleep(self.timeInterval)
                elapsed += self.timeInterval
                v = self.getVoltagePSC()
                c = self.getCurrentPSC()
                dataStorage.addTime(elapsed)
                dataStorage.addVoltage(v)
                dataStorage.addCurrent(c)
                if v >= charge_voltage:
                    break
            self.chargeCV(charge_voltage)
            while True:
                time.sleep(self.timeInterval)
                elapsed += self.timeInterval
                v = self.getVoltagePSC()
                c = self.getCurrentPSC()
                dataStorage.addTime(elapsed)
                dataStorage.addVoltage(v)
                dataStorage.addCurrent(c)
                if c <= 0.05 * charge_current:
                    break
            self.stopPSOutput()

            time.sleep(600)  # rest

            # -- discharge step --
            self.stopDischarge()
            self.setCCLmode()
            self.setCCcurrentL1(d_current)
            self.startDischarge()
            capacity = 0.0
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
                if v <= discharge_voltage:
                    break
            self.stopDischarge()
            dataStorage.createTable(
                f"rate_characteristic_{i}", d_current, i, temperature, self.timeInterval
            )

        self.event.set()

    def ocv_curve_test(
        self,
        step_current: float,
        steps: int = 10,
        rest_time: float = 1800.0,
        temperature: float = 20.0,
    ) -> None:
        """Generate an OCV curve by stepping the SOC and measuring the open
        circuit voltage after each rest period."""

        dataStorage = DataStorage()
        self.event.clear()
        self.apply_safety_limits(charge_current_max=step_current)

        elapsed = 0.0
        for i in range(steps + 1):
            # charge for one step
            self.startPSOutput()
            self.chargeCC(step_current)
            time.sleep(60)
            self.stopPSOutput()

            print(f"Resting before OCV measurement {i}")
            time.sleep(rest_time)
            v = self.getVoltageELC()
            elapsed += rest_time
            dataStorage.addTime(elapsed)
            dataStorage.addVoltage(v)
            dataStorage.addCurrent(0.0)
            print(f"Step {i}: OCV {v:.4f} V")

        dataStorage.createTable(
            "ocv_curve_test", step_current, 0, temperature, self.timeInterval
        )
        self.event.set()

    def internal_resistance_test(
        self,
        pulse_current: float,
        pulse_duration: float = 1.0,
        temperature: float = 20.0,
    ) -> None:
        """Measure the DC and AC internal resistance using a current pulse and
        the multimeter reading."""

        dataStorage = DataStorage()
        self.event.clear()

        # Open circuit voltage
        self.apply_safety_limits(charge_current_max=pulse_current)
        ocv = self.getVoltageELC()
        print(f"OCV: {ocv:.4f} V")

        # Apply current pulse
        self.stopDischarge()
        self.setCCLmode()
        self.setCCcurrentL1(pulse_current)
        self.startDischarge()
        time.sleep(pulse_duration)
        v_loaded = self.getVoltageELC()
        self.stopDischarge()

        delta_v = ocv - v_loaded
        r_dc = 0.0
        if pulse_current != 0:
            r_dc = delta_v / pulse_current
        r_ac = float(self.multimeterController.getResistance())
        print(f"DC resistance: {r_dc:.4f} ohm, AC resistance: {r_ac}")

        dataStorage.addTime(0.0)
        dataStorage.addVoltage(ocv)
        dataStorage.addCurrent(0.0)
        dataStorage.addTime(pulse_duration)
        dataStorage.addVoltage(v_loaded)
        dataStorage.addCurrent(pulse_current)

        dataStorage.createTable(
            "internal_resistance_test", pulse_current, 0, temperature, self.timeInterval
        )

        self.event.set()

    def actual_capacity_test(
        self,
        charge_current_1c: float,
        discharge_current_1c: float,
        rest_time: float = 3600.0,
        charge_voltage: float = 4.1,
        temperature: float = 20.0,
    ) -> float:
        """Perform an actual capacity test.

        The procedure charges the cell at ``charge_current_1c`` up to ``charge_voltage``,
        rests for one hour and then discharges at ``discharge_current_1c`` down
        to 2.75 V while logging the cumulative capacity.
        """

        dataStorage = DataStorage()
        self.event.clear()

        # ----- Charge step -----
        self.apply_safety_limits(
            charge_volt_end=charge_voltage,
            charge_current_max=charge_current_1c,
        )
        self.startPSOutput()
        self.chargeCC(charge_current_1c)
        self.setVoltage(charge_voltage)

        elapsed = 0.0
        capacity = 0.0
        print(f"Charging to {charge_voltage} V at {charge_current_1c} A")
        while True:
            time.sleep(self.timeInterval)
            elapsed += self.timeInterval
            v = self.getVoltageELC()
            c = self.getCurrentPSC()
            dataStorage.addTime(elapsed)
            dataStorage.addVoltage(v)
            dataStorage.addCurrent(c)
            dataStorage.addCapacity(capacity)
            if c <= 1.5:
                break

        self.stopPSOutput()

        # ----- Rest step -----
        print(f"Resting for {rest_time} seconds")
        time.sleep(rest_time)

        # ----- Discharge step -----
        self.stopDischarge()
        self.setCCHmode()
        self.setCCcurrentL1(discharge_current_1c)
        self.startDischarge()

        print(f"Discharging to 2.75 V at {discharge_current_1c} A")
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
            "actual_capacity_test", discharge_current_1c, 0, temperature, self.timeInterval
        )

        print(f"Accumulated capacity: {capacity:.3f} Ah")
        self.event.set()
        return capacity


