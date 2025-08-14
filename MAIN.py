"""Command line interface for running custom battery tests."""

from dataclasses import dataclass
import argparse
import json
import os
from pathlib import Path
from AlIonBatteryTestSoftware import TestController
from defaults import DEFAULT_LIMITS

# Charge/discharge voltage and current limits
CHARGE_VOLT_START: float = 4.1    # V
CHARGE_VOLT_END: float = DEFAULT_LIMITS["CHARGE_VOLT_END"]
CHARGE_CURRENT_MAX: float = DEFAULT_LIMITS["CHARGE_CURRENT_MAX"]

DCHARGE_VOLT_MIN: float = 2.75    # V
DCHARGE_CURRENT_MAX: float = 20    # A

CHARGE_VOLT_PROT: int = DEFAULT_LIMITS["CHARGE_VOLT_PROT"]
CHARGE_CURRENT_PROT: int = DEFAULT_LIMITS["CHARGE_CURRENT_PROT"]
CHARGE_POWER_PROT: int = DEFAULT_LIMITS["CHARGE_POWER_PROT"]


# Slew (ramp) settings
SLEW_VOLT: float = DEFAULT_LIMITS["SLEW_VOLT"]
SLEW_CURRENT: float = DEFAULT_LIMITS["SLEW_CURRENT"]

# Timing (in seconds)
# Ramp duration for increasing the charge voltage from CHARGE_VOLT_START
# to CHARGE_VOLT_END at the beginning of each cycle
LEADIN_TIME: int = 1    # s

CHARGE_TIME: int = 5    # s
DCHARGE_TIME: int = 5   # s
REST_TIME: int = 0      # s

# Cycling
NUM_CYCLES: int = 1   # n

# Misc
TEST_NAME: str = "YUASA"
TEMPERATURE: float = 23.4    # °C


@dataclass
class CustomTestSettings:
    """Configuration for a custom test run."""

    test_name: str = TEST_NAME
    temperature: float = TEMPERATURE
    charge_volt_prot: int = CHARGE_VOLT_PROT
    charge_current_prot: int = CHARGE_CURRENT_PROT
    charge_power_prot: int = CHARGE_POWER_PROT
    charge_volt_start: float = CHARGE_VOLT_START
    charge_volt_end: float = CHARGE_VOLT_END
    charge_current_max: float = CHARGE_CURRENT_MAX
    dcharge_volt_min: float = DCHARGE_VOLT_MIN
    dcharge_current_max: float = DCHARGE_CURRENT_MAX
    slew_volt: float = SLEW_VOLT
    slew_current: float = SLEW_CURRENT
    leadin_time: int = LEADIN_TIME
    charge_time: int = CHARGE_TIME
    dcharge_time: int = DCHARGE_TIME
    rest_time: int = REST_TIME
    num_cycles: int = NUM_CYCLES
    charge_mode: str = "CC"
    discharge_mode: str = "CC"
    sample_interval: float = TestController.timeInterval
    multimeter_mode: str | None = None



def load_config(config_path: str, profile: str) -> tuple[dict, dict, str | None]:
    """Load profile parameters, capacity defaults and test type from a JSON file."""
    try:
        data = json.loads(Path(config_path).read_text())
    except FileNotFoundError:
        print(f"Configuration file not found: {config_path}")
        return {}, {}, None
    except json.JSONDecodeError as exc:
        print(f"Error decoding JSON from {config_path}: {exc}")
        return {}, {}, None

    if not isinstance(data, dict):
        return {}, {}, None

    profile_data = data.get(profile, {})
    if not isinstance(profile_data, dict):
        return {}, data.get("capacity_defaults", {}), None

    test_type = profile_data.get("test_type")
    params = profile_data.get("parameters", {})
    return params, data.get("capacity_defaults", {}), test_type



