from typing import Optional, Union

import pytest

from tagged_enum import TaggedEnum


class _Container(TaggedEnum):
    NUMBERS = list[int]
    MAPPING = dict[str, int]
    ID = Union[int, str]
    LABEL = Optional[str]
    PIPED = int | str


def test_list_payload_accepts_list():
    assert _Container.NUMBERS([1, 2, 3]).payload == [1, 2, 3]


def test_list_payload_rejects_non_list():
    with pytest.raises(TypeError):
        _Container.NUMBERS("not a list")


def test_dict_payload():
    assert _Container.MAPPING({"a": 1}).payload == {"a": 1}
    with pytest.raises(TypeError):
        _Container.MAPPING(["not", "a", "dict"])


def test_union_payload_accepts_any_member_type():
    assert _Container.ID(42).payload == 42
    assert _Container.ID("42").payload == "42"


def test_union_payload_rejects_other_types():
    with pytest.raises(TypeError):
        _Container.ID(4.2)


def test_optional_payload_accepts_none_or_type():
    assert _Container.LABEL(None).payload is None
    assert _Container.LABEL("hi").payload == "hi"


def test_optional_payload_rejects_wrong_type():
    with pytest.raises(TypeError):
        _Container.LABEL(123)


def test_pep604_union_payload():
    assert _Container.PIPED(1).payload == 1
    assert _Container.PIPED("x").payload == "x"
    with pytest.raises(TypeError):
        _Container.PIPED(1.5)
