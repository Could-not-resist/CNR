"""Command line interface for running battery tests.

Command-line test type flags (e.g., ``--efficiency-test``) take priority
over the ``test_type`` defined in a profile.
"""

from dataclasses import dataclass
import argparse
import json
import os
from pathlib import Path
from pprint import pprint
from defaults import (
    DEFAULT_LIMITS,
    DEFAULT_TEST_PARAMS,
    DEFAULT_SAMPLE_INTERVAL,
)

# Charge/discharge voltage and current limits
CHARGE_VOLT_START: float = DEFAULT_TEST_PARAMS["CHARGE_VOLT_START"]
CHARGE_VOLT_END: float = DEFAULT_LIMITS["CHARGE_VOLT_END"]
CHARGE_CURRENT_MAX: float = DEFAULT_LIMITS["CHARGE_CURRENT_MAX"]

DCHARGE_VOLT_MIN: float = DEFAULT_TEST_PARAMS["DCHARGE_VOLT_MIN"]
DCHARGE_CURRENT_MAX: float = DEFAULT_TEST_PARAMS["DCHARGE_CURRENT_MAX"]

CHARGE_VOLT_PROT: int = DEFAULT_LIMITS["CHARGE_VOLT_PROT"]
CHARGE_CURRENT_PROT: int = DEFAULT_LIMITS["CHARGE_CURRENT_PROT"]
CHARGE_POWER_PROT: int = DEFAULT_LIMITS["CHARGE_POWER_PROT"]


# Slew (ramp) settings
SLEW_VOLT: float = DEFAULT_LIMITS["SLEW_VOLT"]
SLEW_CURRENT: float = DEFAULT_LIMITS["SLEW_CURRENT"]

# Timing (in seconds)
# Ramp duration for increasing the charge voltage from CHARGE_VOLT_START
# to CHARGE_VOLT_END at the beginning of each cycle
LEADIN_TIME: int = DEFAULT_TEST_PARAMS["LEADIN_TIME"]

CHARGE_TIME: int = DEFAULT_TEST_PARAMS["CHARGE_TIME"]
DCHARGE_TIME: int = DEFAULT_TEST_PARAMS["DCHARGE_TIME"]
REST_TIME: int = DEFAULT_TEST_PARAMS["REST_TIME"]

# Cycling
NUM_CYCLES: int = DEFAULT_TEST_PARAMS["NUM_CYCLES"]

# Misc
TEST_NAME: str = DEFAULT_TEST_PARAMS["TEST_NAME"]
TEMPERATURE: float = DEFAULT_TEST_PARAMS["TEMPERATURE"]


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
    sample_interval: float = DEFAULT_SAMPLE_INTERVAL
    multimeter_mode: str | None = None



def load_config(
    config_path: str, profile: str
) -> tuple[dict, dict, str | None, dict]:
    """Load profile configuration, defaults, test type and required keys.

    Raises:
        KeyError: If ``profile`` is missing from the configuration data.
    """
    try:
        data = json.loads(Path(config_path).read_text())
    except FileNotFoundError:
        print(f"Configuration file not found: {config_path}")
        return {}, {}, None, {}
    except json.JSONDecodeError as exc:
        print(f"Error decoding JSON from {config_path}: {exc}")
        return {}, {}, None, {}

    if not isinstance(data, dict):
        return {}, {}, None, {}

    if profile not in data:
        raise KeyError(f"Profile '{profile}' not found in {config_path}")

    profile_data = data[profile]
    if not isinstance(profile_data, dict):
        return {}, data.get("capacity_defaults", {}), None, data.get("required_keys", {})

    test_type = profile_data.get("test_type")
    return (
        profile_data,
        data.get("capacity_defaults", {}),
        test_type,
        data.get("required_keys", {}),
    )


def validate_required_keys(profile: dict, required: dict, test_type: str) -> None:
    """Raise if profile is missing parameters required by ``test_type``."""
    params = {k: v for k, v in profile.items() if k != "parameters"}
    params.update(profile.get("parameters", {}))
    missing = [k for k in required.get(test_type, []) if k not in params]
    if missing:
        raise KeyError(
            f"Missing required keys for {test_type}: {', '.join(missing)}"
        )



