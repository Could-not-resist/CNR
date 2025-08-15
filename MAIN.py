"""Command line interface for running battery tests.

Command-line test type flags (e.g., ``--efficiency-test``) take priority
over the ``test_type`` defined in a profile.
"""

from dataclasses import dataclass
import argparse
import json
import logging
import os
from pathlib import Path
from typing import Any
from defaults import (
    DEFAULT_LIMITS,
    DEFAULT_TEST_PARAMS,
    DEFAULT_SAMPLE_INTERVAL,
)


logger = logging.getLogger(__name__)


@dataclass
class CustomTestSettings:
    """Configuration for a custom test run."""

    test_name: str = DEFAULT_TEST_PARAMS["TEST_NAME"]
    temperature: float = DEFAULT_TEST_PARAMS["TEMPERATURE"]
    charge_volt_prot: int = DEFAULT_LIMITS["CHARGE_VOLT_PROT"]
    charge_current_prot: int = DEFAULT_LIMITS["CHARGE_CURRENT_PROT"]
    charge_power_prot: int = DEFAULT_LIMITS["CHARGE_POWER_PROT"]
    charge_volt_start: float = DEFAULT_TEST_PARAMS["CHARGE_VOLT_START"]
    charge_volt_end: float = DEFAULT_LIMITS["CHARGE_VOLT_END"]
    charge_current_max: float = DEFAULT_LIMITS["CHARGE_CURRENT_MAX"]
    dcharge_volt_min: float = DEFAULT_TEST_PARAMS["DCHARGE_VOLT_MIN"]
    dcharge_current_max: float = DEFAULT_TEST_PARAMS["DCHARGE_CURRENT_MAX"]
    slew_volt: float = DEFAULT_LIMITS["SLEW_VOLT"]
    slew_current: float = DEFAULT_LIMITS["SLEW_CURRENT"]
    leadin_time: int = DEFAULT_TEST_PARAMS["LEADIN_TIME"]
    charge_time: int = DEFAULT_TEST_PARAMS["CHARGE_TIME"]
    dcharge_time: int = DEFAULT_TEST_PARAMS["DCHARGE_TIME"]
    rest_time: int = DEFAULT_TEST_PARAMS["REST_TIME"]
    num_cycles: int = DEFAULT_TEST_PARAMS["NUM_CYCLES"]
    charge_mode: str = "CC"
    discharge_mode: str = "CC"
    sample_interval: float = DEFAULT_SAMPLE_INTERVAL
    multimeter_mode: str = "tcouple"



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
        logger.error("Configuration file not found: %s", config_path)
        return {}, {}, None, {}
    except json.JSONDecodeError as exc:
        logger.error(
            "Error decoding JSON from %s: %s (line %s column %s char %s)",
            config_path,
            exc.msg,
            exc.lineno,
            exc.colno,
            exc.pos,
        )
        return {}, {}, None, {}

    if not isinstance(data, dict):
        return {}, {}, None, {}

    if profile not in data:
        raise KeyError(
            f"Profile '{profile}' not found in {config_path}. "
            "Run --list-profiles to see available profiles."
        )

    profile_data = data[profile]
    if not isinstance(profile_data, dict):
        return (
            {},
            data.get("capacity_defaults", {}),
            None,
            data.get("required_keys", {}),
        )

    test_type = profile_data.get("test_type")
    return (
        profile_data,
        data.get("capacity_defaults", {}),
        test_type,
        data.get("required_keys", {}),
    )

def validate_required_keys(
    profile: dict, required: dict, test_type: str
) -> None:
    """Raise if profile is missing parameters required by ``test_type``."""
    params = {k: v for k, v in profile.items() if k != "parameters"}
    params.update(profile.get("parameters", {}))
    missing = [k for k in required.get(test_type, []) if k not in params]
    if missing:
        raise KeyError(
            f"Missing required keys for {test_type}: {', '.join(missing)}"
        )


