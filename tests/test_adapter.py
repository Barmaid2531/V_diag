import pytest
from vdiag.adapter import AdapterResult, ElmSerial


def test_adapter_result_identified_from_ati():
    result = AdapterResult(port="COM3", baudrate=115200, responses={"ATI": "vLinker FS"})
    assert result.identified


def test_adapter_result_not_identified_without_ati():
    result = AdapterResult(port="COM3", baudrate=115200)
    assert not result.identified


def test_only_at_commands_are_allowed():
    elm = ElmSerial("COM3")
    with pytest.raises(ValueError):
        elm.command("0100")
