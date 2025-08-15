import sys
import types
from unittest.mock import MagicMock

import importlib
import pathlib

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
