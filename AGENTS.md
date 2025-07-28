# Agent Instructions

This repository contains Python scripts for controlling a UPS battery testing setup. To help agents work efficiently, follow these guidelines when making changes:

1. **Syntax check**: Before committing, run `python -m py_compile *.py` at the repository root. This ensures all Python files compile without syntax errors.
2. **No automated tests**: There are currently no automated tests. If you add any, document how to run them in `README.md`.
3. **Commit messages**: Write concise commit messages summarizing what you changed.
4. **Documentation**: Keep the `README.md` up to date if your changes affect usage or setup instructions.
5. **Hardware caution**: The scripts interact with specific hardware. Avoid modifying device command sequences unless necessary, and clearly comment any changes.