def main():
    """Entry point for the command-line interface.

    Builds an :class:`argparse.ArgumentParser` for test configuration, then
    loads an optional profile from ``profiles.json`` (or ``--config-file``).
    Test parameters are resolved with the following precedence:

    1. Command-line arguments
    2. ``parameters`` section inside the selected profile
    3. Top-level keys of the profile
    4. Fallback values from :mod:`defaults`

    Defaults imported from :mod:`defaults` provide a central source of truth
    for safety limits and test parameters, easing future updates.
    """

    parser = argparse.ArgumentParser(description="Run custom test")
    parser.add_argument(
        "--config-file",
        help="JSON file with cell settings (defaults to profiles.json)",
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List available profiles and exit",
    )
    parser.add_argument("--profile", help="cell profile name in config file")
    parser.add_argument(
        "--ps-resource",
        help="VISA resource name for power supply",
    )
    parser.add_argument(
        "--el-resource",
        help="VISA resource name for electronic load",
    )
    parser.add_argument(
        "--mm-resource",
        help="VISA resource name for multimeter",
    )
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
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument(
        "--actual-capacity-test",
        action="store_true",
        help="run actual capacity test (overrides profile test_type)",
    )
    parser.add_argument(
        "--capacity-charge-current",
        type=float,
        help="charge current for capacity test in amperes",
    )
    parser.add_argument(
        "--capacity-discharge-current",
        type=float,
        help="discharge current for capacity test in amperes",
    )
    parser.add_argument(
        "--capacity-rest-time",
        type=float,
        help="rest time before discharge in seconds",
    )
    parser.add_argument(
        "--capacity-charge-voltage",
        type=float,
        help="charge voltage for capacity test",
    )
    parser.add_argument(
        "--capacity-min-voltage",
        type=float,
        help="minimum discharge voltage for capacity test",
    )
    parser.add_argument(
        "--capacity-finish-current",
        type=float,
        help="current threshold to end charging during capacity test",
    )
    test_group.add_argument(
        "--efficiency-test",
        action="store_true",
        help="run efficiency test (overrides profile test_type)",
    )
    test_group.add_argument(
        "--rate-characteristic-test",
        action="store_true",
        help="run rate characteristic test (overrides profile test_type)",
    )
    test_group.add_argument(
        "--ocv-curve-test",
        action="store_true",
        help="run OCV curve test (overrides profile test_type)",
    )
    test_group.add_argument(
        "--internal-resistance-test",
        action="store_true",
        help=(
            "run internal resistance test (no capacity measurement) "
            "and override profile test_type"
        ),
    )
    parser.add_argument(
        "--rates",
        default="1.0,0.5,0.2",
        help="comma separated discharge rates in A",
    )
    parser.add_argument(
        "--step-current",
        type=float,
        default=1.0,
        help="step current for OCV curve",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=10,
        help="number of steps for OCV curve",
    )
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
        help=(
            "log measurement with multimeter (voltage or thermocouple, "
            "default: tcouple)"
        ),
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
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="set logging verbosity (default: INFO)",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()), format="%(message)s"
    )

    if args.list_profiles:
        config_path = args.config_file or "profiles.json"
        try:
            data = json.loads(Path(config_path).read_text())
        except FileNotFoundError as exc:
            logger.error("Error reading %s: %s", config_path, exc)
            return
        except json.JSONDecodeError as exc:
            logger.error(
                "Error decoding JSON from %s: %s (line %s column %s char %s)",
                config_path,
                exc.msg,
                exc.lineno,
                exc.colno,
                exc.pos,
            )
            return
        for name in data:
            if name not in {"capacity_defaults", "required_keys"}:
                logger.info(name)
        return

    profile = args.profile
    config: dict = {}
    test_type = None
    required_keys: dict = {}
    capacity_defaults: dict[str, Any] = {}
    config_file = args.config_file
    if profile:
        if not config_file:
            config_file = "profiles.json"
        try:
            config, capacity_defaults, test_type, required_keys = load_config(
                config_file, profile
            )
        except KeyError as exc:
            logger.error(exc)
            return
        if test_type and required_keys:
            try:
                validate_required_keys(config, required_keys, test_type)
            except KeyError as exc:
                logger.error(exc)
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

    def resolve_multimeter_mode() -> str:
        """Return validated multimeter mode.

        Resolution order:
        1. Command line argument
        2. Profile's "parameters" section
        3. Top level of the profile
        4. ``capacity_defaults`` mapping
        5. Default "tcouple"
        """
        mode = args.multimeter_mode
        if mode is None:
            mode = params_section.get("multimeter_mode")
        if mode is None:
            mode = config.get("multimeter_mode")
        if mode is None:
            mode = capacity_defaults.get("multimeter_mode")
        if mode is None:
            mode = "tcouple"
        if mode not in {"voltage", "tcouple"}:
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
    # Argparse's mutually exclusive group ensures only one of these flags can be
    # provided. Command-line flags override the ``test_type`` loaded from a
    # profile.
    resolved_test_type = next(
        (t for t, flag in cli_flags.items() if flag),
        None,
    )
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

    def build_actual_capacity_params() -> dict[str, Any]:
        return {
            "charge_current_1c": resolve_param(
                "capacity_charge_current",
                "capacity_charge_current",
                capacity_defaults.get("charge_current", 1.0),
            ),
            "discharge_current_1c": resolve_param(
                "capacity_discharge_current",
                "capacity_discharge_current",
                capacity_defaults.get("discharge_current", 1.0),
            ),
            "rest_time": resolve_param(
                "capacity_rest_time",
                "capacity_rest_time",
                capacity_defaults.get("rest_time", 3600.0),
            ),
            "charge_voltage": resolve_param(
                "capacity_charge_voltage",
                "capacity_charge_voltage",
                capacity_defaults.get(
                    "charge_voltage",
                    DEFAULT_LIMITS["CHARGE_VOLT_END"],
                ),
            ),
            "min_voltage": resolve_param(
                "capacity_min_voltage",
                "capacity_min_voltage",
                capacity_defaults.get(
                    "min_voltage",
                    DEFAULT_TEST_PARAMS["DCHARGE_VOLT_MIN"],
                ),
            ),
            "temperature": resolve_param(
                "temperature",
                "temperature",
                capacity_defaults.get(
                    "temperature",
                    DEFAULT_TEST_PARAMS["TEMPERATURE"],
                ),
            ),
            "finish_current": resolve_param(
                "capacity_finish_current",
                "capacity_finish_current",
                capacity_defaults.get("finish_current", 1.5),
            ),
        }

    def build_efficiency_params() -> dict[str, Any]:
        return {
            "charge_current": resolve_param(
                "charge_current_max",
                "charge_current_max",
                DEFAULT_LIMITS["CHARGE_CURRENT_MAX"],
            ),
            "discharge_current": resolve_param(
                "dcharge_current_max",
                "dcharge_current_max",
                DEFAULT_TEST_PARAMS["DCHARGE_CURRENT_MAX"],
            ),
            "charge_voltage": resolve_param(
                "charge_volt_end",
                "charge_volt_end",
                DEFAULT_LIMITS["CHARGE_VOLT_END"],
            ),
            "discharge_voltage": resolve_param(
                "dcharge_volt_min",
                "dcharge_volt_min",
                DEFAULT_TEST_PARAMS["DCHARGE_VOLT_MIN"],
            ),
            "temperature": resolve_param(
                "temperature",
                "temperature",
                DEFAULT_TEST_PARAMS["TEMPERATURE"],
            ),
        }

    def build_rate_params() -> dict[str, Any]:
        rates_val = resolve_param("rates", "rates", "1.0,0.5,0.2")
        if isinstance(rates_val, str):
            rates = [float(r) for r in rates_val.split(",") if r]
        else:
            rates = [float(r) for r in rates_val]
        return {
            "discharge_currents": rates,
            "charge_current": resolve_param(
                "charge_current_max",
                "charge_current_max",
                DEFAULT_LIMITS["CHARGE_CURRENT_MAX"],
            ),
            "charge_voltage": resolve_param(
                "charge_volt_end",
                "charge_volt_end",
                DEFAULT_LIMITS["CHARGE_VOLT_END"],
            ),
            "discharge_voltage": resolve_param(
                "dcharge_volt_min",
                "dcharge_volt_min",
                DEFAULT_TEST_PARAMS["DCHARGE_VOLT_MIN"],
            ),
            "temperature": resolve_param(
                "temperature",
                "temperature",
                DEFAULT_TEST_PARAMS["TEMPERATURE"],
            ),
        }

    def build_ocv_params() -> dict[str, Any]:
        return {
            "step_current": resolve_param(
                "step_current",
                "step_current",
                1.0,
            ),
            "steps": resolve_param(
                "steps",
                "steps",
                10,
            ),
            "rest_time": resolve_param(
                "rest_time",
                "rest_time",
                1800.0,
            ),
            "temperature": resolve_param(
                "temperature",
                "temperature",
                DEFAULT_TEST_PARAMS["TEMPERATURE"],
            ),
        }

    def build_ir_params() -> dict[str, Any]:
        return {
            "pulse_current": resolve_param(
                "pulse_current",
                "pulse_current",
                1.0,
            ),
            "pulse_duration": resolve_param(
                "pulse_duration",
                "pulse_duration",
                1.0,
            ),
            "temperature": resolve_param(
                "temperature",
                "temperature",
                DEFAULT_TEST_PARAMS["TEMPERATURE"],
            ),
        }

    def build_custom_params() -> dict[str, Any]:
        # Apply the same resolution order as ``resolve_param`` so that the CLI
        # can override values from the profile.  "config" is consulted only
        # after ``params_section`` to allow the profile's "parameters" section
        # to take precedence over top level entries.
        kwargs = {}
        for field in CustomTestSettings.__annotations__.keys():
            if field == "multimeter_mode":
                continue
            if field == "test_name" and profile:
                val = None
            else:
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
        "actual_capacity_test": (
            "actual_capacity_test",
            build_actual_capacity_params,
        ),
        "efficiency_test": (
            "efficiency_test",
            build_efficiency_params,
        ),
        "rate_characteristic_test": (
            "rate_characteristic_test",
            build_rate_params,
        ),
        "ocv_curve_test": (
            "ocv_curve_test",
            build_ocv_params,
        ),
        "internal_resistance_test": (
            "internal_resistance_test",
            build_ir_params,
        ),
        "custom": (
            "custom_test",
            build_custom_params,
        ),
    }

    method_name, builder = dispatch.get(resolved_test_type, dispatch["custom"])
    params = builder()
    logger.info("Resolved parameters: %s", params)
    if args.dry_run:
        return

    from AlIonBatteryTestSoftware import TestController
    try:
        from AlIonBatteryTestSoftware import VisaIOError
    except ImportError:  # pragma: no cover - falls back when mock is used
        VisaIOError = Exception
    try:
        tc = TestController(
            multimeter_mode,
            args.debug,
            ps_resource,
            el_resource,
            mm_resource,
        )
    except (SystemExit, ConnectionError, OSError, VisaIOError) as exc:
        print(f"Failed to initialize TestController: {exc}")
        return

    method = getattr(tc, method_name)
    try:
        result = method(**params)
        if resolved_test_type == "actual_capacity_test" and result is not None:
            logger.info("Measured capacity: %.3f Ah", result)
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt received, stopping test")
        tc.abort()


if __name__ == "__main__":
    main()
    
# This allows running the script directly from the command line

# Example usage:
# python MAIN.py --profile YUASA
# python MAIN.py --profile YUASA_ACT1 -d
