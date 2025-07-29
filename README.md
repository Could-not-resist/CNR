# CNR

This project contains Python scripts for automated charging and discharging tests.
It communicates with a **Chroma 63600 Modular DC Electronic Load** and a
**Chroma 62000P Programmable DC Power Supply** to perform UPS battery cycling and
log the resulting data.

## Requirements

- Python 3
- NI-VISA driver software
- pyvisa
- pandas
- openpyxl
- matplotlib
- tabulate

Install the Python packages with:

```bash
pip install pyvisa pandas openpyxl matplotlib tabulate
```

## Usage

1. Connect the Chroma 63600 electronic load and Chroma 62000P power supply to
   your PC and ensure the NI-VISA drivers are installed.
2. Adjust the charge/discharge parameters using command-line options or rely on
   the defaults defined in `MAIN.py`.
3. Run the test script:

```bash
python MAIN.py
```

To perform a full capacity measurement instead of the default cycling test run:

```bash
python MAIN.py --actual-capacity-test --capacity-current 1.0
```

Additional tests can be invoked with the following flags:

- **Efficiency test**

  ```bash
  python MAIN.py --efficiency-test
  ```

  Performs a CC–CV charge followed by a discharge and prints the round
  trip efficiency.

- **Rate characteristic test**

  ```bash
  python MAIN.py --rate-characteristic-test --rates 1.0,0.5,0.2
  ```

  Charges the cell and then discharges sequentially at the specified currents
  to record the delivered capacity at each rate.

- **OCV curve test**

  ```bash
  python MAIN.py --ocv-curve-test --step-current 1.0 --steps 10
  ```

  Steps the state of charge and logs the open circuit voltage after each rest
  period.

- **Internal resistance test**

  ```bash
  python MAIN.py --internal-resistance-test --pulse-current 1 --pulse-duration 1
  ```

  Applies a short current pulse to determine the DC and AC resistance of the
  cell.

This charges the cell at 1C to **4.1&nbsp;V**, rests for one hour at
20&nbsp;±&nbsp;2 °C and then discharges at 1C down to **2.75&nbsp;V** while
recording the delivered ampere hours.

By default the parameters in `MAIN.py` define a single cycle with
16.21&ndash;16.4&nbsp;V charging at 5&nbsp;A and a discharge down to 11&nbsp;V.
You can override any of these values using the command-line options
documented below.

### Main parameters

The top of `MAIN.py` contains constants used to configure a test run:

| Variable | Default | Units |
| --- | --- | --- |
| `CHARGE_VOLT_START` | `16.21` | V |
| `CHARGE_VOLT_END` | `16.4` | V |
| `CHARGE_CURRENT_MAX` | `5.0` | A |
| `DCHARGE_VOLT_MIN` | `11.0` | V |
| `DCHARGE_CURRENT_MAX` | `1` | A |
| `CHARGE_VOLT_PROT` | `20` | V |
| `CHARGE_CURRENT_PROT` | `10` | A |
| `CHARGE_POWER_PROT` | `2000` | W |
| `SLEW_VOLT` | `0.1` | V/ms |
| `SLEW_CURRENT` | `0.1` | A/ms |
| `LEADIN_TIME` | `1` | s |
| `CHARGE_TIME` | `5` | s |
| `DCHARGE_TIME` | `5` | s |
| `NUM_CYCLES` | `1` | &ndash; |

Refer to the device programming manuals for the meaning of each setting.

### Command-line options

The parameters above can be overridden on the command line. The most
common flags accepted by `MAIN.py` are listed below. Run
`python MAIN.py --help` for the full set of options.

| Option | Description |
| --- | --- |
| `--test-name` | Name used for log and output files |
| `--temperature` | Ambient temperature in °C |
| `--charge-volt-prot` | Overvoltage protection limit |
| `--charge-current-prot` | Overcurrent protection limit |
| `--charge-power-prot` | Overpower protection limit |
| `--charge-volt-start` | Starting charge voltage |
| `--charge-volt-end` | Ending charge voltage |
| `--charge-current-max` | Maximum charge current |
| `--dcharge-volt-min` | Minimum discharge voltage |
| `--dcharge-current-max` | Maximum discharge current |
| `--slew-volt` | Voltage slew rate in V/ms |
| `--slew-current` | Current slew rate in A/ms |
| `--leadin-time` | Lead-in delay before measurements; overrides `--slew-volt` and ramps from the start to end voltage |
| `--charge-time` | Allowed charging time |
| `--dcharge-time` | Allowed discharging time |
| `--num-cycles` | Number of charge/discharge cycles |


## Manufacturer Programming Manuals

The `manuals/` directory contains the official programming references used by
the scripts:

- `UM-63600 DC Load - v2.6 012021.pdf` – operating and programming manual for
  the Chroma 63600 electronic load.
- `62000P Operating Programming Manual 1704 - CSS.pdf` – programming manual for
  the Chroma 62000P power supply.

Consult these documents for the full list of SCPI commands and parameter ranges.
Additional manuals can be placed in this folder; it is normally excluded from
version control except for small README files.

SCPI command mappings used by the driver classes are summarized in
`scpi_commands.py` for quick reference when developing new tests.
