# ✅ Release Qualification Checklist

This is the runbook for deciding whether a commit is fit to become a
release candidate (RC) for `tagged-enum`. Every step below was performed
manually and verified for the v1.0.0 release; this document formalizes
that process so future releases (and other contributors) can repeat it
without re-deriving it from scratch.

Run every step from a clean checkout of the commit you intend to release.
If any step fails, fix the underlying issue, commit the fix, and start
the checklist over — don't skip ahead.

## 1. Install dependencies

```bash
uv sync
```

**Gotcha worth knowing:** plain `uv sync` (no flags) only works here because
`pyproject.toml` declares the test dependency in *two* places:

```toml
[project.optional-dependencies]
test = ["pytest>=7.0"]

[dependency-groups]
dev = ["pytest>=7.0"]
```

- `[project.optional-dependencies]` (the `test` extra) is what `pip install
  ".[test]"` uses — it exists for non-`uv` consumers.
- `[dependency-groups]` (the `dev` group) is what `uv sync` installs *by
  default*, with no flags.

**`uv sync` alone does NOT install `optional-dependencies` extras** — only
`dependency-groups`. If test deps were declared solely under
`[project.optional-dependencies]`, a plain `uv sync` would silently produce
an environment without `pytest`, and the next step would fail with a
confusing "module not found." Both entries need to stay in sync when
dependencies change.

## 2. Run the full test suite

```bash
uv run pytest
```

All tests must pass. As of v1.0.0 this is 44 tests across `tests/`, split
by topic so a single area can be run in isolation if needed:

- `test_construction.py`
- `test_type_checking.py`
- `test_equality_and_hashing.py`
- `test_kind.py`
- `test_make_and_payload_type.py`
- `test_generic_payloads.py`
- `test_recursive_cases.py`
- `test_multiple_enums.py`
- `test_pattern_matching.py`
- `test_repr.py`
- `test_immutability.py`

If the test count or file list has changed since this doc was written,
that's expected as the library grows — the point isn't the exact number,
it's that the *whole suite* passes, not a subset.

## 3. Build the distributions

```bash
uv build
```

This produces both an sdist and a wheel in `dist/`. Clear out any stale
`dist/` contents from a previous run first so the inspection steps below
aren't looking at old artifacts.

## 4. Validate package metadata

```bash
uv run --with twine twine check dist/*
```

Both the sdist and the wheel must report `PASSED`. This catches malformed
metadata and, critically, verifies the README renders correctly as the
`long_description` — since the README becomes the PyPI project page
verbatim (see step 6).

## 5. Inspect the wheel contents

```bash
python -m zipfile -l dist/*.whl
```

Confirm the wheel contains **only** the intended package files:

- `tagged_enum/TaggedEnum.py`
- `tagged_enum/__init__.py`
- `tagged_enum/py.typed`
- the standard `*.dist-info/` metadata: `METADATA`, `WHEEL`,
  `licenses/LICENSE`, `RECORD`

Anything else (stray caches, editor files, local config) means the wheel
is shipping things it shouldn't, and the packaging config needs fixing
before proceeding.

## 6. Inspect the sdist contents

```bash
python -m tarfile -l dist/*.tar.gz
```

**This is the step that actually caught a real bug during the v1.0.0
qualification pass.** The sdist was bundling `.claude/settings.local.json`
— a local Claude Code tool config — because it was excluded only via the
*developer's global* `~/.gitignore`, not the repo's own `.gitignore`.
Hatchling (the build backend) has no visibility into a global gitignore,
so it had no way to know to skip that file.

The fix was an explicit exclude list in `pyproject.toml`:

```toml
[tool.hatch.build]
exclude = [
    ".claude/",
    ".venv/",
    ".pytest_cache/",
    "**/__pycache__/",
]
```

**Lesson:** always inspect the actual sdist contents before publishing —
don't just trust `.gitignore`. A repo's own `.gitignore` and a
contributor's *global* git excludes are two different mechanisms, and a
build backend only ever sees the repo's own ignore rules (if it consults
`.gitignore` at all). The only reliable check is looking at what actually
landed in the archive.

## 7. Check README links

Since the README becomes the PyPI project page's rendered description
*standalone* — not viewed inside the GitHub repo — any relative link
(e.g. `[TODO.md](TODO.md)`) will 404 on PyPI. The README must only use
absolute URLs for anything meant to work off-repo.

Verify no relative links exist, e.g.:

```bash
grep -oE '\[[^]]+\]\(([^)h][^)]*)\)' README.md
```

(This flags any markdown link whose target doesn't start with `h`, i.e.
isn't `http(s)://` — adjust if the README ever legitimately needs a
non-http absolute reference.) An empty result is what you want.

## 8. Clean-room smoke test

Install the **actual built wheel** — not an editable/dev install — into a
throwaway venv completely outside the repo, then import the package and
exercise its real API from a fresh Python process. This catches anything
an editable install would mask: missing files in the wheel, packaging
path issues, incorrect package discovery, etc.

```bash
# outside the repo directory
python -m venv /tmp/tagged-enum-smoketest
/tmp/tagged-enum-smoketest/Scripts/python -m pip install "C:/Users/Rob Barker/Developer/tagged-enum/dist/tagged_enum-1.0.0-py3-none-any.whl"
/tmp/tagged-enum-smoketest/Scripts/python -c "
from tagged_enum import TaggedEnum

class Shape(TaggedEnum):
    CIRCLE = float
    RECTANGLE = tuple[float, float]

s = Shape.CIRCLE(2.0)
match s:
    case Shape(kind=Shape.CIRCLE, payload=r):
        print('ok', r)
"
```

Adjust the venv path and wheel filename for the version being qualified.
The point is a fresh interpreter, a fresh environment, and the real
built artifact — nothing borrowed from the dev environment.

## 9. Check PyPI name availability (new projects only)

Before ever attempting a real publish of a brand-new project name, confirm
it isn't already taken:

```bash
curl -s -o /dev/null -w "%{http_code}" https://pypi.org/pypi/tagged-enum/json
```

- `404` — name is available.
- `200` — name is taken (either by you already, or by someone else).

This only needs to be done once per project name, not on every release.

## Done

Once all nine steps pass on a given commit, that commit is a qualified
release candidate. Proceed to [`docs/publishing.md`](./publishing.md) to
actually ship it.
