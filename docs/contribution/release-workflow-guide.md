# Release workflow

This guide describes how releases are published to PyPI in the current CI setup.
First make sure release notes are described in `CHANGELOG.md`.

## CI-based release (recommended)

Before you click **Publish release** on GitHub, quick checklist:

1. `pyproject.toml` version is updated.
2. `selene/__init__.py` `__version__` is updated.
3. Release tag equals these versions and has no `v` prefix.
4. `CHANGELOG.md` contains release notes for this version.
5. Ensure repository secret `PYPI_TOKEN` is configured for publish workflow.


Then publish through GitHub Releases:

1. Create a new GitHub Release.
2. Create or select a tag without `v` prefix, for example `1.0.1` or `2.0.0a39`.
3. Set release title equal to the tag value.
4. Add release notes (summary + details, usually based on `CHANGELOG.md`).
5. Mark as pre-release when needed.
6. Publish the release.

After publishing, GitHub Actions workflow [`publish.yml`](https://github.com/yashaka/selene/blob/master/.github/workflows/publish.yml) is triggered on `release.published` and performs:

1. Version consistency check (`tag == pyproject.toml == selene/__init__.py`).
2. Package build (`poetry build`).
3. Distribution validation (`twine check dist/*`).
4. Upload to PyPI (`poetry publish` using `PYPI_TOKEN`).

Important: CI does not auto-commit version changes. If versions do not match the release tag, the publish job fails.

## Manual fallback (maintainers-only emergency path)

Use this path only when CI-based publish is unavailable.
For regular releases, use GitHub Release + CI publish flow above.

You can publish manually:

1. `bash .run/bump_version.sh x.x.x`
2. `bash .run/build.sh`
3. `bash .run/publish.sh`

Or in one command:

`bash .run/bump_build_publish.sh x.x.x`

Or fully manual:

1. Update versions in `pyproject.toml` and `selene/__init__.py`.
2. Run `poetry publish --build`.

Do not forget to push the release tag and publish release notes on GitHub.
If the same version was already published manually, CI publish for that tag will fail on duplicate version upload.

## Troubleshooting

If `Publish Python Package` fails at `Check release version consistency`:

1. Compare release tag with `pyproject.toml` version and `selene/__init__.py` `__version__`.
2. Fix mismatches in source branch.
3. Push changes and create a new release/tag that matches source versions.