#!/usr/bin/env python3
"""Interactive helper to build test configuration profiles.

The tool asks for a ``test_name`` and a ``test_type`` such as
``custom``, ``actual_capacity_test`` or ``efficiency_test``.  It then
    prompts only for the parameters relevant to that test and writes a JSON
    snippet compatible with ``profiles.json`` using the format::

    {
      "test_type": "custom",
      "parameters": {
        "test_name": "...",
        ...
      }
    }
"""

import json
from pathlib import Path
from typing import Callable, Any
from defaults import DEFAULT_LIMITS, DEFAULT_TEST_PARAMS

# Default custom test settings matching MAIN.py constants
DEFAULT_TEST_NAME = DEFAULT_TEST_PARAMS["TEST_NAME"]

# Multimeter mode options
MULTIMETER_CHOICES = ("voltage", "tcouple")
MULTIMETER_DEFAULT = "tcouple"

CUSTOM_DEFAULTS = {
    "temperature": DEFAULT_TEST_PARAMS["TEMPERATURE"],
    "charge_volt_prot": DEFAULT_LIMITS["CHARGE_VOLT_PROT"],
    "charge_current_prot": DEFAULT_LIMITS["CHARGE_CURRENT_PROT"],
    "charge_power_prot": DEFAULT_LIMITS["CHARGE_POWER_PROT"],
    "charge_volt_start": DEFAULT_TEST_PARAMS["CHARGE_VOLT_START"],
    "charge_volt_end": DEFAULT_LIMITS["CHARGE_VOLT_END"],
    "charge_current_max": DEFAULT_LIMITS["CHARGE_CURRENT_MAX"],
    "dcharge_volt_min": DEFAULT_TEST_PARAMS["DCHARGE_VOLT_MIN"],
    "dcharge_current_max": DEFAULT_TEST_PARAMS["DCHARGE_CURRENT_MAX"],
    "slew_volt": DEFAULT_LIMITS["SLEW_VOLT"],
    "slew_current": DEFAULT_LIMITS["SLEW_CURRENT"],
    "leadin_time": DEFAULT_TEST_PARAMS["LEADIN_TIME"],
    "charge_time": DEFAULT_TEST_PARAMS["CHARGE_TIME"],
    "dcharge_time": DEFAULT_TEST_PARAMS["DCHARGE_TIME"],
    "num_cycles": DEFAULT_TEST_PARAMS["NUM_CYCLES"],
}

# Ranges for validation
CUSTOM_RANGES = {
    "temperature": (-50, 150),
    "charge_volt_prot": (0, 1000),
    "charge_current_prot": (0, 1000),
    "charge_power_prot": (0, 100000),
    "charge_volt_start": (0, 1000),
    "charge_volt_end": (0, 1000),
    "charge_current_max": (0, 1000),
    "dcharge_volt_min": (0, 1000),
    "dcharge_current_max": (0, 1000),
    "slew_volt": (0, 1000),
    "slew_current": (0, 1000),
    "leadin_time": (0, 86400),
    "charge_time": (0, 86400),
    "dcharge_time": (0, 86400),
    "num_cycles": (1, 100000),
}

CAPACITY_DEFAULTS = {
    "rest_time": 60.0,
    "charge_voltage": DEFAULT_LIMITS["CHARGE_VOLT_END"],
    "min_voltage": DEFAULT_TEST_PARAMS["DCHARGE_VOLT_MIN"],
    "charge_current": 1.0,
    "finish_current": 1.5,
    "discharge_current": 1.0,
}

CAPACITY_RANGES = {
    "rest_time": (0, 86400),
    "charge_voltage": (0, 1000),
    "min_voltage": (0, 1000),
    "charge_current": (0, 1000),
    "finish_current": (0, 1000),
    "discharge_current": (0, 1000),
}

EFFICIENCY_DEFAULTS = {
    "charge_current": 1.0,
    "discharge_current": 1.0,
    "charge_voltage": DEFAULT_LIMITS["CHARGE_VOLT_END"],
    "discharge_voltage": DEFAULT_TEST_PARAMS["DCHARGE_VOLT_MIN"],
    "temperature": DEFAULT_TEST_PARAMS["TEMPERATURE"],
}

