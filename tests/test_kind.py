from helpers import _Tester


def test_kind_on_member_returns_itself():
    assert _Tester.STRING.kind is _Tester.STRING


def test_kind_on_instance_returns_owning_member():
    instance = _Tester.COORDINATES((1.0, 2.0))
    assert instance.kind is _Tester.COORDINATES


def test_kind_type_alias_matches_class():
    assert _Tester.Kind is _Tester