class TestTypes:
    def __init__(
        self,
        multimeter_mode: str | None = None,
        debug: bool = False,
        ps_resource: str | None = None,
        el_resource: str | None = None,
        mm_resource: str | None = None,
    ):
        self.testController = TestController(
            multimeter_mode, debug, ps_resource, el_resource, mm_resource
        )
        self.custom_thread = None

    def run_custom_test(self, settings: CustomTestSettings):
        """Start a custom test using the provided settings."""
        import threading
        valid_modes = {"CC", "CV", "CP"}
        if settings.charge_mode not in valid_modes:
            raise ValueError(f"Invalid charge_mode: {settings.charge_mode}")
        if settings.discharge_mode not in valid_modes:
            raise ValueError(f"Invalid discharge_mode: {settings.discharge_mode}")

        self.testController.event.clear()
        self.custom_thread = threading.Thread(
            target=self.testController.custom_test,
            args=(
                settings.test_name,
                settings.temperature,
                settings.charge_volt_prot,
                settings.charge_current_prot,
                settings.charge_power_prot,
                settings.charge_volt_start,
                settings.charge_volt_end,
                settings.charge_current_max,
                settings.dcharge_volt_min,
                settings.dcharge_current_max,
                settings.slew_volt,
                settings.slew_current,
                settings.leadin_time,
                settings.charge_time,
                settings.dcharge_time,
                settings.rest_time,
                settings.num_cycles,
                settings.charge_mode,
                settings.discharge_mode,
                settings.sample_interval,
                settings.multimeter_mode,
            ),
        )
        self.custom_thread.start()
        return self.custom_thread

    def stop(self):
        """Abort the running test and wait for it to finish."""
        if self.testController:
            self.testController.abort()
        if self.custom_thread is not None:
            self.custom_thread.join()


