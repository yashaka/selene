# How to organize documentation

> We will provide some key points from [MkDocs User Guide][mkdocs-user-guide]
as well as specific notes for Selene documentation.

## File layout

Your documentation source should be written as regular Markdown files
(see [How to write documentation][syntax-guide]),
and placed in the documentation directory.
By default, this directory will be named `docs`
and will exist at the top level of your project,
alongside the `mkdocs.yml` configuration file.

- Name your files with lower case words separated by `-` hyphen.
- Try to pick concise and descriptive filename
(coping the whole header is not always a good idea).
- Tag (label) document type at the end of filename,
separated by `.` (dot) and before `.md` extension,
sticking to the following recommendations:
    - `*.guide.md` - like "long-read" with detailed explanation,
    or article about fundamental things (e.g. `quick-start.guide.md`);
    - `*.howto.md` - document type is more focused on
    solving certain task / issue / problem.
    A good choice for pages in FAQ section.
    Please, avoid duplication of "how-to" in the filename
    (e.g. `custom-chrome-profile.howto.md`)
    - `*.tutorial.md` - step by step instruction
    (e.g. `deploy-selenium-grid.tutorial.md`);
    - `*.example.md` - demonstrates usage of Selene.
    Use Cases section is the right place for these documents
    (e.g. `allure-step-annotations.example.md`)

<!-- markdownlint-disable MD046 -->
!!! warning "Don't use names which begin with a dot"

    Files and directories with names which begin with a dot
    (for example: `.foo.md` or `.bar/baz.md`) are ignored by MkDocs,
    which matches the behavior of most web servers.
    There is no option to override this behavior.
<!-- markdownlint-enable MD046 -->

The file layout you use determines the URLs
that are used for the generated HTML pages.
Given this layout, pages would be generated for the following URLs:

<!-- markdownlint-disable MD046 -->
=== "Layout"

    ```plain
    📁 docs/
    ├── 📁 contribution/
        ├── 📄 to-source-code.guide.md
        └── 📄 code-conventions.guide.md
    ├── 📄 index.md
    └── 📄 license.md
    ```

=== "URLs"

    /contribution/to-source-code.guide/  
    /contribution/code-conventions.guide/  
    /  
    /license/
<!-- markdownlint-enable MD046 -->

## Navigation

The `nav` configuration setting in your `mkdocs.yml` file
defines which pages are included in the global site navigation menu
as well as the structure of that menu.

A minimal navigation configuration could look like this:

```yaml
nav:
    - Home: 'index.md'
    - About: 'about.md'
```

!!! warning "Avoid references to page headers in navigation menu"

```yaml
nav:
# ...
    - Release Process: CONTRIBUTING/#release-process  # This is BAD
```

- Write navigation section / sub-section / page title and related paths
without any quoting  
*(maybe it's contr-intuitive, but it's good for YAML syntax highlighting)*
- After completing new document **don't forget to update
navigation menu** in `mkdocs.yml` file.  
*(If it should be there.)*
- Append (insert) link to your page in folder's (section's) `index.md` file
to have a list with all pages in this section.

## Selene docs structure

Selene has following file layout:

<!-- markdownlint-disable MD046 -->
!!! warning ""

    - Can be out-dated here, please look into `docs` folder
    or ask project owner where to put new document.
    - Some filenames are not real, for demonstration purpose only).
<!-- markdownlint-enable MD046 -->

```plain
📁 docs/
├── 📁 assets
    ├── 📁 images
        ├── 🎨 logo-icon.png
        └── 🎨 favicon.png
├── 📁 contribution/
    ├── 📄 code-conventions.guide.md
    ├── 📄 how-to-organize-docs.guide.md
    ├── 📄 how-to-write-docs.guide.md
    ├── 📄 index.md
    ├── 📄 release-workflow.guide.md
    ├── 📄 to-documentation.guide.md
    └── 📄 to-source-code.guide.md
├── 📁 faq/
    ├── 📁 assets/
        └── 🎨 chrome-driver-window.png
    ├── 📄 index.md
    ├── 📄 q-tbd-1.howto.md
    └── 📄 custom-chrome-profile.howto.md
├── 📁 learn-advanced/
    ├── 📁 assets/
    ├── 📄 index.md
    ├── 📄 learn-deeper-1.tutorial.md
    └── 📄 learn-deeper-2.guide.md
├── 📁 learn-basics/
    ├── 📄 index.md
    ├── 📄 quick-start.tutorial.md
    └── 📄 learn-something.tutorial.md
├── 📁 use-cases/
    ├── 📁 assets/
        └── 🎨 my-pic.png
    ├── 📄 ex-tbd-1.example.md
    ├── 📄 ex-tbd-2.example.md
    └── 📄 index.md
├── 📄 changelog.md
├── 📄 index.md
└── 📄 license.md
```

Pay attention, that:

- `docs/index.md` is almost full include (snippet) of README.md
from the project root (except three links at the end).
Separate links are required because README is rendered on three place:
GitHub, PyPI and Selene documentation website.
- `docs/license.md` and `docs/changelog.md` are full snippets of
LICENSE.md and CHANGELOG.md from the project root.
- `contribution/to-source-code.guide.md` is snippet
of CONTRIBUTING.md from the root
(except two links at the end of the page).
- Images for each section (page type) are located in `assets` subfolder.
- Top `docs/assets` folder contains theme's assets.
- There is an `index.md` in each top section.

How to use snippets, please refer to Markdown
[extension documentation][snippets-doc] page.

## Selene navigation structure

Initial (might be changed in the future) `nav` structure (left panel)
has following items:

```plain
Overview  # -> ./README.md
Learn Basics
    ...
Learn Advanced
    ...
FAQ
    ...
Use Cases
    ...
Contribution
    ...
Changelog
License
```

<!-- References -->
[mkdocs-user-guide]: https://www.mkdocs.org/user-guide/writing-your-docs/
[syntax-guide]: how-to-write-docs.guide.md
[snippets-doc]: https://facelessuser.github.io/pymdown-extensions/extensions/snippets/
