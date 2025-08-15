"""Core routines for controlling custom battery test sequences."""

from datetime import datetime, timedelta
import os
import struct
import threading
import time
import traceback

try:
    import pyvisa
    VisaIOError = pyvisa.errors.VisaIOError
except Exception:  # pyvisa may not be installed when using mock drivers
    class VisaIOError(Exception):
        """Fallback VisaIOError when pyvisa is unavailable."""
        pass

from AlIonTestSoftwareDataManagement import DataStorage
from AlIonTestSoftwareDeviceDrivers import (
    PowerSupplyController,
    ElectronicLoadController,
    MultimeterController,
)
from AlIonTestSoftwareDeviceDriversMock import (
    PowerSupplyControllerMock,
    ElectronicLoadControllerMock,
    MultimeterControllerMock,
)
from defaults import DEFAULT_LIMITS, DEFAULT_SAMPLE_INTERVAL


# Class used to control test procedures
class TestController:
    """Coordinate power supply, load and measurement devices for tests."""
    # Default number of seconds between each measurement. Instances store the
    # current interval in ``self.timeInterval`` which defaults to
    # ``DEFAULT_SAMPLE_INTERVAL`` but can be overridden.

    # Initiating function
    def __init__(
        self,
        multimeter_mode: str | None = None,
        debug: bool = False,
        ps_resource: str | None = None,
        el_resource: str | None = None,
        mm_resource: str | None = None,
        use_mock: bool | None = None,
        sample_interval: float = DEFAULT_SAMPLE_INTERVAL,
    ) -> None:
        self.multimeter_mode = multimeter_mode
        self.debug = debug
        if use_mock is None:
            env = os.getenv("USE_MOCK_DRIVERS")
            if env is not None:
                use_mock = env.lower() in ("1", "true", "yes")
            else:
                use_mock = False

        if use_mock:
            print("Using mock objects")
            self.powerSupplyController = PowerSupplyControllerMock()
            self.electronicLoadController = ElectronicLoadControllerMock()
            self.multimeterController = MultimeterControllerMock()
        else:
            # Trying to connect to the real device controllers.  Failures for
            # each instrument are handled separately so the user knows exactly
            # which device could not be reached.
            try:
                self.powerSupplyController = PowerSupplyController(ps_resource)
                print("Testcontroller succesfully connected to Power Supply")
            except Exception as exc:  # pragma: no cover - hardware dependent
                if self.debug:
                    traceback.print_exc()
                raise SystemExit(f"Failed to connect to power supply: {exc}") from exc

            try:
                self.electronicLoadController = ElectronicLoadController(el_resource)
                print("Testcontroller succesfully connected to Electronic Load")
            except Exception as exc:  # pragma: no cover - hardware dependent
                if self.debug:
                    traceback.print_exc()
                raise SystemExit(
                    f"Failed to connect to electronic load: {exc}"
                ) from exc

            if multimeter_mode:
                try:
                    self.multimeterController = MultimeterController(mm_resource)
                    print("Testcontroller succesfully connected to Multimeter")
                    if multimeter_mode == "tcouple":
                        self.multimeterController.configure_thermocouple()
                except Exception as exc:  # pragma: no cover - hardware dependent
                    if self.debug:
                        traceback.print_exc()
                    raise SystemExit(
                        f"Failed to connect to multimeter: {exc}"
                    ) from exc
            else:
                self.multimeterController = MultimeterControllerMock()

        # Create an event to indicate if test is running
        self.event = threading.Event()
        # Event used to gracefully abort a running test
        self.stop_event = threading.Event()
        # Sampling interval between measurements
        self.timeInterval = sample_interval

    def _debug(self, message: str, mm_value: float | None = None) -> None:
        """Print debug message when debug mode is enabled.

        If ``mm_value`` is given the measurement is appended to the output.
        """
        if self.debug:
            if mm_value is not None:
                print(f"{message} MM:{mm_value:.4f}")
            else:
                print(message)

    def abort(self) -> None:
        """Stop all outputs and signal running loops to exit."""
        self.stop_event.set()
        try:
            self.stop_ps_output()
        except Exception:
            pass
        try:
            self.stop_discharge()
        except Exception:
            pass

    # Defining basic functionality of all remote devices through the device controller
    #####  62000P Power supply #####
    # Function for constant CURRENT charging, taking in current in amps
    def charge_cc(self, amps):
        self.powerSupplyController.chargeCC(amps)

    # Function for constant VOLTAGE charging, taking in voltage in volts
    def charge_cv(self, volts):
        self.powerSupplyController.chargeCV(volts)

    # Function for constant POWER charging, taking in power in watts
    def charge_cp(self, watts):
        self.powerSupplyController.chargeCP(watts)

    # def startCharge(self):
    #     self.powerSupplyController.st
    # Functions to START/STOP the powersupply from charging
    def start_ps_output(self):
        self.powerSupplyController.startOutput()

    def stop_ps_output(self):
        self.powerSupplyController.stopOutput()

    # Functions that allow user to set the maximum voltage, current and power for safety
    #### VOLTAGE #### VOLTAGE #### VOLTAGE #### VOLTAGE ####
    def set_voltage(self, volts: float):
        self.powerSupplyController.setVoltage(volts)

    def set_voltage_lim_max(self, volts: float):
        self.powerSupplyController.setVoltageLimMax(volts)

    def set_voltage_lim_min(self, volts: float):
        self.powerSupplyController.setVoltageLimMin(volts)

    def set_voltage_prot(self, volts: float):
        self.powerSupplyController.setVoltageProt(volts)

    def set_voltage_slew(self, volts: float):
        self.powerSupplyController.setVoltageSlew(volts)

    # def setMaxVoltageMax(self):
    #     self.powerSupplyController.setVoltageMax()

    #### CURRENT #### CURRENT #### CURRENT #### CURRENT ####
    def set_current(self, amps: float):
        self.powerSupplyController.setCurrent(amps)

    def set_current_lim_max(self, amps: float):
        self.powerSupplyController.setCurrentLimMax(amps)

    def set_current_lim_min(self, amps: float):
        self.powerSupplyController.setCurrentLimMin(amps)

    def set_current_prot(self, amps: float):
        self.powerSupplyController.setCurrentProt(amps)

    def set_current_slew(self, amps: float):
        self.powerSupplyController.setCurrentSlew(amps)

    # def setMaxCurrentMax(self):
    #     self.powerSupplyController.setCurrentMax()

    #### POWER #### POWER #### POWER #### POWER #### POWER ####
    def set_power_prot(self, watts: float):
        self.powerSupplyController.setPowerProt(watts)

    # def setMaxPowerMax(self):
    #     self.powerSupplyController.setPowerMax()

    # DISCHARGE functions ###### DC LOAD 63600-5

    def start_discharge(self):
        self.electronicLoadController.startDischarge()  # Activates the electronic load

    def stop_discharge(self):
        self.electronicLoadController.stopDischarge()  # Inactivates the electronic load

    def set_ccl_mode(self):
        # Switch to CC mode Low Range (max 0.8 amper)
        self.electronicLoadController.setCCLmode()

    def set_ccm_mode(self):
        # Switch to CC mode Medium Range (max 8 amper)
        self.electronicLoadController.setCCMmode()

    def set_cch_mode(self):
        # Switch to CC mode High Range
        self.electronicLoadController.setCCHmode()

    def set_cc_current_l1(self, amper: float):
        self.electronicLoadController.setCCcurrentL1(
            amper)  # Set the desired current of Channel L1

    def set_cc_current_l1_max(self, amper: float):
        self.electronicLoadController.setCCcurrentL1MAX(
            amper)  # Set the desired current of Channel L1

    def get_cc_current_l1_max(self):
        # Read the maximum amp setting of Channel 1
        try:
            return float(self.electronicLoadController.getCCcurrentL1MAX())
        except (VisaIOError, struct.error) as err:
            print(f"Electronic-load read timeout: {err}")
            return float('nan')

    # Helper methods for discharging and reading instrument values

    def discharge_cc(self, amper):
        self.electronicLoadController.dischargeCC(amper)

    def discharge_cv(self, volts):
        self.electronicLoadController.dischargeCV(volts)

    def discharge_cp(self, watts):
        self.electronicLoadController.dischargeCP(watts)

    def get_voltage_elc(self):
        try:
            x = self.electronicLoadController.getVoltage()
        except (VisaIOError, struct.error) as err:
            print(f"Electronic-load read timeout: {err}")
            return float('nan')
        return float(x)

    def get_current_elc(self):
        try:
            x = self.electronicLoadController.getCurrent()
        except (VisaIOError, struct.error) as err:
            print(f"Electronic-load read timeout: {err}")
            return float('nan')
        return float(x)

    def get_voltage_psc(self):
        try:
            x = self.powerSupplyController.getVoltage()
        except (VisaIOError, struct.error) as err:
            print(f"Power-supply read timeout: {err}")
            return float('nan')
        return float(x)

    def get_current_psc(self):
        try:
            x = self.powerSupplyController.getCurrent()
        except (VisaIOError, struct.error) as err:
            print(f"Power-supply read timeout: {err}")
            return float('nan')
        return float(x)

    def get_voltage_mm(self):
        try:
            return float(self.multimeterController.getVolts())
        except (VisaIOError, struct.error) as err:
            print(f"Multimeter read timeout: {err}")
            return float('nan')

    def get_temperature_mm(self):
        try:
            return float(self.multimeterController.getThermocoupleTemp())
        except (VisaIOError, struct.error) as err:
            print(f"Multimeter read timeout: {err}")
            return float('nan')

    # def stop_discharge(self):
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

        If parameters are omitted, values from ``defaults.DEFAULT_LIMITS`` are
        used.
        """

        charge_volt_prot = (
            DEFAULT_LIMITS["CHARGE_VOLT_PROT"]
            if charge_volt_prot is None
            else charge_volt_prot
        )
        charge_current_prot = (
            DEFAULT_LIMITS["CHARGE_CURRENT_PROT"]
            if charge_current_prot is None
            else charge_current_prot
        )
        charge_power_prot = (
            DEFAULT_LIMITS["CHARGE_POWER_PROT"]
            if charge_power_prot is None
            else charge_power_prot
        )
        charge_volt_end = (
            DEFAULT_LIMITS["CHARGE_VOLT_END"]
            if charge_volt_end is None
            else charge_volt_end
        )
        charge_current_max = (
            DEFAULT_LIMITS["CHARGE_CURRENT_MAX"]
            if charge_current_max is None
            else charge_current_max
        )
        slew_volt = (
            DEFAULT_LIMITS["SLEW_VOLT"] if slew_volt is None else slew_volt
        )
        slew_current = (
            DEFAULT_LIMITS["SLEW_CURRENT"]
            if slew_current is None
            else slew_current
        )

        self.stop_ps_output()
        self.stop_discharge()
        self.set_voltageLimMax(charge_volt_end - 0.01)
        self.set_voltageProt(charge_volt_prot)
        self.set_currentLimMax(charge_current_max - 0.01)
        self.set_currentProt(charge_current_prot)
        self.set_voltageSlew(slew_volt)
        self.set_currentSlew(slew_current)
        self.set_power_prot(charge_power_prot)

    # Test protocal for testing the capacity of a battery

# Runs a custom test using the provided parameters
    def _custom_test_impl(
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
        rest_time: int,
        num_cycles: int,
        charge_mode: str = "CC",
        discharge_mode: str = "CC",
        multimeter_mode: str | None = None,
    ):
        valid_modes = {"CC", "CV", "CP"}
        if charge_mode not in valid_modes:
            raise ValueError(f"Invalid charge_mode: {charge_mode}")
        if discharge_mode not in valid_modes:
            raise ValueError(f"Invalid discharge_mode: {discharge_mode}")

        TotstartTime = datetime.now()
        self.stop_event.clear()
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
        print(f"Max allowable discharge current {self.get_cc_current_l1_max()}")
        print("===========================")

        # Charge each cycle for charge_time seconds
        Cduration = timedelta(seconds=charge_time)
        # Discharge each cycle for dcharge_time seconds
        Dduration = timedelta(seconds=dcharge_time)
        Lduration = timedelta(seconds=leadin_time)     # Leadin time in seconds
        # the amount to increase the start Volt to get to end Volt
        DeltaV = charge_volt_end-charge_volt_start

        # Charging/Discharging loop starts
        try:
            for cycleNumber in range(int(num_cycles)):
                dataStorage = DataStorage()
                Cend_time = datetime.now() + Cduration
                ChargestartTime = datetime.now()
                try:
                    # Charging loop
                    self.start_ps_output()
                    if charge_mode == "CC":
                        self.charge_cc(charge_current_max)
                        self.set_voltage(charge_volt_start)
                    elif charge_mode == "CV":
                        self.charge_cv(charge_volt_end)
                    elif charge_mode == "CP":
                        self.charge_cp(charge_volt_end * charge_current_max)
                    print('Charging')
                    while datetime.now() < Cend_time and not self.stop_event.is_set():
                        time.sleep(self.timeInterval)
                        tmp = datetime.now() - ChargestartTime
                        if charge_mode == "CC":
                            if leadin_time > 0:
                                ratio = min(tmp.total_seconds() / float(leadin_time), 1.0)
                            else:
                                ratio = 1.0
                            currentVolt = charge_volt_start + DeltaV * ratio
                            if currentVolt > charge_volt_end:
                                currentVolt = charge_volt_end
                            self.set_voltage(currentVolt)
                        v_ps = self.get_voltage_psc()
                        v = self.get_voltage_elc()
                        c = self.get_current_psc()
                        mm = None
                        if multimeter_mode == "voltage":
                            mm = self.get_voltage_mm()
                        elif multimeter_mode == "tcouple":
                            mm = self.get_temperature_mm()
                        self._debug(
                            f"{cycleNumber} of {num_cycles} -CHARGING- {tmp.total_seconds():03.2f} s of {Cduration.total_seconds():.1f} s - V_PS:{v_ps:.4f} V:{v:.4f} C:{c:.4f}",
                            mm,
                        )
                        dataStorage.add_time(float(tmp.total_seconds()))
                        dataStorage.add_voltage(v)
                        dataStorage.add_current(c)
                        if multimeter_mode == "voltage":
                            assert mm is not None
                            dataStorage.add_mm_voltage(mm)
                        elif multimeter_mode == "tcouple":
                            assert mm is not None
                            dataStorage.add_mm_temperature(mm)
                    self.stop_ps_output()
                    if rest_time > 0:
                        time.sleep(rest_time)

                    Dend_time = datetime.now() + Dduration
                    self.stop_discharge()
                    if discharge_mode == "CC":
                        self.discharge_cc(dcharge_current_max)
                    elif discharge_mode == "CV":
                        self.discharge_cv(dcharge_volt_min)
                    elif discharge_mode == "CP":
                        self.discharge_cp(dcharge_volt_min * dcharge_current_max)

                    DischargestartTime = datetime.now()
                    print('Discharging')
                    while datetime.now() < Dend_time and not self.stop_event.is_set():
                        time.sleep(self.timeInterval)
                        tmp = datetime.now()-DischargestartTime
                        v = self.get_voltage_elc()
                        c = self.get_current_elc()
                        mm = None
                        if multimeter_mode == "voltage":
                            mm = self.get_voltage_mm()
                        elif multimeter_mode == "tcouple":
                            mm = self.get_temperature_mm()
                        self._debug(
                            f"{cycleNumber} of {num_cycles} -DISCHARGING- {tmp.total_seconds():03.2f} s of {Dduration.total_seconds():.1f} s - V:{v:.4f} C:{c:.4f}",
                            mm,
                        )
                        dataStorage.add_time(float(tmp.total_seconds()))
                        dataStorage.add_voltage(v)
                        dataStorage.add_current(c)
                        if multimeter_mode == "voltage":
                            assert mm is not None
                            dataStorage.add_mm_voltage(mm)
                        elif multimeter_mode == "tcouple":
                            assert mm is not None
                            dataStorage.add_mm_temperature(mm)
                        if v < dcharge_volt_min:
                            print(f"below {dcharge_volt_min} volts")
                            break
                    self.stop_discharge()
                    if rest_time > 0:
                        time.sleep(rest_time)
                except KeyboardInterrupt:
                    print("Keyboard interrupt - aborting test")
                    self.abort()
                    raise
                finally:
                    dataStorage.create_table(
                        test_name,
                        dcharge_current_max,
                        cycleNumber,
                        temperature,
                        self.timeInterval,
                        charge_time,
                    )
                    self.stop_ps_output()
                    self.stop_discharge()
                if self.stop_event.is_set():
                    break
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_ps_output()
            self.stop_discharge()

        # Set the event to indicate that testing is finished
        self.event.set()

    def custom_test(
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
        rest_time: int,
        num_cycles: int,
        charge_mode: str,
        discharge_mode: str,
        sample_interval: float,
        multimeter_mode: str | None = None,
    ):
        prev_interval = self.timeInterval
        self.timeInterval = sample_interval
        try:
            self._custom_test_impl(
                test_name,
                temperature,
                charge_volt_prot,
                charge_current_prot,
                charge_power_prot,
                charge_volt_start,
                charge_volt_end,
                charge_current_max,
                dcharge_volt_min,
                dcharge_current_max,
                slew_volt,
                slew_current,
                leadin_time,
                charge_time,
                dcharge_time,
                rest_time,
                num_cycles,
                charge_mode,
                discharge_mode,
                multimeter_mode,
            )
        finally:
            self.timeInterval = prev_interval

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
        self.start_ps_output()
        self.charge_cc(charge_current)
        self.set_voltage(charge_voltage)
        while True:
            time.sleep(self.timeInterval)
            elapsed += self.timeInterval
            v = self.get_voltage_psc()
            c = self.get_current_psc()
            self._debug(
                f"CC Charging: {elapsed:.2f} s - V:{v:.4f} C:{c:.4f}"
            )
            energy_in += v * c * self.timeInterval / 3600.0
            dataStorage.add_time(elapsed)
            dataStorage.add_voltage(v)
            dataStorage.add_current(c)
            if v >= charge_voltage:
                break

        # ----- CV step -----
        print("Charging (CV stage)")
        self.charge_cv(charge_voltage)
        while True:
            time.sleep(self.timeInterval)
            elapsed += self.timeInterval
            v = self.get_voltage_psc()
            c = self.get_current_psc()
            self._debug(
                f"CV Charging: {elapsed:.2f} s - V:{v:.4f} C:{c:.4f}"
            )
            energy_in += v * c * self.timeInterval / 3600.0
            dataStorage.add_time(elapsed)
            dataStorage.add_voltage(v)
            dataStorage.add_current(c)
            if c <= 0.05 * charge_current:
                break

        self.stop_ps_output()

        print("Resting for 10 minutes")
        time.sleep(600)

        # ----- Discharge step -----
        print("Discharging")
        self.stop_discharge()
        self.set_ccl_mode()
        self.set_cc_current_l1(discharge_current)
        self.start_discharge()
        while True:
            time.sleep(self.timeInterval)
            elapsed += self.timeInterval
            v = self.get_voltage_elc()
            c = self.get_current_elc()
            self._debug(
                f"Discharging: {elapsed:.2f} s - V:{v:.4f} C:{c:.4f}"
            )
            energy_out += v * c * self.timeInterval / 3600.0
            dataStorage.add_time(elapsed)
            dataStorage.add_voltage(v)
            dataStorage.add_current(c)
            if v <= discharge_voltage:
                break

        self.stop_discharge()
        efficiency = 0.0
        if energy_in > 0:
            efficiency = (energy_out / energy_in) * 100.0
        print(f"Efficiency: {efficiency:.2f}%")
        dataStorage.create_table(
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
            self.start_ps_output()
            self.charge_cc(charge_current)
            self.set_voltage(charge_voltage)
            while True:
                time.sleep(self.timeInterval)
                elapsed += self.timeInterval
                v = self.get_voltage_psc()
                c = self.get_current_psc()
                self._debug(
                    f"CC Charging: {elapsed:.2f} s - V:{v:.4f} C:{c:.4f}"
                )
                dataStorage.add_time(elapsed)
                dataStorage.add_voltage(v)
                dataStorage.add_current(c)
                if v >= charge_voltage:
                    break
            self.charge_cv(charge_voltage)
            while True:
                time.sleep(self.timeInterval)
                elapsed += self.timeInterval
                v = self.get_voltage_psc()
                c = self.get_current_psc()
                self._debug(
                    f"CV Charging: {elapsed:.2f} s - V:{v:.4f} C:{c:.4f}"
                )
                dataStorage.add_time(elapsed)
                dataStorage.add_voltage(v)
                dataStorage.add_current(c)
                if c <= 0.05 * charge_current:
                    break
            self.stop_ps_output()

            time.sleep(600)  # rest

            # -- discharge step --
            self.stop_discharge()
            self.set_ccl_mode()
            self.set_cc_current_l1(d_current)
            self.start_discharge()
            capacity = 0.0
            while True:
                time.sleep(self.timeInterval)
                elapsed += self.timeInterval
                v = self.get_voltage_elc()
                c = self.get_current_elc()
                capacity += c * self.timeInterval / 3600.0
                self._debug(
                    f"Discharging: {elapsed:.2f} s - V:{v:.4f} C:{c:.4f} Ah:{capacity:.3f}"
                )
                dataStorage.add_time(elapsed)
                dataStorage.add_voltage(v)
                dataStorage.add_current(c)
                dataStorage.add_capacity(capacity)
                if v <= discharge_voltage:
                    break
            self.stop_discharge()
            dataStorage.create_table(
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
            self.start_ps_output()
            self.charge_cc(step_current)
            time.sleep(60)
            self.stop_ps_output()

            print(f"Resting before OCV measurement {i}")
            time.sleep(rest_time)
            v = self.get_voltage_elc()
            elapsed += rest_time
            dataStorage.add_time(elapsed)
            dataStorage.add_voltage(v)
            dataStorage.add_current(0.0)
            print(f"Step {i}: OCV {v:.4f} V")

        dataStorage.create_table(
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
        ocv = self.get_voltage_elc()
        print(f"OCV: {ocv:.4f} V")

        # Apply current pulse
        self.stop_discharge()
        self.set_ccl_mode()
        self.set_cc_current_l1(pulse_current)
        self.start_discharge()
        time.sleep(pulse_duration)
        v_loaded = self.get_voltage_elc()
        self.stop_discharge()

        delta_v = ocv - v_loaded
        r_dc = 0.0
        if pulse_current != 0:
            r_dc = delta_v / pulse_current
        r_ac = float(self.multimeterController.getResistance())
        print(f"DC resistance: {r_dc:.4f} ohm, AC resistance: {r_ac}")

        dataStorage.add_time(0.0)
        dataStorage.add_voltage(ocv)
        dataStorage.add_current(0.0)
        dataStorage.add_time(pulse_duration)
        dataStorage.add_voltage(v_loaded)
        dataStorage.add_current(pulse_current)

        dataStorage.create_table(
            "internal_resistance_test", pulse_current, 0, temperature, self.timeInterval
        )

        self.event.set()

    def actual_capacity_test(
        self,
        charge_current_1c: float,
        discharge_current_1c: float,
        rest_time: float = 3600.0,
        charge_voltage: float = 4.1,
        min_voltage: float = 2.75,
        temperature: float = 20.0,
        finish_current: float = 1.5,
    ) -> float:
        """Perform an actual capacity test.

        The procedure charges the cell at ``charge_current_1c`` up to ``charge_voltage``,
        rests for ``rest_time`` seconds and then discharges at ``discharge_current_1c``
        down to ``min_voltage`` while logging the cumulative capacity. The
        charging phase ends once the supply current stays below ``finish_current``
        for at least 10 seconds.
        """

        dataStorage = DataStorage()
        self.event.clear()

        elapsed = 0.0
        capacity = 0.0
        try:
            try:
                # ----- Charge step -----
                self.apply_safety_limits(
                    charge_volt_end=charge_voltage,
                    charge_current_max=charge_current_1c,
                )
                self.start_ps_output()
                self.charge_cc(charge_current_1c)
                self.set_voltage(charge_voltage)

                elapsed = 0.0
                capacity = 0.0
                print(f"Charging to {charge_voltage} V at {charge_current_1c} A")
                low_current_time = 0.0
                while not self.stop_event.is_set():
                    time.sleep(self.timeInterval)
                    elapsed += self.timeInterval
                    if self.stop_event.is_set():
                        break
                    v = self.get_voltage_elc()
                    c = self.get_current_psc()
                    mm = None
                    if self.multimeter_mode == "voltage":
                        mm = self.get_voltage_mm()
                    elif self.multimeter_mode == "tcouple":
                        mm = self.get_temperature_mm()
                    self._debug(
                        f"Charging: {elapsed:.2f} s - V:{v:.4f} C:{c:.4f} Ah:{capacity:.3f}",
                        mm,
                    )
                    dataStorage.add_time(elapsed)
                    dataStorage.add_voltage(v)
                    dataStorage.add_current(c)
                    if self.multimeter_mode == "voltage":
                        assert mm is not None
                        dataStorage.add_mm_voltage(mm)
                    elif self.multimeter_mode == "tcouple":
                        assert mm is not None
                        dataStorage.add_mm_temperature(mm)
                    dataStorage.add_capacity(capacity)
                    if self.stop_event.is_set():
                        break
                    if c <= finish_current:
                        low_current_time += self.timeInterval
                        if low_current_time >= 10.0:
                            break
                    else:
                        low_current_time = 0.0

                self.stop_ps_output()

                # ----- Rest step -----
                print(f"Resting for {rest_time} seconds")
                time.sleep(rest_time)

                # ----- Discharge step -----
                self.stop_discharge()
                self.set_cch_mode()
                self.set_cc_current_l1(discharge_current_1c)
                self.start_discharge()

                print(f"Discharging to {min_voltage} V at {discharge_current_1c} A")
                while not self.stop_event.is_set():
                    time.sleep(self.timeInterval)
                    elapsed += self.timeInterval
                    if self.stop_event.is_set():
                        break
                    v = self.get_voltage_elc()
                    c = self.get_current_elc()
                    capacity += c * self.timeInterval / 3600.0
                    mm = None
                    if self.multimeter_mode == "voltage":
                        mm = self.get_voltage_mm()
                    elif self.multimeter_mode == "tcouple":
                        mm = self.get_temperature_mm()
                    self._debug(
                        f"Discharging: {elapsed:.2f} s - V:{v:.4f} C:{c:.4f} Ah:{capacity:.3f}",
                        mm,
                    )
                    dataStorage.add_time(elapsed)
                    dataStorage.add_voltage(v)
                    dataStorage.add_current(c)
                    if self.multimeter_mode == "voltage":
                        assert mm is not None
                        dataStorage.add_mm_voltage(mm)
                    elif self.multimeter_mode == "tcouple":
                        assert mm is not None
                        dataStorage.add_mm_temperature(mm)
                    dataStorage.add_capacity(capacity)
                    if v <= min_voltage or self.stop_event.is_set():
                        break

                self.stop_discharge()
            except KeyboardInterrupt:
                print("Keyboard interrupt - aborting test")
                self.abort()
                raise
            finally:
                dataStorage.create_table(
                    "actual_capacity_test",
                    discharge_current_1c,
                    0,
                    temperature,
                    self.timeInterval,
                )
                self.stop_ps_output()
                self.stop_discharge()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_ps_output()
            self.stop_discharge()

        print(f"Accumulated capacity: {capacity:.3f} Ah")
        self.event.set()
        return capacity