def main():
    parser = argparse.ArgumentParser(description="Run custom test")
    parser.add_argument(
        "--config-file", default="profiles.json", help="JSON file with cell settings"
    )
    parser.add_argument("--profile", help="cell profile name in config file")
    parser.add_argument("--ps-resource", help="VISA resource name for power supply")
    parser.add_argument("--el-resource", help="VISA resource name for electronic load")
    parser.add_argument("--mm-resource", help="VISA resource name for multimeter")
    parser.add_argument("--test-name")
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--charge-volt-prot", type=int)
    parser.add_argument("--charge-current-prot", type=int)
    parser.add_argument("--charge-power-prot", type=int)
    parser.add_argument("--charge-volt-start", type=float)
    parser.add_argument("--charge-volt-end", type=float)
    parser.add_argument("--charge-current-max", type=float)
    parser.add_argument("--dcharge-volt-min", type=float)
    parser.add_argument("--dcharge-current-max", type=float)
    parser.add_argument("--slew-volt", type=float)
    parser.add_argument("--slew-current", type=float)
    parser.add_argument("--leadin-time", type=int)
    parser.add_argument("--charge-time", type=int)
    parser.add_argument("--dcharge-time", type=int)
    parser.add_argument("--rest-time", type=int)
    parser.add_argument("--sample-interval", type=float)
    parser.add_argument(
        "--charge-mode",
        choices=["CC", "CV", "CP"],
        help="charging mode: CC, CV or CP",
    )
    parser.add_argument(
        "--discharge-mode",
        choices=["CC", "CV", "CP"],
        help="discharging mode: CC, CV or CP",
    )
    parser.add_argument("--num-cycles", type=int)
    parser.add_argument("--actual-capacity-test", action="store_true",
                        help="run actual capacity test")
    parser.add_argument("--capacity-charge-current", type=float,
                        help="charge current for capacity test in amperes")
    parser.add_argument("--capacity-discharge-current", type=float,
                        help="discharge current for capacity test in amperes")
    parser.add_argument("--capacity-rest-time", type=float,
                        help="rest time before discharge in seconds")
    parser.add_argument("--capacity-charge-voltage", type=float,
                        help="charge voltage for capacity test")
    parser.add_argument("--capacity-min-voltage", type=float,
                        help="minimum discharge voltage for capacity test")
    parser.add_argument("--capacity-finish-current", type=float,
                        help="current threshold to end charging during capacity test")
    parser.add_argument("--efficiency-test", action="store_true",
                        help="run efficiency test")
    parser.add_argument("--rate-characteristic-test", action="store_true",
                        help="run rate characteristic test")
    parser.add_argument("--ocv-curve-test", action="store_true",
                        help="run OCV curve test")
    parser.add_argument(
        "--internal-resistance-test",
        action="store_true",
        help="run internal resistance test (no capacity measurement)",
    )
    parser.add_argument("--rates", default="1.0,0.5,0.2",
                        help="comma separated discharge rates in A")
    parser.add_argument("--step-current", type=float, default=1.0,
                        help="step current for OCV curve")
    parser.add_argument("--steps", type=int, default=10,
                        help="number of steps for OCV curve")
    parser.add_argument(
        "--pulse-current",
        type=float,
        default=1.0,
        help="pulse current for internal resistance test",
    )
    parser.add_argument(
        "--pulse-duration",
        type=float,
        default=1.0,
        help="pulse duration for internal resistance test in seconds",
    )
    parser.add_argument(
        "--multimeter-mode",
        choices=["voltage", "tcouple"],
        help="log measurement with multimeter (voltage or thermocouple)"
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="print detailed progress information",
    )

    args = parser.parse_args()


    profile = args.profile or args.test_name or TEST_NAME
    config = {}
    capacity_defaults = {}
    test_type = None
    if args.config_file:
        config, capacity_defaults, test_type = load_config(args.config_file, profile)

    ps_resource = (
        args.ps_resource
        or os.getenv("POWER_SUPPLY_RESOURCE")
        or config.get("ps_resource")
    )
    el_resource = (
        args.el_resource
        or os.getenv("ELECTRONIC_LOAD_RESOURCE")
        or config.get("el_resource")
    )
    mm_resource = (
        args.mm_resource
        or os.getenv("MULTIMETER_RESOURCE")
        or config.get("mm_resource")
    )


    for field in CustomTestSettings.__annotations__.keys():
        if getattr(args, field) is None:
            if field in config:
                setattr(args, field, config[field])
        if getattr(args, field) is None:
            # fall back to dataclass default by leaving as None
            pass

    # apply defaults for standalone tests
    charge_volt_end = args.charge_volt_end if args.charge_volt_end is not None else CHARGE_VOLT_END
    dcharge_volt_min = args.dcharge_volt_min if args.dcharge_volt_min is not None else DCHARGE_VOLT_MIN
    charge_current_max = args.charge_current_max if args.charge_current_max is not None else CHARGE_CURRENT_MAX
    dcharge_current_max = args.dcharge_current_max if args.dcharge_current_max is not None else DCHARGE_CURRENT_MAX
    temperature = args.temperature if args.temperature is not None else TEMPERATURE

    rest_time = args.capacity_rest_time
    if rest_time is None:
        rest_time = capacity_defaults.get("rest_time", 3600.0)

    cap_charge_current = args.capacity_charge_current
    if cap_charge_current is None:
        cap_charge_current = capacity_defaults.get("charge_current", 1.0)

    cap_discharge_current = args.capacity_discharge_current
    if cap_discharge_current is None:
        cap_discharge_current = capacity_defaults.get("discharge_current", 1.0)

    multimeter_mode = args.multimeter_mode
    if multimeter_mode is None:
        multimeter_mode = capacity_defaults.get("multimeter_mode")

    cap_charge_volt = args.capacity_charge_voltage
    if cap_charge_volt is None:
        if args.charge_volt_end is None and "charge_voltage" in capacity_defaults:
            cap_charge_volt = capacity_defaults["charge_voltage"]
        else:
            cap_charge_volt = charge_volt_end

    cap_min_volt = args.capacity_min_voltage
    if cap_min_volt is None:
        if args.dcharge_volt_min is None and "min_voltage" in capacity_defaults:
            cap_min_volt = capacity_defaults["min_voltage"]
        else:
            cap_min_volt = dcharge_volt_min

    finish_current = args.capacity_finish_current
    if finish_current is None:
        finish_current = capacity_defaults.get("finish_current", 1.5)

    if args.actual_capacity_test:
        tc = TestController(multimeter_mode, args.debug, ps_resource, el_resource, mm_resource)
        tc.actual_capacity_test(
            cap_charge_current,
            cap_discharge_current,
            rest_time,
            cap_charge_volt,
            cap_min_volt,
            temperature,
            finish_current,
        )
    elif args.efficiency_test:
        tc = TestController(multimeter_mode, args.debug, ps_resource, el_resource, mm_resource)
        tc.efficiency_test(
            charge_current_max,
            dcharge_current_max,
            charge_volt_end,
            dcharge_volt_min,
            temperature,
        )
    elif args.rate_characteristic_test:
        rates = [float(r) for r in args.rates.split(',') if r]
        tc = TestController(multimeter_mode, args.debug, ps_resource, el_resource, mm_resource)
        tc.rate_characteristic_test(
            rates,
            charge_current_max,
            charge_volt_end,
            dcharge_volt_min,
            temperature,
        )
    elif args.ocv_curve_test:
        tc = TestController(multimeter_mode, args.debug, ps_resource, el_resource, mm_resource)
        tc.ocv_curve_test(
            args.step_current,
            args.steps,
            1800.0,
            temperature,
        )
    elif args.internal_resistance_test:

        tc.internal_resistance_test(
            args.pulse_current,
            args.pulse_duration,
            temperature,
        )
        capacity = tc.actual_capacity_test(
            cap_charge_current,
            cap_discharge_current,
            rest_time,
            cap_charge_volt,
            cap_min_volt,
            temperature,
            finish_current,
        )
        print(f"Measured capacity: {capacity:.3f} Ah")
    elif args.config_file and test_type:
        tc = TestController(multimeter_mode, args.debug, ps_resource, el_resource, mm_resource)
        if test_type == "actual_capacity_test":
            tc.actual_capacity_test(
                cap_charge_current,
                cap_discharge_current,
                rest_time,
                cap_charge_volt,
                cap_min_volt,
                temperature,
                finish_current,
            )
        elif test_type == "efficiency_test":
            tc.efficiency_test(
                charge_current_max,
                dcharge_current_max,
                charge_volt_end,
                dcharge_volt_min,
                temperature,
            )
        elif test_type == "rate_characteristic_test":
            rates_cfg = config.get("rates", args.rates)
            if isinstance(rates_cfg, str):
                rates = [float(r) for r in rates_cfg.split(',') if r]
            else:
                rates = [float(r) for r in rates_cfg]
            tc.rate_characteristic_test(
                rates,
                charge_current_max,
                charge_volt_end,
                dcharge_volt_min,
                temperature,
            )
        elif test_type == "ocv_curve_test":
            step_current = config.get("step_current", args.step_current)
            steps = config.get("steps", args.steps)
            tc.ocv_curve_test(
                step_current,
                steps,
                1800.0,
                temperature,
            )
        elif test_type == "internal_resistance_test":
            pulse_current = config.get("pulse_current", args.pulse_current)
            pulse_duration = config.get("pulse_duration", args.pulse_duration)
            tc.internal_resistance_test(
                pulse_current,
                pulse_duration,
                temperature,
            )
            capacity = tc.actual_capacity_test(
                cap_charge_current,
                cap_discharge_current,
                rest_time,
                cap_charge_volt,
                cap_min_volt,
                temperature,
                finish_current,
            )
            print(f"Measured capacity: {capacity:.3f} Ah")
        elif test_type == "custom":
            kwargs = {}
            for field in CustomTestSettings.__annotations__.keys():
                val = getattr(args, field, None)
                if val is not None:
                    kwargs[field] = val
            settings = CustomTestSettings(**kwargs)
            TObj = TestTypes(multimeter_mode, args.debug, ps_resource, el_resource, mm_resource)
            thread = TObj.run_custom_test(settings)
            try:
                while thread.is_alive():
                    thread.join(0.5)
            except KeyboardInterrupt:
                print("Keyboard interrupt received, stopping test")
                TObj.stop()
        else:
            print(f"Unsupported test_type: {test_type}")
            return

    else:
        kwargs = {}
        for field in CustomTestSettings.__annotations__.keys():
            val = getattr(args, field, None)
            if val is not None:
                kwargs[field] = val
        settings = CustomTestSettings(**kwargs)

        TObj = TestTypes(multimeter_mode, args.debug, ps_resource, el_resource, mm_resource)
        thread = TObj.run_custom_test(settings)
        try:
            while thread.is_alive():
                thread.join(0.5)
        except KeyboardInterrupt:
            print("Keyboard interrupt received, stopping test")
            TObj.stop()


if __name__ == "__main__":
    main()
    
# This allows running the script directly from the command line

# Example usage:
# python MAIN.py --actual-capacity-test --capacity-charge-current 4.6 --capacity-discharge-current 46 --multimeter-mode tcouple
# python MAIN.py --actual-capacity-test --config-file profiles.json -d
