<!-- --8<-- [start:githubSection] -->

# How to contribute

Before implementing your ideas, it is recommended first to create a corresponding issue and discuss the plan to be approved;). Also consider first to help with issues marked with `help_needed` label ;)

1. Find an existing relevant issue or add a new one to this project.
2. Discuss its need and possible implementation. And once approved...
3. [Fork][how-to-fork-project] the [project][selene-fork].
4. Clone your fork of the project

    `git clone https://github.com/[my-github-username]/selene.git`

5. Install [poetry][poetry-org] via `pip install poetry`
6. `cd selene`
7. `poetry install`
8. `poetry shell`
9. Create your feature branch (`git checkout -b my-new-feature`)
10. Stage appropriate changes (via `git add`),

    and commit: `git commit -am "[#$ISSUE_NUMBER] $COMMIT_MESSAGE"`,

    (example: `git commit -am "[#321] TEST: improve tests structure"`)

    where

    - ISSUE_NUMBER is the number of issue this commit relates to  
    - COMMIT_MESSAGE is...

    ```plain
    <type>: <subject>

    <body>
    ```

    where

    `<type>` is one of:

      - NEW: (new feature for the user, not a new feature for build script)
      - FIX: (bug fix for the user, not a fix to a build script)
      - DOCS: (changes to the documentation)
      - STYLE: (formatting, missing semi colons, etc; no production code change)
      - REFACTOR: (refactoring production code, eg. renaming a variable)
      - TEST: (adding missing tests, refactoring tests; no production code change)
      - CHORE: (updating build tasks etc; no production code change)

    `<subject>`

      - summary of "what and why?" (not "how?")
      - is in present tense,  
        in the imperative (e.g. `change` over `changes` or `changed`),  
        <= 50 symbols
      - has no period in the end

    `<body>`

      - More detailed explanatory text if needed. Wrapped to 72 characters.
      - Focused on what and why over how.
      - Separated from `<subject>` with a blank line
      - Further paragraphs come after blank lines.
      - Bullet points are okay, too.
      - Typically, a hyphen or asterisk is used for the bullet, followed by a  single space. Use a hanging indent.

    credits: these commit message conventions based on sources from:

      - [Tim Pope][tim-pope]
      - [@joshbuchea][joshbuchea]
      - [@robertpainsi][robertpainsi]

11. Push to the branch (`git push origin my-new-feature`)
12. Create a new Pull Request

To get more information about contributing,
you can *(and should)* read our
[Code conventions][code-conventions]
and
[Release workflow][release-workflow]
pages.

<!-- References -->
[how-to-fork-project]: https://docs.github.com/en/github/getting-started-with-github/fork-a-repo
[selene-fork]: https://github.com/yashaka/selene/fork
[poetry-org]: https://python-poetry.org
[tim-pope]: https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
[joshbuchea]: https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716
[robertpainsi]: https://gist.github.com/robertpainsi/b632364184e70900af4ab688decf6f53
<!-- --8<-- [end:githubSection] -->

<!-- GitHub only references -->
[code-conventions]: https://yashaka.github.io/selene/contribution/code-conventions-guide/
[release-workflow]: https://yashaka.github.io/selene/contribution/release-workflow-guide/
