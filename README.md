# CNR

This project contains Python scripts for automated charging and discharging tests.
It communicates with a **Chroma 63600 Modular DC Electronic Load**, a
**Chroma 62000P Programmable DC Power Supply** and a **Chroma 12061 multimeter**
to perform the ``custom_test`` charge/discharge cycle and other built-in
measurements while logging the resulting data.

## Project structure

| File | Purpose |
| --- | --- |
| `MAIN.py` | Command-line interface and entry point. Parses arguments, loads configuration from `cell_profiles.json` and invokes tests in `TestController`. |
| `AlIonBatteryTestSoftware.py` | Implements `TestController`, coordinating the power supply, electronic load and multimeter. Contains high level test routines such as custom tests, efficiency tests and capacity measurements. |
| `AlIonTestSoftwareDataManagement.py` | Provides the `DataStorage` class used to store and export measurement data to CSV/Excel and to create graphs. |
| `AlIonTestSoftwareDeviceDrivers.py` | Low level device drivers using NI-VISA to control the power supply, electronic load and multimeter. |
| `AlIonTestSoftwareDeviceDriversMock.py` | Mock versions of the device drivers for running the software without hardware attached. |
| `build_test_config.py` | Interactive helper that writes profile entries for any test type. |
| `scpi_commands.py` | Quick reference of SCPI command strings used by the drivers. |
| `cell_profiles.json` | Example configuration profiles containing test parameters and their `test_type`. |
| `manuals/` | Manufacturer programming manuals (not tracked by version control). |

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

1. Connect the Chroma 63600 electronic load, Chroma 62000P power supply and
   Chroma 12061 multimeter to your PC and ensure the NI-VISA drivers are
   installed.
2. Adjust the charge/discharge parameters using command-line options, or
   provide a JSON configuration file with cell profiles and capacity defaults.
3. Run the test script:

```bash
python MAIN.py
```
   If no hardware connection is detected the program aborts unless mock
drivers are enabled. Set the environment variable `USE_MOCK_DRIVERS=1`
to force the built‑in mock drivers for development without hardware.
Use the `-d` flag to print detailed progress messages during a test.

Charging and discharging default to constant current (`CC`). Select
constant voltage (`CV`) or constant power (`CP`) with the
`--charge-mode` and `--discharge-mode` options:

```bash
python MAIN.py --charge-mode CV --discharge-mode CP
```

### Instrument resource names

The scripts use preset NI-VISA resource names for the power supply,
electronic load and multimeter.  These can be overridden:

* Command line options `--ps-resource`, `--el-resource` and `--mm-resource`
* Environment variables `POWER_SUPPLY_RESOURCE`,
  `ELECTRONIC_LOAD_RESOURCE` and `MULTIMETER_RESOURCE`
* Keys `ps_resource`, `el_resource` and `mm_resource` in the selected
  JSON configuration profile

If none of these are provided the built-in defaults are used.

To perform a full capacity measurement instead of the default cycling test run:

```bash
python MAIN.py --actual-capacity-test \
  --capacity-charge-current 1.0 \
  --capacity-discharge-current 1.0 \
  [--capacity-rest-time 3600] \
  [--capacity-charge-voltage 4.1] \
  [--capacity-min-voltage 2.75] \
  [--capacity-finish-current 1.5]
```
``--capacity-charge-voltage`` defaults to the value of ``--charge-volt-end``
(or ``4.1``&nbsp;V). ``--capacity-rest-time`` and ``--capacity-min-voltage``
fall back to the values in the ``capacity_defaults`` section of the JSON
file passed with ``--config-file`` or, if that section is absent, to one
hour and ``2.75``&nbsp;V respectively.

The configuration file may define ``rest_time``, ``charge_voltage``,
``min_voltage``, ``charge_current``, ``discharge_current``,
``finish_current`` and ``multimeter_mode`` keys inside
``capacity_defaults``. These values override the built‑in defaults in
``MAIN.py`` but any command-line options still take precedence.

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
  cell. This command only measures resistance; run `--actual-capacity-test`
  separately to measure capacity.

### Using configuration files

Instead of specifying every parameter on the command line you can store
cell profiles in a JSON file. A sample `cell_profiles.json` is included in
the repository. It also contains a ``capacity_defaults`` section used for
standalone capacity tests.

Profiles follow this structure:

```json
{
  "YUASA": {
    "test_type": "custom",
    "parameters": {
      "charge_volt_start": 4.1,
      "charge_volt_end": 4.1,
      "charge_current_max": 5.0,
      "dcharge_volt_min": 2.75,
      "dcharge_current_max": 20.0,
      "test_name": "YUASA"
    }
  }
}
```

Run the profile without additional flags and `MAIN.py` selects the
appropriate test based on `test_type`:

```bash
python MAIN.py --config-file cell_profiles.json --profile YUASA
```

Command-line options still override the values loaded from the profile.

The helper `build_test_config.py` prompts for a test name and `test_type`
and then gathers the relevant parameters before writing a profile snippet
under `configs/`.

This charges the cell at 1C up to the voltage specified by
`--capacity-charge-voltage` (default taken from `--charge-volt-end`),
rests for the duration given by `--capacity-rest-time` (default one hour)
at 20&nbsp;±&nbsp;2 °C and then discharges at 1C down to
`--capacity-min-voltage` (default **2.75&nbsp;V**) while recording the
delivered ampere hours.

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
| `REST_TIME` | `0` | s |
| `NUM_CYCLES` | `1` | &ndash; |

`LEADIN_TIME` controls how long the power supply ramps from
`CHARGE_VOLT_START` to `CHARGE_VOLT_END` at the beginning of each charge cycle.
`REST_TIME` defines a pause inserted after each charge or discharge phase.

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
| `--leadin-time` | Time in seconds used to ramp the supply from the starting to the ending charge voltage |
| `--charge-time` | Allowed charging time |
| `--dcharge-time` | Allowed discharging time |
| `--rest-time` | Rest period in seconds between charge and discharge |
| `--num-cycles` | Number of charge/discharge cycles |
| `--sample-interval` | Time between measurements in seconds |
| `--multimeter-mode` | Log measurement using the multimeter (`voltage` or `tcouple`) |
| `-d`, `--debug` | Print detailed progress information |


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

## Development notes

Results generated by the test scripts are stored under the `Data/` directory.
The `DataStorage` class automatically creates this folder on first use and
saves a CSV file for each test run. Each row now contains the actual
measurement time down to milliseconds followed by the elapsed time in seconds.
Excel files with embedded graphs can be generated by passing
``export_xlsx=True`` when calling ``createTable``.

There are currently no automated tests. Contributors should run a quick syntax
check before committing by executing

```bash
python -m py_compile *.py
```

at the repository root. This ensures all Python files compile cleanly.

## Breaking Changes

- The `--use-multimeter` flag has been removed. Use `--multimeter-mode` to enable
  multimeter logging.

## Stopping a running test

Press `Ctrl+C` while a test is active to abort safely. The program turns off
all outputs and saves the results collected so far before exiting.
