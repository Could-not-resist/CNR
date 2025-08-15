import sys
import types
from unittest.mock import MagicMock

import importlib
import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MAIN = importlib.import_module("MAIN")


def test_num_cycles_cli_overrides_profile(monkeypatch):
    """Passing --num-cycles overrides profile value."""
    # Stub out TestController to avoid hardware access
    tc_instance = MagicMock()
    tc_cls = MagicMock(return_value=tc_instance)
    dummy_module = types.SimpleNamespace(TestController=tc_cls)
    monkeypatch.setitem(sys.modules, "AlIonBatteryTestSoftware", dummy_module)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "MAIN.py",
            "--profile",
            "YUASA_CUSTOM1",
            "--num-cycles",
            "1",
        ],
    )

    MAIN.main()

    tc_cls.assert_called_once()
    tc_instance.custom_test.assert_called_once()
    assert tc_instance.custom_test.call_args.kwargs["num_cycles"] == 1


def test_validate_required_keys_missing_parameters():
    """Missing required keys trigger a KeyError."""
    profile = {"parameters": {"temperature": 25.0}}
    required = {"custom": ["temperature", "dcharge_current_max"]}
    with pytest.raises(KeyError) as excinfo:
        MAIN.validate_required_keys(profile, required, "custom")
    assert "dcharge_current_max" in str(excinfo.value)


def test_multimeter_mode_cli_overrides_profile(monkeypatch):
    """Passing --multimeter-mode overrides profile value."""
    tc_instance = MagicMock()
    tc_cls = MagicMock(return_value=tc_instance)
    dummy_module = types.SimpleNamespace(TestController=tc_cls)
    monkeypatch.setitem(sys.modules, "AlIonBatteryTestSoftware", dummy_module)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "MAIN.py",
            "--profile",
            "YUASA_CUSTOM1",
            "--multimeter-mode",
            "voltage",
        ],
    )

    MAIN.main()

    tc_cls.assert_called_once()
    tc_instance.custom_test.assert_called_once()
    assert tc_instance.custom_test.call_args.kwargs["multimeter_mode"] == "voltage"
