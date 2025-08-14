"""Shared default configuration values for safety limits.

This module centralises fallback values used across the project so that
`MAIN.py` and `AlIonBatteryTestSoftware.py` reference a single source of
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


__all__ = ["DEFAULT_LIMITS"]

