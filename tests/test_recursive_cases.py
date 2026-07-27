import pytest

from tagged_enum import TaggedEnum


class Json(TaggedEnum):
    NULL = None
    NUMBER = float
    ARRAY = list["Json"]
    NEXT = "Json"  # bare self-reference


def test_self_referential_case_can_be_constructed():
    leaf = Json.NUMBER(1.0)
    tree = Json.ARRAY([leaf])
    assert tree.payload == [leaf]


def test_container_of_self_reference_still_checks_outer_container_type():
    # The forward ref to the enclosing class can't be resolved at
    # declaration time, but the outer `list` container is still checked.
    with pytest.raises(TypeError):
        Json.ARRAY("not actually a list")


def test_bare_self_reference_skips_strict_typecheck():
    # A case typed as a bare forward reference to its own enum has no
    # resolvable type to check against, so any payload is accepted.
    leaf = Json.NUMBER(1.0)
    assert Json.NEXT(leaf).payload is leaf
