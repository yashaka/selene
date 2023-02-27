# How to contribute to documentation

If you feel like a contribution to Selene documentation,
first of all stick to the same [contributing rules][contributing]
as for source code.
One key difference: name your git branch
starting with prefix `docs-`  
For instance, `docs-faq-custom-command` or `docs-ci-improve`

Before you start,
we recommend reading our two short pages:

- [How to organize docs][organizing-docs]
- [How to write docs][writing-docs]

Before you ask, look through existing documentation pages and their raw view
as source of accepted style, formatting, used UI blocks and so on.

## How to preview docs

### Local deploy

For local docs deploy:

1. Get Selene code (clone / fork repo or pull PR)
2. In project root directory, execute:

    `poetry install --with docs`

3. Activate Python virtual environment. The easiest way is:

    `poetry shell`

4. Run mkdocs' local web server:

    `mkdocs serve`

5. Open printed URL in browser, e.g. `http://127.0.0.1:8000/selene/`

While server is running, any saved changes in `docs` directory
will reload the browser tab.

To stop server press ++ctrl+c++ in your terminal
(where server was running).

<!-- markdownlint-disable MD046 -->
!!! note "Editing included pages"

    When you edit documents which are located in project **root** directory,
    and they are included (as snippets) to other pages
    (for example, `README.md` is included in `index.md`).
    you ==have to== reload (stop & start) local web server manually.
    After that changes in included pages are displayed on website
    (because `mkdocs serve` watches only for file in `docs` folder).
<!-- markdownlint-enable MD046 -->

### Web deploy (to preview docs website)

<!-- markdownlint-disable MD046 -->
!!! danger "Not available at this moment"

    It's required additional setup (not so trivial)
    to deploy your fork's branch and preview docs changes online.
    Someday we add this feature, I hope.
    At least, when you open pull-request (PR) and make new pushes into it.
    In the meantime,
    you should carefully check your pages (or changes) locally,
    baring in mind that some things might not work on your local server.
<!-- markdownlint-enable MD046 -->

## How to validate Markdown syntax

### Using VS Code extension

Install [markdownlint][markdownlint-extension] for VS Code.

Open **Problems** tab in VS Code ++ctrl+shift+m++. All markdownlint warnings rows start with `MD###`.

<!-- markdownlint-disable MD046 -->
??? tip "How to suppress linter's warnings MD041 and MD046 in VS Code"

    Using snippets, meta-data and other not supported Markdown syntax,
    in many cases H1 won't be the first line of the page
    and MD041 warning will appear for those documents.
    If it's distracting you, disable it in configuration file (see below).

    The similar thing for non-standard indented MarkDown blocks (MD046).
    Besides configuring it,
    you have to add special comment lines wrapping target text
    and temporarily disabling (suppressing) linter's check for that text:

    ```md
    <!-- markdownlint-disable MD046 -->  
    !!! info

        Example text of Info block.
    <!-- markdownlint-enable MD046 -->    
    ```

    To configure `markdownlint` you can use `setting.json` in VS Code.
    Add these line to your settings (configuration file).

    ```json
        // markdownlint
        "markdownlint.config": {
            "MD041": false,
            "MD046": { "style": "fenced"},
            "MD007": { "indent": 4},
        },
    ```

    **Note:** Someday we will add `markdownlint`'s configuration file
    in the project root, and you will be able to remove this settings
    from VS Code.
<!-- markdownlint-enable MD046 -->

### Using plugin for PyCharm

There is a plugin for PyCharm - [Vale CLI][vale-cli-plugin],
which let you lint your Markdown files for
[GitHub-Flavored Markdown rules][vale-github-flavored-markdown]
in realtime (while you typing).

Also you can use PyCharm's terminal in conjunction with
[Awesome Console][awesome-console-plugin] plugin
and different CLI linters.
The most popular tools among them are:

- [markdownlint-cli2][markdownlint-cli2-github] (Node.js is required)
- [pymarkdown][pymarkdown-linter] (Python is required)
- [markdownlint-cli][markdownlint-cli1-github] (Node.js is required)

### Using npm package

If you have Node.js installed on your machine, you can use `markdownlint-cli2`
A fast, flexible, configuration-based command-line interface
for linting Markdown/CommonMark files with the `markdownlint` library.
This library (engine) is used in VS Code extension, mentioned above.

For installation and usage of this CLI utility,
please refer to its [GitHub page][markdownlint-cli2-github].

### Using CI job

<!-- markdownlint-disable MD046 -->
!!! note ""

    We plan to add CI job (or step) with `pre-commit` execution,
    which will lint all MarkDown documents for you.
    Just bear with us while we implement this task.

<!-- markdownlint-enable MD046 -->

<!-- References -->
[contributing]: to-source-code-guide.md
[markdownlint-extension]: https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint
[vale-cli-plugin]: https://plugins.jetbrains.com/plugin/19613-vale-cli
[vale-github-flavored-markdown]: https://vale.sh/docs/topics/scoping/#markdown
[awesome-console-plugin]: https://plugins.jetbrains.com/plugin/7677-awesome-console
[markdownlint-cli2-github]: https://github.com/DavidAnson/markdownlint-cli2
[pymarkdown-linter]: https://github.com/jackdewinter/pymarkdown
[markdownlint-cli1-github]: https://github.com/igorshubovych/markdownlint-cli
[organizing-docs]: how-to-organize-docs-guide.md
[writing-docs]: how-to-write-docs-guide.md
