# tagged-enum

Tagged enums (sum types / algebraic data types) for Python, built directly on
`enum.Enum`. Each case can carry a typed payload, payloads are validated at
construction time, and instances work with `match` statements out of the box.

## Installation

```bash
pip install tagged-enum
```

Requires Python 3.11+.

## Usage

```python
from tagged_enum import TaggedEnum

class Message(TaggedEnum):
    PING = None
    STRING = str
    COORDINATES = tuple[int, int]

ping_msg = Message.PING()
string_msg = Message.STRING("hello world")
coords_msg = Message.COORDINATES((1, -1))
```

Each uppercase attribute on a `TaggedEnum` subclass declares a case. The
value assigned to it is the type of payload that case carries; `None` means
the case carries no payload. Calling a case constructs an instance, and the
payload is validated against the declared type:

```python
Message.STRING(123)  # raises TypeError: STRING: expected <class 'str'>, got <class 'int'>
```

### Pattern matching

Instances unpack via `match`, using the `case`/`item` attributes:

```python
match message:
    case Message(case=Message.PING):
        ...
    case Message(case=Message.STRING, item=string):
        ...
    case Message(case=Message.COORDINATES, item=(x, y)):
        ...
```

The `.kind` property returns the case (the "tag") associated with an
instance, for matching or comparing without touching the payload:

```python
if message.kind is Message.Kind.STRING:
    print("This is a string message")

match message.kind:
    case Message.Kind.PING:
        ...
    case Message.Kind.STRING:
        ...
```

### Members vs. instances

**Member**: the class attribute (e.g. `Message.STRING`) representing a
case's definition.

**Instance**: the object produced by calling a member with a payload (e.g.
`Message.STRING("hello")`). Instances are immutable and compare/hash by
`(case, payload)`.

The `Kind` type attribute is a type-level alias for the enum itself, useful
for annotating a variable that should hold a case rather than an instance.

### Supported payload types

Payload declarations may be plain types, generic containers, unions, or
forward references to the enclosing class for recursive structures:

```python
from typing import Optional

class Json(TaggedEnum):
    NULL = None
    NUMBER = float
    STRING = str
    ARRAY = list["Json"]
    OBJECT = dict[str, "Json"]
```

Type checking validates the outer container (e.g. `list`, `dict`, a `Union`
member) but does not recurse into generic type parameters, and skips
validation entirely for unresolved forward references.

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
uv sync --extra test
uv run pytest
```

Tests live in `tests/`, split by topic (construction, equality/hashing,
pattern matching, generic payloads, etc.) so a single area can be run in
isolation, e.g.:

```bash
uv run pytest tests/test_generic_payloads.py
```

Without uv, the equivalent is:

```bash
pip install -e ".[test]"
pytest
```
