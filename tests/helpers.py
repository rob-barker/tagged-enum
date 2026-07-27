"""Shared TaggedEnum fixtures used across multiple test modules."""

from tagged_enum import TaggedEnum


# Leading underscore keeps pytest's default `Test*` collection from
# picking this up as a test class.
class _Tester(TaggedEnum):
    STRING = str
    COORDINATES = tuple[float, float]
    NONE = None
