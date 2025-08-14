#!/usr/bin/env python3
"""Interactive helper to create UPS and capacity test configuration files.

The generated JSON file uses the following structure:
{
  "ups_settings": {...},
  "capacity_test": {...}
}
"""

import json
from pathlib import Path
from typing import Callable, Any

# Default UPS settings matching MAIN.py constants
UPS_DEFAULTS = {
    "test_name": "YUASA",
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
UPS_RANGES = {
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
    "multimeter_mode": None,
}

CAPACITY_RANGES = {
    "rest_time": (0, 86400),
    "charge_voltage": (0, 1000),
    "min_voltage": (0, 1000),
    "charge_current": (0, 1000),
    "finish_current": (0, 1000),
    "discharge_current": (0, 1000),
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


def build_ups_settings() -> dict:
    """Collect UPS settings from the user with range validation."""
    ups = {}
    for field, default in UPS_DEFAULTS.items():
        if isinstance(default, (int, float)):
            minimum, maximum = UPS_RANGES.get(field, (0, 1e9))
            caster = int if isinstance(default, int) and not isinstance(default, bool) else float
            ups[field] = _prompt_number(field, caster, default=default, minimum=minimum, maximum=maximum)
        else:
            val = input(f"{field} [{default if default is not None else 'none'}]: ")
            ups[field] = val if val else default
    return ups


def build_capacity_settings() -> dict:
    """Collect capacity test parameters from the user."""
    cap = {}
    for field, default in CAPACITY_DEFAULTS.items():
        if field == "multimeter_mode":
            val = input(f"{field} [{default if default else 'none'}]: ")
            cap[field] = val if val else default
            continue
        minimum, maximum = CAPACITY_RANGES[field]
        cap[field] = _prompt_number(field, float, default=default, minimum=minimum, maximum=maximum)
    return cap


def main() -> None:
    print("Enter UPS settings:")
    ups_settings = build_ups_settings()
    print("\nEnter capacity test parameters:")
    capacity_settings = build_capacity_settings()
    config = {"ups_settings": ups_settings, "capacity_test": capacity_settings}
    print("\nGenerated configuration:")
    print(json.dumps(config, indent=2))
    filename = input("\nSave under configs/ as (without extension): ").strip() or "test_config"
    path = Path("configs") / f"{filename}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(config, indent=2))
    print(f"Configuration saved to {path}")


if __name__ == "__main__":
    main()
