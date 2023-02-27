# Release workflow

First make sure you described release notes in CHANGELOG.md.

## Automatically

1. Create new release on GitHub.
2. Choose new tag or take not released yet.

    Name it without `v` prefix, like: `1.0.1`, `2.0.0a39`

3. Set "release title" to same value as tag name

    (in order to fully render at Releases section on main github project page,
    and be consistent with other common github projects)

4. Describe release notes.

    Give it a short summary as `# <Heading Summary>`
    Provide details (usually copied from CHANGELOG)  
    (if they are not the same as summary ;)

5. Select pre-release checkbox if not stable.

    (Currently the 2.0.0a* alpha versions can also be marked
    as stable)

6. Publish the release on GitHub.

Then GitHub action will automatically build and publish release
to PyPI with selected tag automatically.
Also it will commit the tag semver
into `__init__.py` and `pyproject.toml`
before building if it has not been there yet.

## Old fashion manually

(only if GitHub Actions CI is not available)

1. bump version via `bash .run/bump_version.sh x.x.x`
2. build via `bash .run/build.sh`
3. publish via `bash .run/publish.sh`

or

`bash .run/bump_build_publish.sh x.x.x`

or if you want to control all by yourself

1. manually bump version in `pyproject.toml` and `selene/__init.py:__version__`
2. `poetry publish --build`

Also don't forget to push a tag and describe release notes on GitHub!
(If GitHub Actions works then publish job will fail
because same version had already been published on pypi.org)