class TestTypes:
    def __init__(
        self,
        multimeter_mode: str | None = None,
        debug: bool = False,
        ps_resource: str | None = None,
        el_resource: str | None = None,
        mm_resource: str | None = None,
    ):
        from AlIonBatteryTestSoftware import TestController
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
        "--config-file", help="JSON file with cell settings (defaults to profiles.json)"
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List available profiles and exit",
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
    parser.add_argument(
        "--actual-capacity-test",
        action="store_true",
        help="run actual capacity test (overrides profile test_type)",
    )
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
    parser.add_argument(
        "--efficiency-test",
        action="store_true",
        help="run efficiency test (overrides profile test_type)",
    )
    parser.add_argument(
        "--rate-characteristic-test",
        action="store_true",
        help="run rate characteristic test (overrides profile test_type)",
    )
    parser.add_argument(
        "--ocv-curve-test",
        action="store_true",
        help="run OCV curve test (overrides profile test_type)",
    )
    parser.add_argument(
        "--internal-resistance-test",
        action="store_true",
        help=(
            "run internal resistance test (no capacity measurement) "
            "and override profile test_type"
        ),
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
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show resolved parameters and exit",
    )

    args = parser.parse_args()

    if args.list_profiles:
        config_path = args.config_file or "profiles.json"
        try:
            data = json.loads(Path(config_path).read_text())
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            print(f"Error reading {config_path}: {exc}")
            return
        for name in data:
            if name not in {"capacity_defaults", "required_keys"}:
                print(name)
        return

    profile = args.profile or args.test_name or TEST_NAME
    config: dict = {}
    test_type = None
    required_keys: dict = {}
    config_file = args.config_file
    if args.profile and not config_file:
        config_file = "profiles.json"
    if config_file:
        try:
            config, _, test_type, required_keys = load_config(config_file, profile)
        except KeyError as exc:
            print(exc)
            return
        if test_type and required_keys:
            try:
                validate_required_keys(config, required_keys, test_type)
            except KeyError as exc:
                print(exc)
                return

    params_section = config.get("parameters", {})

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

    def resolve_multimeter_mode() -> str | None:
        """Return validated multimeter mode from CLI, params or config."""
        mode = config.get("multimeter_mode")
        if mode is None:
            mode = params_section.get("multimeter_mode")
        if mode is None:
            mode = args.multimeter_mode
        if mode not in {None, "voltage", "tcouple"}:
            raise ValueError(f"Invalid multimeter_mode: {mode}")
        return mode

    multimeter_mode = resolve_multimeter_mode()

    cli_flags = {
        "actual_capacity_test": args.actual_capacity_test,
        "efficiency_test": args.efficiency_test,
        "rate_characteristic_test": args.rate_characteristic_test,
        "ocv_curve_test": args.ocv_curve_test,
        "internal_resistance_test": args.internal_resistance_test,
    }
    # Command-line flags override the ``test_type`` loaded from a profile
    resolved_test_type = next((t for t, flag in cli_flags.items() if flag), None)
    if resolved_test_type is None:
        resolved_test_type = test_type or "custom"

    def resolve_param(key: str, cli_attr: str, default):
        # Parameter resolution hierarchy:
        # 1. Command line argument
        # 2. Profile's "parameters" section
        # 3. Top level of the profile
        # 4. Hard coded defaults
        # "config" is checked after "params_section" so that values inside the
        # dedicated "parameters" block override broader profile settings.
        val = getattr(args, cli_attr, None)
        if val is None:
            val = params_section.get(key)
        if val is None:
            val = config.get(key)
        if val is None:
            val = default
        return val

    def build_actual_capacity_params():
        return {
            "charge_current_1c": resolve_param(
                "capacity_charge_current", "capacity_charge_current", 1.0
            ),
            "discharge_current_1c": resolve_param(
                "capacity_discharge_current", "capacity_discharge_current", 1.0
            ),
            "rest_time": resolve_param("capacity_rest_time", "capacity_rest_time", 3600.0),
            "charge_voltage": resolve_param(
                "capacity_charge_voltage", "capacity_charge_voltage", CHARGE_VOLT_END
            ),
            "min_voltage": resolve_param(
                "capacity_min_voltage", "capacity_min_voltage", DCHARGE_VOLT_MIN
            ),
            "temperature": resolve_param("temperature", "temperature", TEMPERATURE),
            "finish_current": resolve_param(
                "capacity_finish_current", "capacity_finish_current", 1.5
            ),
        }

    def build_efficiency_params():
        return {
            "charge_current": resolve_param(
                "charge_current_max", "charge_current_max", CHARGE_CURRENT_MAX
            ),
            "discharge_current": resolve_param(
                "dcharge_current_max", "dcharge_current_max", DCHARGE_CURRENT_MAX
            ),
            "charge_voltage": resolve_param(
                "charge_volt_end", "charge_volt_end", CHARGE_VOLT_END
            ),
            "discharge_voltage": resolve_param(
                "dcharge_volt_min", "dcharge_volt_min", DCHARGE_VOLT_MIN
            ),
            "temperature": resolve_param("temperature", "temperature", TEMPERATURE),
        }

    def build_rate_params():
        rates_val = resolve_param("rates", "rates", "1.0,0.5,0.2")
        if isinstance(rates_val, str):
            rates = [float(r) for r in rates_val.split(",") if r]
        else:
            rates = [float(r) for r in rates_val]
        return {
            "discharge_currents": rates,
            "charge_current": resolve_param(
                "charge_current_max", "charge_current_max", CHARGE_CURRENT_MAX
            ),
            "charge_voltage": resolve_param(
                "charge_volt_end", "charge_volt_end", CHARGE_VOLT_END
            ),
            "discharge_voltage": resolve_param(
                "dcharge_volt_min", "dcharge_volt_min", DCHARGE_VOLT_MIN
            ),
            "temperature": resolve_param("temperature", "temperature", TEMPERATURE),
        }

    def build_ocv_params():
        return {
            "step_current": resolve_param("step_current", "step_current", 1.0),
            "steps": resolve_param("steps", "steps", 10),
            "rest_time": resolve_param("rest_time", "rest_time", 1800.0),
            "temperature": resolve_param("temperature", "temperature", TEMPERATURE),
        }

    def build_ir_params():
        return {
            "pulse_current": resolve_param("pulse_current", "pulse_current", 1.0),
            "pulse_duration": resolve_param(
                "pulse_duration", "pulse_duration", 1.0
            ),
            "temperature": resolve_param("temperature", "temperature", TEMPERATURE),
        }

    def build_custom_params():
        # Apply the same resolution order as ``resolve_param`` so that the CLI
        # can override values from the profile.  "config" is consulted only
        # after ``params_section`` to allow the profile's "parameters" section
        # to take precedence over top level entries.
        kwargs = {}
        for field in CustomTestSettings.__annotations__.keys():
            if field == "multimeter_mode":
                continue
            val = getattr(args, field, None)
            if val is None:
                val = params_section.get(field)
            if val is None:
                val = config.get(field)
            if val is not None:
                kwargs[field] = val
        kwargs["multimeter_mode"] = multimeter_mode
        return vars(CustomTestSettings(**kwargs))

    dispatch = {
        "actual_capacity_test": ("actual_capacity_test", build_actual_capacity_params),
        "efficiency_test": ("efficiency_test", build_efficiency_params),
        "rate_characteristic_test": ("rate_characteristic_test", build_rate_params),
        "ocv_curve_test": ("ocv_curve_test", build_ocv_params),
        "internal_resistance_test": ("internal_resistance_test", build_ir_params),
        "custom": ("custom_test", build_custom_params),
    }

    method_name, builder = dispatch.get(resolved_test_type, dispatch["custom"])
    params = builder()
    pprint(params)
    if args.dry_run:
        return

    from AlIonBatteryTestSoftware import TestController
    tc = TestController(
        multimeter_mode, args.debug, ps_resource, el_resource, mm_resource
    )
    method = getattr(tc, method_name)
    try:
        result = method(**params)
        if resolved_test_type == "actual_capacity_test" and result is not None:
            print(f"Measured capacity: {result:.3f} Ah")
    except KeyboardInterrupt:
        print("Keyboard interrupt received, stopping test")
        tc.abort()


if __name__ == "__main__":
    main()
    
# This allows running the script directly from the command line

# Example usage:
# python MAIN.py --profile YUASA
# python MAIN.py --profile YUASA_ACT1 -d
