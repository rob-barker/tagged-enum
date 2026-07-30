<h1 align="center">🏷️ tagged-enum</h1>

<p align="center">
  <a href="https://pypi.org/project/tagged-enum/"><img src="https://img.shields.io/pypi/v/tagged-enum.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/tagged-enum/"><img src="https://img.shields.io/pypi/pyversions/tagged-enum.svg" alt="Python versions"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/rob-barker/tagged-enum.svg" alt="License: MIT"></a>
  <a href="https://pypi.org/project/tagged-enum/"><img src="https://img.shields.io/pypi/dm/tagged-enum.svg" alt="PyPI downloads"></a>
</p>

Tagged enums for Python 🐍.

Tagged enums (a.k.a. tagged unions, discriminated unions, enums with associated values, etc.)
are enums where each case carries a typed **payload**.

```python
class Shape(TaggedEnum):
    CIRCLE = float                   # radius
    RECTANGLE = tuple[float, float]  # width, height
    TRIANGLE = tuple[float, float]   # base, height

Shape.CIRCLE(2.0)
Shape.RECTANGLE((3.0, 4.0))
Shape.TRIANGLE((6.0, 2.0))
```

Unpack cases with `match`:

```python
def area(shape: Shape) -> float:
    match shape:
        case Shape(kind=Shape.CIRCLE, payload=radius):
            return 3.14159 * radius ** 2
        case Shape(kind=Shape.RECTANGLE, payload=(w, h)):
            return w * h
        case Shape(kind=Shape.TRIANGLE, payload=(b, h)):
            return 0.5 * b * h
```

This is one of my favorite features from [Swift](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/enumerations/#Associated-Values) and [Rust](https://doc.rust-lang.org/rust-by-example/custom_types/enum.html) so I brought it to Python 😈.

## ⬇ Installation

```bash
pip install tagged-enum
```

Requires Python 3.11+

## 🤔 How to use

Each uppercase attribute on a `TaggedEnum` subclass declares a *case*. The
value assigned to it is the *type* of payload that case carries. `None`
means the case carries nothing.

```python
class Result(TaggedEnum):
    SUCCESS = None   # void — it just worked
    FAILURE = str    # error message
```

Calling a case constructs an **instance**, and the payload is checked against
the declared type on instantiation.

```python
Result.SUCCESS()                  # 👍
Result.FAILURE("invalid input")   # 👍
Result.FAILURE(404)               # 👎 - TypeError
```

### 🧩 Typing

Payload declarations may be plain types, generic containers, unions, custom types, or forward references to the enclosing class for recursive structures:

```python
class Json(TaggedEnum):
    NULL = None
    NUMBER = float
    STRING = str
    ARRAY = list["Json"]
    OBJECT = dict[str, "Json"]
    CUSTOM = MyDataclass

Json.OBJECT({
    "name": Json.STRING("Ada"),
    "tags": Json.ARRAY([Json.STRING("math"), Json.NUMBER(1815.0)]),
    "other": Json.CUSTOM(MyDataclass())
})
```

`Union[...]` or `X | Y` and `Optional[...]` payloads are also valid types. Construction succeeds if the value matches any member of the union:

```python
class ID(TaggedEnum):
    VALUE = int | str

ID.VALUE(42)     # 👍
ID.VALUE("abc")  # 👍
ID.VALUE(4.2)    # 👎 - TypeError
```

Type checking validates the outer container (e.g. `list`, `dict`, which
member of a `Union`) but does not recurse into generic type parameters, and
skips validation entirely for unresolved forward references like `"Json"`
above. This is a known limitation and will be addressed in a future release.

### ✨ Pattern Matching

Tagged enums are unpacked with Python's native [match statement](https://docs.python.org/3/tutorial/controlflow.html#match-statements) using the `kind`/`payload` attributes:

```python
class GameEvent(TaggedEnum):
    PLAYER_JOINED = str             # player name
    DAMAGE_DEALT = tuple[str, int]  # target, amount
    GAME_OVER = None                # void

def handle(event: GameEvent) -> str:
    match event:
        case GameEvent(kind=GameEvent.PLAYER_JOINED, payload=name):
            return f"{name} joined the game"
        case GameEvent(kind=GameEvent.DAMAGE_DEALT, payload=(target, amount)):
            return f"{target} took {amount} damage"
        case GameEvent(kind=GameEvent.GAME_OVER):
            return "Game over"

handle(GameEvent.DAMAGE_DEALT(("Grendel", 42)))
# 'Grendel took 42 damage'
```

When you only care about which case you're looking at and not the payload, use `.kind` to return the tag itself (also called the **member**):

```python
if event.kind is GameEvent.Kind.PLAYER_JOINED:
    print("player joined")

match event.kind:
    case GameEvent.Kind.PLAYER_JOINED:
        ...
    case GameEvent.Kind.GAME_OVER:
        ...
```

`GameEvent.PLAYER_JOINED` (the **member**) and
`GameEvent.PLAYER_JOINED(...)` (an **instance**) are different objects and ideas. The member is a singleton tag you compare with `is`, while the instance carries the actual data payload. Members and instances are not equal (by `==`). Instances of the same kind/case are equal if and only if their payload values are equal. 

The `Kind` type attribute is a type-level alias for annotating variables that should hold a case rather than an instance.

```python
def describe(kind: GameEvent.Kind) -> str:
    if kind is GameEvent.Kind.PLAYER_JOINED:
        do_something()

describe(event.kind) # 'damage was dealt'
```

## 🤓 Development

This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management.

```bash
uv sync
uv run pytest
```

### Building

Build the sdist/wheel into `dist/`:

```bash
uv build
```

To try the library locally without installing it anywhere:

```bash
# drop into a REPL
uv run python
# OR run a script inside the project's environment
uv run python my_script.py
```

### 🧪 Testing 

Tests live in `tests/`, split by topic (construction, equality/hashing,
pattern matching, generic payloads, etc.) so a single area can be run in
isolation, e.g.:

```bash
uv run pytest tests/test_generic_payloads.py
```

Without `uv`, the equivalent is:

```bash
pip install -e ".[test]"
pytest
```

## 🛠️ Contribution Guidelines

This repository is open source, though maintenance is infrequent. Please be
patient 🥺.

- **File an issue first:** Anything beyond a small fix should be discussed in an issue
  before you put work into a PR.
- **Keep PRs focused:** One change or feature per PR, branched off `Development`
  and rebased/updated before you submit.
- **Branch naming:** `issues/<issue-number>`, optionally with a short
  description, e.g. `issues/123-fix-a-bug`.
- **Include a description and test coverage:** Explain what changed and
  why, add or update tests under `tests/`, and reference the issue it
  closes.

Thanks for helping keep this repo clean and organized! 😁
