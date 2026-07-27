# 🚀 Publishing a Release

This is the runbook for taking a commit that has already passed
[`docs/qualification.md`](./qualification.md) and actually shipping it to
PyPI. Follow it in order — the TestPyPI dry run exists specifically to
catch problems *before* the irreversible step.

**PyPI's upload-is-forever rule:** you can never re-upload the same
version number to a given index, even if you delete the release
afterward. Get it right in the dry run; there is no "undo" on the real
index.

## 0. Prerequisites: API tokens

Generate a token per index, separately:

- **TestPyPI:** https://test.pypi.org/manage/account/ → API tokens
- **Real PyPI:** https://pypi.org/manage/account/ → API tokens

For the **first-ever upload of a new project name**, you need an
**account-scoped** token (`Scope: Entire account`) — a project-scoped
token can't be created until the project already exists on that index.
Once the first upload succeeds, go back and create a **project-scoped**
token for that project, and prefer that for future releases — it limits
the blast radius if the token ever leaks.

Never commit a token, never pass it via a `--token` CLI flag (it lands in
shell history), and never paste it into a chat tool, issue, or AI
assistant. Set it as an environment variable for the duration of the
publish command only (see step 3).

## 1. Register TestPyPI as a named `uv` index

This is a one-time change to `pyproject.toml` — add the following block if
it isn't there yet:

```toml
[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
publish-url = "https://test.pypi.org/legacy/"
explicit = true
```

`explicit = true` keeps this index out of normal dependency resolution —
it's registered purely as a publish target, so `uv sync` / `uv add` won't
start pulling packages from TestPyPI by accident.

## 2. Tag the release commit locally

Do this once you're confident the commit is the one going out (after
qualification passes), but hold off on pushing the tag until after the
real publish succeeds — see step 6.

```bash
git tag v1.0.0
```

## 3. Dry run: publish to TestPyPI

Set the TestPyPI token for this command only:

```bash
# PowerShell
$env:UV_PUBLISH_TOKEN = "pypi-..."   # the TestPyPI token
uv publish --index testpypi
```

```bash
# bash
UV_PUBLISH_TOKEN="pypi-..." uv publish --index testpypi
```

`uv publish --index testpypi` looks up the `testpypi` index registered in
step 1 and uploads whatever is currently in `dist/` (from
`docs/qualification.md` step 3) to its `publish-url`.

## 4. Verify the TestPyPI release

1. Check the rendered project page: `https://test.pypi.org/project/tagged-enum/`
   — confirm the README rendered correctly, metadata looks right, links work.
2. Install it into a fresh throwaway venv from TestPyPI and confirm it
   actually works:

   ```bash
   python -m venv /tmp/tagged-enum-testpypi-check
   /tmp/tagged-enum-testpypi-check/Scripts/python -m pip install --index-url https://test.pypi.org/simple/ tagged-enum
   /tmp/tagged-enum-testpypi-check/Scripts/python -c "from tagged_enum import TaggedEnum; print('ok')"
   ```

   Note: if `tagged-enum` has any dependencies, `--index-url` alone won't
   resolve them (TestPyPI doesn't mirror the full package index). Not an
   issue for this project today since it has none at runtime, but worth
   remembering if that changes — the fix would be adding
   `--extra-index-url https://pypi.org/simple/`.

If anything looks wrong here, **do not proceed to the real publish.** Fix
the issue, bump nothing yet (TestPyPI uploads for a version number are
also permanent — see the note in step 3 of qualification about redoing
`uv build` if you change anything), and re-run from qualification.

## 5. Push the git tag

This is a separate, deliberate step from creating the tag in step 2.
Pushing a tag is externally visible (it shows up on GitHub as a release
point), so don't automate it blindly — only push once you're actually
about to publish for real.

```bash
git push origin v1.0.0
```

## 6. Real publish: PyPI

Set the real PyPI token for this command only, then publish with no
`--index` flag (the default index is real PyPI):

```bash
# PowerShell
$env:UV_PUBLISH_TOKEN = "pypi-..."   # the real PyPI token
uv publish
```

```bash
# bash
UV_PUBLISH_TOKEN="pypi-..." uv publish
```

## 7. Verify the real release

```bash
python -m venv /tmp/tagged-enum-pypi-check
/tmp/tagged-enum-pypi-check/Scripts/python -m pip install tagged-enum
/tmp/tagged-enum-pypi-check/Scripts/python -c "from tagged_enum import TaggedEnum; print('ok')"
```

Also check `https://pypi.org/project/tagged-enum/` renders correctly.

## Future improvement: Trusted Publishing

The flow above uses long-lived API tokens set by hand. PyPI supports
**Trusted Publishing** — an OIDC-based flow where GitHub Actions exchanges
a short-lived identity token for a publish credential at upload time, with
no stored secret at all. Once this repo has a CI workflow, that's the
better long-term approach:

- Configure a trusted publisher for the project on PyPI (and separately
  on TestPyPI), pointing at the specific GitHub repo, workflow file, and
  environment.
- The workflow needs `permissions: id-token: write`.
- Trigger the workflow on version tags (e.g. `on: push: tags: ['v*']`),
  so `git push origin v1.0.0` from step 5 is what kicks off the publish
  instead of a manual `uv publish`.
- Typically implemented with the
  [`pypa/gh-action-pypi-publish`](https://github.com/pypa/gh-action-pypi-publish)
  action, which also generates [PEP 740](https://peps.python.org/pep-0740/)
  attestations for the uploaded artifacts by default.

This repo doesn't have CI set up yet, so for now the manual token-based
flow in this document is the process. Revisit this once a CI workflow
exists.

## Sources consulted

- [uv: Building and publishing a package](https://docs.astral.sh/uv/guides/package/)
- [uv: Package indexes](https://docs.astral.sh/uv/concepts/indexes/)
- [PyPI: Publishing with a Trusted Publisher](https://docs.pypi.org/trusted-publishers/using-a-publisher/)
- [GitHub Docs: Configuring OpenID Connect in PyPI](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-pypi)
- [pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish)
