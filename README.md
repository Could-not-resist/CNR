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

By default the parameters in `MAIN.py` define a single cycle with 16.21&ndash;16.4 V
charging at 5&nbsp;A and a discharge down to 11&nbsp;V. Adjust them as needed for your
test setup.


## Manufacturer Programming Manuals

A `manuals/` directory is provided for storing manufacturer documentation such as programming manuals.
Add any PDF or reference files you need for the hardware here. The folder is ignored by Git so large documents won't be committed.