EFFICIENCY_RANGES = {
    "charge_current": (0, 1000),
    "discharge_current": (0, 1000),
    "charge_voltage": (0, 1000),
    "discharge_voltage": (0, 1000),
    "temperature": (-50, 150),
}

RATE_DEFAULTS = {
    "discharge_currents": [1.0, 0.5, 0.2],
    "charge_current": 1.0,
    "charge_voltage": DEFAULT_LIMITS["CHARGE_VOLT_END"],
    "discharge_voltage": DEFAULT_TEST_PARAMS["DCHARGE_VOLT_MIN"],
    "temperature": DEFAULT_TEST_PARAMS["TEMPERATURE"],
}

RATE_RANGES = {
    "charge_current": (0, 1000),
    "charge_voltage": (0, 1000),
    "discharge_voltage": (0, 1000),
    "temperature": (-50, 150),
}

OCV_DEFAULTS = {
    "step_current": 1.0,
    "steps": 10,
    "rest_time": 1800.0,
    "temperature": DEFAULT_TEST_PARAMS["TEMPERATURE"],
}

OCV_RANGES = {
    "step_current": (0, 1000),
    "steps": (1, 1000),
    "rest_time": (0, 86400),
    "temperature": (-50, 150),
}

RESISTANCE_DEFAULTS = {
    "pulse_current": 1.0,
    "pulse_duration": 1.0,
    "temperature": DEFAULT_TEST_PARAMS["TEMPERATURE"],
}

RESISTANCE_RANGES = {
    "pulse_current": (0, 1000),
    "pulse_duration": (0, 86400),
    "temperature": (-50, 150),
}


def _prompt_number(
    prompt: str,
    caster: Callable[[str], Any],
    *,
    default: Any,
    minimum: float,
    maximum: float,
) -> Any:
    """Prompt for a numeric value within ``minimum``..``maximum``."""
    while True:
        raw = input(f"{prompt} [{default}]: ") or str(default)
        try:
            value = caster(raw)
            if value < minimum or value > maximum:
                raise ValueError
            return value
        except ValueError:
            print(f"Enter a value between {minimum} and {maximum}.")


def _prompt_multimeter_mode() -> str:
    """Prompt for a multimeter mode from ``MULTIMETER_CHOICES``."""
    choices = ", ".join(MULTIMETER_CHOICES)
    prompt = f"multimeter_mode ({choices}) [{MULTIMETER_DEFAULT}]: "
    while True:
        mode = input(prompt).strip().lower() or MULTIMETER_DEFAULT
        if mode in MULTIMETER_CHOICES:
            return mode
        print(f"Enter one of: {choices}.")


def build_custom_settings(test_name: str) -> dict[str, Any]:
    """Collect custom test settings from the user with range validation."""
    custom = {"test_name": test_name}
    for field, default in CUSTOM_DEFAULTS.items():
        if isinstance(default, (int, float)):
            minimum, maximum = CUSTOM_RANGES.get(field, (0, 1e9))
            caster = (
                int
                if isinstance(default, int) and not isinstance(default, bool)
                else float
            )
            custom[field] = _prompt_number(
                field,
                caster,
                default=default,
                minimum=minimum,
                maximum=maximum,
            )
        else:
            val = input(f"{field} [{default if default is not None else 'none'}]: ")
            custom[field] = val if val else default
    custom["multimeter_mode"] = _prompt_multimeter_mode()
    return custom


def build_capacity_settings(test_name: str) -> dict[str, Any]:
    """Collect parameters for ``actual_capacity_test``."""
    cap = {"test_name": test_name}
    for field, default in CAPACITY_DEFAULTS.items():
        minimum, maximum = CAPACITY_RANGES[field]
        cap[field] = _prompt_number(
            field,
            float,
            default=default,
            minimum=minimum,
            maximum=maximum,
        )
    cap["multimeter_mode"] = _prompt_multimeter_mode()
    return cap


def build_efficiency_settings(test_name: str) -> dict[str, Any]:
    """Collect parameters for ``efficiency_test``."""
    eff = {"test_name": test_name}
    for field, default in EFFICIENCY_DEFAULTS.items():
        minimum, maximum = EFFICIENCY_RANGES[field]
        eff[field] = _prompt_number(
            field,
            float,
            default=default,
            minimum=minimum,
            maximum=maximum,
        )
    eff["multimeter_mode"] = _prompt_multimeter_mode()
    return eff


