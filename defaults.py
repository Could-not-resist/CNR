"""Shared default configuration values for safety limits.

This module centralises fallback values used across the project so that
`main.py` and `al_ion_battery_test_software.py` reference a single source of
truth. Importing from here keeps the defaults consistent should they need
to be updated in the future.
"""

from typing import TypedDict


class LimitDefaults(TypedDict):
    """Type definition for default safety limits."""

    CHARGE_VOLT_PROT: int
    CHARGE_CURRENT_PROT: int
    CHARGE_POWER_PROT: int
    CHARGE_VOLT_END: float
    CHARGE_CURRENT_MAX: float
    SLEW_VOLT: float
    SLEW_CURRENT: float


DEFAULT_LIMITS: LimitDefaults = {
    "CHARGE_VOLT_PROT": 10,  # V
    "CHARGE_CURRENT_PROT": 100,  # A
    "CHARGE_POWER_PROT": 2000,  # W
    "CHARGE_VOLT_END": 4.1,  # V
    "CHARGE_CURRENT_MAX": 5.0,  # A
    "SLEW_VOLT": 0.1,  # V/ms
    "SLEW_CURRENT": 0.1,  # A/ms
}


class TestDefaults(TypedDict):
    """Type definition for general test parameter defaults."""

    CHARGE_VOLT_START: float
    DCHARGE_VOLT_MIN: float
    DCHARGE_CURRENT_MAX: float
    LEADIN_TIME: int
    CHARGE_TIME: int
    DCHARGE_TIME: int
    REST_TIME: int
    NUM_CYCLES: int
    TEST_NAME: str
    TEMPERATURE: float


DEFAULT_TEST_PARAMS: TestDefaults = {
    "CHARGE_VOLT_START": 4.1,  # V
    "DCHARGE_VOLT_MIN": 2.75,  # V
    "DCHARGE_CURRENT_MAX": 20,  # A
    "LEADIN_TIME": 1,  # s
    "CHARGE_TIME": 5,  # s
    "DCHARGE_TIME": 5,  # s
    "REST_TIME": 0,  # s
    "NUM_CYCLES": 1,
    "TEST_NAME": "YUASA",
    "TEMPERATURE": 23.4,  # °C
}


# Default time interval between each measurement in seconds
DEFAULT_SAMPLE_INTERVAL: float = 0.2


__all__ = ["DEFAULT_LIMITS", "DEFAULT_TEST_PARAMS", "DEFAULT_SAMPLE_INTERVAL"]

