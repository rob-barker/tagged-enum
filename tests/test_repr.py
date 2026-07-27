from helpers import _Tester


def test_repr_of_member():
    assert repr(_Tester.STRING) == "_Tester.STRING"


def test_repr_of_instance_includes_payload():
    assert repr(_Tester.STRING("hi")) == "_Tester.STRING('hi')"
    assert str(_Tester.STRING("hi")) == "_Tester.STRING('hi')"
