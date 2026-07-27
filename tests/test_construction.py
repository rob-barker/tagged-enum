import pytest

from helpers import _Tester


def test_construction_with_payload():
    first = _Tester.STRING("This is a tester")
    second = _Tester.COORDINATES((2, 4.0))

    assert first.payload == "This is a tester"
    assert second.payload == (2, 4.0)


def test_construction_without_payload():
    instance = _Tester.NONE()

    assert instance.payload is None
    assert instance is not _Tester.NONE  # calling produces a new instance
    assert instance == _Tester.NONE()


def test_member_is_not_an_instance():
    assert _Tester.NONE.is_member is True
    assert _Tester.NONE().is_member is False


def test_calling_an_instance_raises():
    instance = _Tester.STRING("already constructed")
    with pytest.raises(TypeError):
        instance("again")


def test_none_payload_defaults_when_no_arg_given():
    assert _Tester.NONE().payload is None
