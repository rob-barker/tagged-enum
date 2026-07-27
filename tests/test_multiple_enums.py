import pytest

from tagged_enum import TaggedEnum

from helpers import _Tester


def test_independent_enums_do_not_share_declared_types():
    class _A(TaggedEnum):
        X = int

    class _B(TaggedEnum):
        X = str

    assert _A.payload_type(_A.X.value) is int
    assert _B.payload_type(_B.X.value) is str
    assert _A.X(1).payload == 1
    with pytest.raises(TypeError):
        _A.X("not an int")


def test_lowercase_and_private_attributes_are_not_treated_as_cases():
    class _WithHelpers(TaggedEnum):
        VALUE = int
        _PRIVATE = "not a case, starts with underscore"

        def helper(self):
            return "not a case, lowercase"

    assert "VALUE" in _WithHelpers.__members__
    assert "_PRIVATE" not in _WithHelpers._declared_types
    assert _WithHelpers.VALUE(1).payload == 1
    assert _WithHelpers.VALUE(1).helper() == "not a case, lowercase"


def test_iterating_enum_yields_only_declared_members():
    assert list(_Tester) == [_Tester.STRING, _Tester.COORDINATES, _Tester.NONE]
