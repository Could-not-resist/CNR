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
2. Edit the values at the top of `MAIN.py` to set charge/discharge parameters
   (voltages, currents, number of cycles, etc.).
3. Run the test script:

```bash
python MAIN.py
```

By default the parameters in `MAIN.py` define a single cycle with
16.21&ndash;16.4&nbsp;V charging at 5&nbsp;A and a discharge down to 11&nbsp;V.
Adjust them as needed for your test setup.

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