def build_rate_settings(test_name: str) -> dict[str, Any]:
    """Collect parameters for ``rate_characteristic_test``."""
    rate = {"test_name": test_name}
    default_rates = ",".join(str(r) for r in RATE_DEFAULTS["discharge_currents"])
    raw = input(f"discharge_currents comma separated [{default_rates}]: ") or default_rates
    try:
        currents = [float(x) for x in raw.split(",") if x.strip()]
    except ValueError:
        print("Invalid input, using defaults")
        currents = RATE_DEFAULTS["discharge_currents"]
    rate["discharge_currents"] = currents
    for field in (
        "charge_current",
        "charge_voltage",
        "discharge_voltage",
        "temperature",
    ):
        default = RATE_DEFAULTS[field]
        minimum, maximum = RATE_RANGES[field]
        rate[field] = _prompt_number(
            field,
            float,
            default=default,
            minimum=minimum,
            maximum=maximum,
        )
    rate["multimeter_mode"] = _prompt_multimeter_mode()
    return rate


def build_ocv_settings(test_name: str) -> dict[str, Any]:
    """Collect parameters for ``ocv_curve_test``."""
    ocv = {"test_name": test_name}
    ocv["step_current"] = _prompt_number(
        "step_current",
        float,
        default=OCV_DEFAULTS["step_current"],
        minimum=OCV_RANGES["step_current"][0],
        maximum=OCV_RANGES["step_current"][1],
    )
    ocv["steps"] = _prompt_number(
        "steps",
        int,
        default=OCV_DEFAULTS["steps"],
        minimum=OCV_RANGES["steps"][0],
        maximum=OCV_RANGES["steps"][1],
    )
    ocv["rest_time"] = _prompt_number(
        "rest_time",
        float,
        default=OCV_DEFAULTS["rest_time"],
        minimum=OCV_RANGES["rest_time"][0],
        maximum=OCV_RANGES["rest_time"][1],
    )
    ocv["temperature"] = _prompt_number(
        "temperature",
        float,
        default=OCV_DEFAULTS["temperature"],
        minimum=OCV_RANGES["temperature"][0],
        maximum=OCV_RANGES["temperature"][1],
    )
    ocv["multimeter_mode"] = _prompt_multimeter_mode()
    return ocv


def build_resistance_settings(test_name: str) -> dict[str, Any]:
    """Collect parameters for ``internal_resistance_test``."""
    res = {"test_name": test_name}
    for field, default in RESISTANCE_DEFAULTS.items():
        minimum, maximum = RESISTANCE_RANGES[field]
        res[field] = _prompt_number(
            field,
            float,
            default=default,
            minimum=minimum,
            maximum=maximum,
        )
    res["multimeter_mode"] = _prompt_multimeter_mode()
    return res


def main() -> None:
    test_name = input(f"test_name [{DEFAULT_TEST_NAME}]: ").strip() or DEFAULT_TEST_NAME
    test_type = (
        input(
            "Test type (custom, actual_capacity_test, efficiency_test, rate_characteristic_test, ocv_curve_test, internal_resistance_test) [custom]: "
        )
        .strip()
        .lower()
        or "custom"
    )

    builders = {
        "custom": build_custom_settings,
        "actual_capacity_test": build_capacity_settings,
        "efficiency_test": build_efficiency_settings,
        "rate_characteristic_test": build_rate_settings,
        "ocv_curve_test": build_ocv_settings,
        "internal_resistance_test": build_resistance_settings,
    }
    builder = builders.get(test_type)
    if builder is None:
        print(f"Unsupported test type: {test_type}")
        return

    print(f"Enter {test_type} parameters:")
    params = builder(test_name)
    config = {"test_type": test_type, "parameters": params}

    print("\nGenerated configuration:")
    print(json.dumps(config, indent=2))
    profiles = Path("profiles.json")
    if profiles.exists():
        data = json.loads(profiles.read_text())
    else:
        data = {}
    data[test_name] = config
    profiles.write_text(json.dumps(data, indent=2))
    print(f"Configuration saved to {profiles}")


if __name__ == "__main__":
    main()
