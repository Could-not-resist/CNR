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


class TestTypes:
    def __init__(self):
        self.testController = TestController()

    def runUPSTest(self,Test_Name: str,Temperature:float,Charge_volt_prot:int,Charge_current_prot:int,Charge_power_prot:int, Charge_Volt_start: float, Charge_volt_end: float,
                   Charge_current_max: float, DCharge_volt_min: float,
                   DCharge_current_max: float, Slew_volt: float, Slew_current: float,
                   LeadinTime: int, Charge_time: int, DCharge_time: int, numCycles: int):
        import threading
        self.testController.event.clear()
        self.upsThread = threading.Thread(target=self.testController.NEWupsTest,
                                          args=(Test_Name,Temperature,Charge_volt_prot,
                                                Charge_current_prot,Charge_power_prot,
                                                Charge_Volt_start, Charge_volt_end,
                                                Charge_current_max,
                                                DCharge_volt_min, DCharge_current_max,
                                                Slew_volt, Slew_current,
                                                LeadinTime, Charge_time,
                                                DCharge_time, numCycles))
        self.upsThread.start()


def main():
    TObj = TestTypes()  # initiating a TestObject:: TObj
    it = 1

    TObj.runUPSTest(
        TEST_NAME,
        TEMPERATURE,
        CHARGE_VOLT_PROT,
        CHARGE_CURRENT_PROT,
        CHARGE_POWER_PROT,
        CHARGE_VOLT_START,
        CHARGE_VOLT_END,
        CHARGE_CURRENT_MAX,
        DCHARGE_VOLT_MIN,
        DCHARGE_CURRENT_MAX,
        SLEW_VOLT,
        SLEW_CURRENT,
        LEADIN_TIME,
        CHARGE_TIME,
        DCHARGE_TIME,
        NUM_CYCLES
    )


if __name__ == "__main__":
    main()
