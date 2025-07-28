from dataclasses import dataclass
import argparse
from AlIonBatteryTestSoftware import TestController

# Charge/discharge voltage and current limits
CHARGE_VOLT_START: float = 16.21    # V
CHARGE_VOLT_END: float = 16.4    # V
CHARGE_CURRENT_MAX: float = 5.0    # A

DCHARGE_VOLT_MIN: float = 11.0    # V
DCHARGE_CURRENT_MAX: float = 1    # 

CHARGE_VOLT_PROT: int = 20    # V
CHARGE_CURRENT_PROT: int = 10    # A
CHARGE_POWER_PROT: int = 2000    # Watts


# Slew (ramp) settings
SLEW_VOLT: float = 0.1    # V/ms
SLEW_CURRENT: float = 0.1    # A/ms

# Timing (in seconds)
LEADIN_TIME: int = 1    # s #TODO: fix the implementation of leadin time
CHARGE_TIME: int = 5    # s
DCHARGE_TIME: int = 5   # s

# Cycling
NUM_CYCLES: int = 1   # n

# Misc
TEST_NAME: str = "LG"
TEMPERATURE: float = 27.0    # °C


@dataclass
class UPSSettings:
    """Configuration for a UPS test run."""

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
    num_cycles: int = NUM_CYCLES


class TestTypes:
    def __init__(self):
        self.testController = TestController()

    def runUPSTest(self, settings: UPSSettings):
        """Start a UPS test using the provided settings."""
        import threading
        self.testController.event.clear()
        self.upsThread = threading.Thread(
            target=self.testController.NEWupsTest,
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
                settings.num_cycles,
            ),
        )
        self.upsThread.start()


def main():
    parser = argparse.ArgumentParser(description="Run UPS test")
    parser.add_argument("--test-name", default=TEST_NAME)
    parser.add_argument("--temperature", type=float, default=TEMPERATURE)
    parser.add_argument("--charge-volt-prot", type=int, default=CHARGE_VOLT_PROT)
    parser.add_argument("--charge-current-prot", type=int, default=CHARGE_CURRENT_PROT)
    parser.add_argument("--charge-power-prot", type=int, default=CHARGE_POWER_PROT)
    parser.add_argument("--charge-volt-start", type=float, default=CHARGE_VOLT_START)
    parser.add_argument("--charge-volt-end", type=float, default=CHARGE_VOLT_END)
    parser.add_argument("--charge-current-max", type=float, default=CHARGE_CURRENT_MAX)
    parser.add_argument("--dcharge-volt-min", type=float, default=DCHARGE_VOLT_MIN)
    parser.add_argument("--dcharge-current-max", type=float, default=DCHARGE_CURRENT_MAX)
    parser.add_argument("--slew-volt", type=float, default=SLEW_VOLT)
    parser.add_argument("--slew-current", type=float, default=SLEW_CURRENT)
    parser.add_argument("--leadin-time", type=int, default=LEADIN_TIME)
    parser.add_argument("--charge-time", type=int, default=CHARGE_TIME)
    parser.add_argument("--dcharge-time", type=int, default=DCHARGE_TIME)
    parser.add_argument("--num-cycles", type=int, default=NUM_CYCLES)
    parser.add_argument("--actual-capacity-test", action="store_true",
                        help="run actual capacity test")
    parser.add_argument("--capacity-current", type=float, default=1.0,
                        help="1C current in amperes")
    parser.add_argument("--efficiency-test", action="store_true",
                        help="run efficiency test")
    parser.add_argument("--rate-characteristic-test", action="store_true",
                        help="run rate characteristic test")
    parser.add_argument("--ocv-curve-test", action="store_true",
                        help="run OCV curve test")
    parser.add_argument("--internal-resistance-test", action="store_true",
                        help="run internal resistance test")
    parser.add_argument("--rates", default="1.0,0.5,0.2",
                        help="comma separated discharge rates in A")
    parser.add_argument("--step-current", type=float, default=1.0,
                        help="step current for OCV curve")
    parser.add_argument("--steps", type=int, default=10,
                        help="number of steps for OCV curve")
    parser.add_argument("--pulse-current", type=float, default=1.0,
                        help="pulse current for resistance test")
    parser.add_argument("--pulse-duration", type=float, default=1.0,
                        help="pulse duration in seconds")

    args = parser.parse_args()

    if args.actual_capacity_test:
        tc = TestController()
        tc.actual_capacity_test(args.capacity_current, args.temperature)
    elif args.efficiency_test:
        tc = TestController()
        tc.efficiency_test(
            args.charge_current_max,
            args.dcharge_current_max,
            args.charge_volt_end,
            args.dcharge_volt_min,
            args.temperature,
        )
    elif args.rate_characteristic_test:
        rates = [float(r) for r in args.rates.split(',') if r]
        tc = TestController()
        tc.rate_characteristic_test(
            rates,
            args.charge_current_max,
            args.charge_volt_end,
            args.dcharge_volt_min,
            args.temperature,
        )
    elif args.ocv_curve_test:
        tc = TestController()
        tc.ocv_curve_test(
            args.step_current,
            args.steps,
            1800.0,
            args.temperature,
        )
    elif args.internal_resistance_test:
        tc = TestController()
        tc.internal_resistance_test(
            args.pulse_current,
            args.pulse_duration,
            args.temperature,
        )
    else:
        settings = UPSSettings(
            test_name=args.test_name,
            temperature=args.temperature,
            charge_volt_prot=args.charge_volt_prot,
            charge_current_prot=args.charge_current_prot,
            charge_power_prot=args.charge_power_prot,
            charge_volt_start=args.charge_volt_start,
            charge_volt_end=args.charge_volt_end,
            charge_current_max=args.charge_current_max,
            dcharge_volt_min=args.dcharge_volt_min,
            dcharge_current_max=args.dcharge_current_max,
            slew_volt=args.slew_volt,
            slew_current=args.slew_current,
            leadin_time=args.leadin_time,
            charge_time=args.charge_time,
            dcharge_time=args.dcharge_time,
            num_cycles=args.num_cycles,
        )

        TObj = TestTypes()
        TObj.runUPSTest(settings)


if __name__ == "__main__":
    main()
