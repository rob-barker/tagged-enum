import pytest

from tagged_enum import TaggedEnum

from helpers import _Tester


def test_member_identity_and_equality():
    assert _Tester.COORDINATES == _Tester.COORDINATES
    assert _Tester.STRING is _Tester.STRING


def test_member_vs_instance_are_not_equal():
    assert _Tester.STRING != _Tester.STRING("Test")
    assert _Tester.STRING("Test") != _Tester.STRING


def test_instance_equality_by_payload():
    assert _Tester.STRING("Test") == _Tester.STRING("Test")
    assert _Tester.STRING("Test") != _Tester.STRING("Test2")
    assert _Tester.COORDINATES((2, 2)) == _Tester.COORDINATES((2, 2))
    assert _Tester.COORDINATES((2, 2)) != _Tester.COORDINATES((3, 4))


def test_instances_of_different_cases_are_not_equal():
    assert _Tester.STRING("2") != _Tester.COORDINATES((0.0, 0.0))


def test_equality_against_foreign_type_is_false():
    assert _Tester.STRING("x") != "x"
    assert _Tester.NONE != None  # noqa: E711
    assert _Tester.NONE() != None  # noqa: E711


def test_equality_across_unrelated_tagged_enums():
    class _Other(TaggedEnum):
        STRING = str

    # Same case name/value/payload, but a different TaggedEnum subclass.
    assert _Tester.STRING("x") != _Other.STRING("x")


def test_member_hash_is_stable_and_matches_value():
    assert hash(_Tester.STRING) == hash(_Tester.STRING)
    assert {_Tester.STRING, _Tester.STRING} == {_Tester.STRING}


def test_instance_hash_incorporates_payload():
    a = _Tester.STRING("same")
    b = _Tester.STRING("same")
    c = _Tester.STRING("different")

    assert hash(a) == hash(b)
    assert {a, b, c} == {a, c}


def test_instance_hash_requires_hashable_payload():
    class _WithList(TaggedEnum):
        ITEMS = list

    with pytest.raises(TypeError):
        hash(_WithList.ITEMS([1, 2, 3]))
