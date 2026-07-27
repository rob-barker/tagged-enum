import pytest

from helpers import _Tester


def test_instance_attributes_cannot_be_reassigned():
    instance = _Tester.STRING("frozen")
    with pytest.raises(AttributeError):
        instance._item = "mutated"


def test_instance_forbids_setting_new_attributes_after_creation():
    instance = _Tester.STRING("frozen")
    instance.extra = "first write should succeed"
    with pytest.raises(AttributeError):
        instance.extra = "second write should fail"
