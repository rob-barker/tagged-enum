import pytest

from helpers import _Tester


def test_make_constructs_from_raw_value():
    instance = _Tester.make(_Tester.STRING.value, "built via make")
    assert instance.kind is _Tester.STRING
    assert instance.item == "built via make"


def test_make_enforces_type_checking():
    with pytest.raises(TypeError):
        _Tester.make(_Tester.STRING.value, 42)


def test_item_type_returns_declared_payload_type():
    assert _Tester.item_type(_Tester.STRING.value) is str
    assert _Tester.item_type(_Tester.NONE.value) is type(None)
