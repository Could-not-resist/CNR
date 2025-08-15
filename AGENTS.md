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
| `main.py` | Command line interface and entry point. Parses arguments, loads configuration from `profiles.json` and invokes tests in `TestController`. |
| `al_ion_battery_test_software.py` | Implements `TestController` coordinating the power supply, electronic load and multimeter. Contains high level test routines such as custom tests, efficiency tests and capacity measurements. |
| `al_ion_test_software_data_management.py` | Provides the `DataStorage` class used to store and export measurement data to CSV/Excel and to create graphs. |
| `al_ion_test_software_device_drivers.py` | Low level device drivers using NI-VISA to control the power supply, electronic load and multimeter. |
| `al_ion_test_software_device_drivers_mock.py` | Mock versions of the device drivers for running the software without hardware attached. |
| `scpi_commands.py` | Quick reference of SCPI command strings used by the drivers. |
| `profiles.json` | Example configuration profiles containing default test parameters. |
| `manuals/` | Folder for manufacturer manuals (ignored by version control). |

### Main modules

**TestController** (`al_ion_battery_test_software.py`)
: Handles test execution. It exposes functions like `custom_test`, `efficiency_test`, `rate_characteristic_test`, `internal_resistance_test` and `actual_capacity_test`. These routines send commands to the instrument drivers and log measurements via `DataStorage`.

**DataStorage** (`al_ion_test_software_data_management.py`)
: Collects timestamps, voltage, current, power and optional capacity or multimeter readings. `createTable()` writes a CSV file and optionally an Excel workbook with graphs.

**Device drivers** (`al_ion_test_software_device_drivers.py` and `al_ion_test_software_device_drivers_mock.py`)
: Provide methods such as `setVoltage`, `startDischarge`, `getVoltage`, etc. The mock drivers emulate these interfaces for development without instruments.

### Running tests

The typical workflow is executing `python main.py` with optional flags or configuration files. `main.py` creates a `TestController` and calls the appropriate test routine based on the arguments.


