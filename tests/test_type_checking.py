import pytest

from helpers import _Tester


@pytest.mark.parametrize("member, bad_value", [
    (_Tester.STRING, 123),
    (_Tester.COORDINATES, "not a tuple"),
    (_Tester.NONE, "not none"),
])
def test_type_safety_rejects_wrong_payload(member, bad_value):
    with pytest.raises(TypeError):
        member(bad_value)


def test_type_safety_accepts_correct_payload():
    assert _Tester.STRING("ok").payload == "ok"
    assert _Tester.COORDINATES((1.0, 2.0)).payload == (1.0, 2.0)
    assert _Tester.NONE(None).payload is None
