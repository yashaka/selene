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
For now code conventions are controlled by few linter jobs in GitHub Actions.
In future we will 

### Pycodestyle-conventions
- concerted to ignore pycodestyle rules E501,E402,E731 for now.
- fails if any of the agreed rule become violated.
- protects code from agreed rules violations.

### Pycodestyle-full-report
- prints full report of violations inside github action job.
- ignores W503 rule in case we agreed with W504 which excludes W503.
- passes even if there are more violations than W503.
- informs about all violations including not agreed.
