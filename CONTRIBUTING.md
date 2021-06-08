# How to contribute

Before implementing your ideas, it is recommended first to create a corresponding issue and discuss the plan to be approved;)
Also consider first to help with issues marked with help_needed label ;)

1. Add a "feature request" Issue to this project.
2. Discuss its need and possible implementation. And once approved...
3. [Fork](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) the [project](https://github.com/yashaka/selene/fork).
4. Clone your fork of the project `git clone https://github.com/[my-github-username]/selene.git`
5. Install [poetry](https://python-poetry.org) via `pip install poetry`
6. `cd selene`
7. `poetry install`
8. `poetry shell`
9. Create your feature branch (`git checkout -b my-new-feature`)
10. Commit your changes (`git commit -am "gh_$ISSUE_NUMBER: Add some feature"`, where ISSUE_NUMBER is the number of issue this commit relates to)  

    **NOTE :** `-am` is just an example here, if new files were added you should stage the changes (`git add ...`) and then commit your changes.
11. Push to the branch (`git push origin my-new-feature`)
12. Create a new Pull Request

# Code Conventions
We follow the principles of consistency and readability.
Code-style is controlled by few linter jobs in GitHub Actions.

1. [Pycodestyle](https://github.com/PyCQA/pycodestyle)
2. [Pylint](https://github.com/PyCQA/pylint)
3. [Black](https://github.com/psf/black)

### Pycodestyle 
- protects the code from violations of agreed rules.
- ignores E402,E731 rules for now.

### Pycodestyle-full-report
- prints a full report of pycodestyle rule violations, including not agreed yet.

### Pylint
- protects the code from violations of agreed rules.
- lints all agreed rules configured in [.pylintrc](https://github.com/yashaka/selene/blob/master/.pylintrc).
- ignores list of rules which are not agreed yet [.pylint-disabled-rules](https://github.com/yashaka/selene/blob/master/.pylint-disabled-rules). 

### Pylint-full-report
- lints all agreed rules configured in [.pylintrc](https://github.com/yashaka/selene/blob/master/.pylintrc)
- prints a full report of pylint rule violations, including not agreed yet.

### Black 
- lints default black rules except "string normalization".

# Release process
First make sure you described release notes in CHANGELOG.md.
## Automatically

1. Create new release on GitHub.
2. Choose new tag or take not released yet.
3. Describe release notes.
4. Select pre-release checkbox if not stable.
5. Publish the release on GitHub.

Then GitHub action will automatically build and publish release to pypi with selected tag automatically. Also it will commit the tag semver into `__init__.py` and `pyproject.toml` before building if it has not been there yet.

## Old fashion manually (only if GitHub Actions CI is not available)
1. bump version via `bash .run/bump_version.sh x.x.x`
2. build via `bash .run/build.sh`
3. publish via `bash .run/publish.sh`

or

`bash .run/bump_build_publish.sh x.x.x`

or if you want to control all by yourself

1. manually bump version in `pyproject.toml` and `selene/__init.py:__version__`
2. poetry publish --build

Also don't forget to push a tag and describe release notes on GitHub! (If GitHub Actions works then publish job will fail because same version had already been published on pypi.org)
