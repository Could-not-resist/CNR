# Agent Instructions

This repository contains Python scripts for controlling a UPS battery testing setup. To help agents work efficiently, follow these guidelines when making changes:

1. **Syntax check**: Before committing, run `python -m py_compile *.py` at the repository root. This ensures all Python files compile without syntax errors.
2. **No automated tests**: There are currently no automated tests. If you add any, document how to run them in `README.md`.
3. **Commit messages**: Write concise commit messages summarizing what you changed.
4. **Documentation**: Keep the `README.md` up to date if your changes affect usage or setup instructions.
5. **Hardware caution**: The scripts interact with specific hardware. Avoid modifying device command sequences unless necessary, and clearly comment any changes.

---

## Code overview

The project is organised as a set of Python modules used to run charging/discharging cycles on battery cells.

| File | Purpose |
| --- | --- |
| `MAIN.py` | Command line interface and entry point. Parses arguments, loads configuration from `cell_profiles.json` and invokes tests in `TestController`. |
| `AlIonBatteryTestSoftware.py` | Implements `TestController` coordinating the power supply, electronic load and multimeter. Contains high level test routines such as UPS tests, efficiency tests and capacity measurements. |
| `AlIonTestSoftwareDataManagement.py` | Provides the `DataStorage` class used to store and export measurement data to CSV/Excel and to create graphs. |
| `AlIonTestSoftwareDeviceDrivers.py` | Low level device drivers using NI-VISA to control the power supply, electronic load and multimeter. |
| `AlIonTestSoftwareDeviceDriversMock.py` | Mock versions of the device drivers for running the software without hardware attached. |
| `scpi_commands.py` | Quick reference of SCPI command strings used by the drivers. |
| `cell_profiles.json` | Example configuration profiles containing default test parameters. |
| `manuals/` | Folder for manufacturer manuals (ignored by version control). |

### Main modules

**TestController** (`AlIonBatteryTestSoftware.py`)
: Handles test execution. It exposes functions like `NEWupsTest`, `efficiency_test`, `rate_characteristic_test`, `internal_resistance_test` and `actual_capacity_test`. These routines send commands to the instrument drivers and log measurements via `DataStorage`.

**DataStorage** (`AlIonTestSoftwareDataManagement.py`)
: Collects timestamps, voltage, current, power and optional capacity or multimeter readings. `createTable()` writes a CSV file and optionally an Excel workbook with graphs.

**Device drivers** (`AlIonTestSoftwareDeviceDrivers.py` and `AlIonTestSoftwareDeviceDriversMock.py`)
: Provide methods such as `setVoltage`, `startDischarge`, `getVoltage`, etc. The mock drivers emulate these interfaces for development without instruments.

### Running tests

The typical workflow is executing `python MAIN.py` with optional flags or configuration files. `MAIN.py` creates a `TestController` and calls the appropriate test routine based on the arguments.


