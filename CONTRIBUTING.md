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
10. Commit your changes (`git commit -am 'Add some feature'`)
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
