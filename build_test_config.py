#!/usr/bin/env python3
"""Interactive helper to build test configuration profiles.

The tool asks for a ``test_name`` and a ``test_type`` such as
``custom``, ``actual_capacity_test`` or ``efficiency_test``.  It then
prompts only for the parameters relevant to that test and writes a JSON
snippet compatible with ``cell_profiles.json`` using the format::

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

# Default custom test settings matching MAIN.py constants
DEFAULT_TEST_NAME = "YUASA"
CUSTOM_DEFAULTS = {
    "temperature": 23.4,
    "charge_volt_prot": 10,
    "charge_current_prot": 100,
    "charge_power_prot": 2000,
    "charge_volt_start": 4.1,
    "charge_volt_end": 4.1,
    "charge_current_max": 5.0,
    "dcharge_volt_min": 2.75,
    "dcharge_current_max": 20.0,
    "slew_volt": 0.1,
    "slew_current": 0.1,
    "leadin_time": 1,
    "charge_time": 5,
    "dcharge_time": 5,
    "num_cycles": 1,
    "multimeter_mode": None,
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
    "charge_voltage": 4.1,
    "min_voltage": 2.75,
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
    "charge_voltage": 4.1,
    "discharge_voltage": 2.75,
    "temperature": 20.0,
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
    "charge_voltage": 4.1,
    "discharge_voltage": 2.75,
    "temperature": 20.0,
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
    "temperature": 20.0,
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
    "temperature": 20.0,
}

RESISTANCE_RANGES = {
    "pulse_current": (0, 1000),
    "pulse_duration": (0, 86400),
    "temperature": (-50, 150),
}


def _prompt_number(prompt: str, caster: Callable[[str], Any], *, default: Any, minimum: float, maximum: float) -> Any:
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


def build_custom_settings(test_name: str) -> dict:
    """Collect custom test settings from the user with range validation."""
    custom = {"test_name": test_name}
    for field, default in CUSTOM_DEFAULTS.items():
        if isinstance(default, (int, float)):
            minimum, maximum = CUSTOM_RANGES.get(field, (0, 1e9))
            caster = int if isinstance(default, int) and not isinstance(default, bool) else float
            custom[field] = _prompt_number(field, caster, default=default, minimum=minimum, maximum=maximum)
        else:
            val = input(f"{field} [{default if default is not None else 'none'}]: ")
            custom[field] = val if val else default
    return custom


def build_capacity_settings(test_name: str) -> dict:
    """Collect parameters for ``actual_capacity_test``."""
    cap = {"test_name": test_name}
    for field, default in CAPACITY_DEFAULTS.items():
        minimum, maximum = CAPACITY_RANGES[field]
        cap[field] = _prompt_number(field, float, default=default, minimum=minimum, maximum=maximum)
    return cap


def build_efficiency_settings(test_name: str) -> dict:
    """Collect parameters for ``efficiency_test``."""
    eff = {"test_name": test_name}
    for field, default in EFFICIENCY_DEFAULTS.items():
        minimum, maximum = EFFICIENCY_RANGES[field]
        eff[field] = _prompt_number(field, float, default=default, minimum=minimum, maximum=maximum)
    return eff


def build_rate_settings(test_name: str) -> dict:
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
    for field in ("charge_current", "charge_voltage", "discharge_voltage", "temperature"):
        default = RATE_DEFAULTS[field]
        minimum, maximum = RATE_RANGES[field]
        rate[field] = _prompt_number(field, float, default=default, minimum=minimum, maximum=maximum)
    return rate


def build_ocv_settings(test_name: str) -> dict:
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
    return ocv


def build_resistance_settings(test_name: str) -> dict:
    """Collect parameters for ``internal_resistance_test``."""
    res = {"test_name": test_name}
    for field, default in RESISTANCE_DEFAULTS.items():
        minimum, maximum = RESISTANCE_RANGES[field]
        res[field] = _prompt_number(field, float, default=default, minimum=minimum, maximum=maximum)
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
    filename = input("\nSave under configs/ as (without extension): ").strip() or "test_config"
    path = Path("configs") / f"{filename}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(config, indent=2))
    print(f"Configuration saved to {path}")


if __name__ == "__main__":
    main()
