# Code conventions

We follow the principles of consistency and readability.
Code-style is controlled by few linter jobs in GitHub Actions.

1. [Pycodestyle][pycodestyle]
2. [Pylint][pylint]
3. [Black][black]

[pycodestyle]: https://github.com/PyCQA/pycodestyle
[pylint]: https://github.com/PyCQA/pylint
[black]: https://github.com/psf/black

## Pycodestyle

- Protects the code from violations of agreed rules.
- Ignores E402,E731 rules for now.

## Pycodestyle-full-report

- Prints a full report of pycodestyle rule violations,
including not agreed yet.

## Pylint

- Protects the code from violations of agreed rules.
- Lints all agreed rules configured in [.pylintrc][selene-pylintrc]
- Ignores list of rules which are not agreed yet
[.pylint-disabled-rules][selene-pylint-disabled-rules]

[selene-pylintrc]: https://github.com/yashaka/selene/blob/master/.pylintrc
[selene-pylint-disabled-rules]: https://github.com/yashaka/selene/blob/master/.pylint-disabled-rules

## Pylint-full-report

- Lints all agreed rules configured in
[.pylintrc][selene-pylintrc]
- Prints a full report of pylint rule violations,
including not agreed yet.

## Black

- Lints default black rules except "string normalization".
