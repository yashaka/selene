# How to write documentation

All documentation files should be written in Markdown documents (`.md`).

If you are not familiar with the Markdown syntax, check out Adam Pritchard's [Markdown Cheatsheet][markdown-cheatsheet] which includes the standard Markdown syntax as well as the extended GFM (GitHub Flavored Markdown) that we will be utilizing in this guide.

[markdown-cheatsheet]: https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet

For consistency reason, we recommend you to use syntax given in this guide
(*not using available alternatives*)

## Preferred Markdown syntax

### Headers

- Use hash (pound) character(s) to define H1-H6 headers.

`# H1`  
`## H2`  
`### H3`  
`#### H4`  
`##### H5`  
`###### H6`  

### Emphasis

- Use asterisks (\*) for emphasis (aka italics).
- Use double asterisks (\**) for strong emphasis (aka bold).
- Use double tilde (~~) for strikethrough text.
- Use double equals (==) for highlighted text.

<!-- markdownlint-disable MD046 -->
=== "Markdown"

    ```plain
    I'm *italics* text.  
    I'm **bold** text.  
    I'm ~~strikethrough~~ text.  
    I'm ==highlighted== text.
    ```

=== "Result"

    I'm *italics* text.  
    I'm **bold** text.  
    I'm ~~strikethrough~~ text.  
    I'm ==highlighted== text.
<!-- markdownlint-enable MD046 -->

### Lists

- Use hyphen `-` followed by space for unordered list.
- Use **four** spaces indentation for unordered lists.  
(in standard syntax it is two spaces,
and `markdownlint` will show warning MD007,
disable it or configure to 4 spaces in config file)
- Use four spaces indentation for paragraphs within list items (after blank line).
- To have a line break without a paragraph, you will need to use two trailing spaces.

<!-- markdownlint-disable MD046 -->
=== "Markdown"

    ```plain
    1. First ordered list item
    2. Another item
        - Unordered item
            - Nested item
    3. Third item

        Blank line and four space indentation for paragraph.
        This line  
        was interrupted by two trailing spaces.
    ```

=== "Result"

    1. First ordered list item
    2. Another item
        - Unordered item
            - Nested item
    3. Third item

        Blank line and four space indentation for paragraph.
        This line  
        was interrupted by two trailing spaces.
<!-- markdownlint-enable MD046 -->

### Links

- Use the reference links wherever possible, instead of inline-style links.
- Reference text can be arbitrary and case-insensitive,
but use words in lower case separated by hyphen(s).
- For relative links to other pages in `docs` folder,
don't forget extension `.md`
- In rare and reasonable cases, you can use an inline-style link.
- Place link definition(s) throughout the content of a document,
immediately after paragraph (or semantic block) where it was mentioned.
Preferably, in order of their appearance in the text.
There might be exceptions for individual documents, where the list of link
definitions at the end of a document is a reasonable idea.

<!-- markdownlint-disable MD046 -->
=== "Markdown"

    ```markdown
    [Selene][selene-github] is cool,  
    especially with good [docs][home-docs].  
    [I'm an inline-style link](https://t.me/selene_py_ru)

    [selene-github]: https://github.com/yashaka/selene/
    [home-docs]: ../index.md
    ```

=== "Result"

    [Selene][selene-github] is cool, 
    especially with good [docs][home-docs].  
    [I'm an inline-style link](https://t.me/selene_py_ru)

    [selene-github]: https://github.com/yashaka/selene/
    [home-docs]: ../index.md
<!-- markdownlint-enable MD046 -->

### Images

- For better accessibility, we encourage you
to specify alt text and title for images.
- If you need to make new picture(s) for page,
please use external optimization tools
(for example,
[Squoosh][squoosh-app],
[TinyPNG][tiny-png-app] and
[SVGOMG][svgomg-app])
to shrink your images,
before you commit them to git repository.
- Put your new images in `assets` subfolder for each section
(/learn-basics/, /faq/, /use-cases/, etc.).
For example `./docs/faq/assets/chrome-driver-window.png`
and use relative URL to it (see example below).
- Use popular formats for your images, like JPEG, PNG, WebP and SVG.

[squoosh-app]: https://squoosh.app/
[tiny-png-app]: https://tinypng.com/
[svgomg-app]: https://jakearchibald.github.io/svgomg/

<!-- markdownlint-disable MD046 -->
=== "Markdown"

    ```markdown
    Here's our logo (hover to see the title text):

    Inline-style: 
    ![Relative to outside path](../assets/images/logo-icon.png "Selene logo")

    Reference-style: 
    ![alt text][logo]

    [logo]: ../assets/images/logo-icon.png "Title in link definition"
    ```

=== "Result"

    Here's our logo (hover to see the title text):

    Inline-style: 
    ![selene logo](../assets/images/logo-icon.png "Selene logo")

    Reference-style: 
    ![alt text][logo]

    [logo]: ../assets/images/logo-icon.png "Title in link definition"
<!-- markdownlint-enable MD046 -->

### Code and Syntax Highlighting

- Use only fenced code blocks (fenced by lines with three back-ticks ```).
- Write language identifier right after back-ticks (**without space**).
- For plain text (console output) use `plain` language identifier.
- In Python code use only single quotes, i.e. `'This is string'`
- Do NOT use disinformative names for variables and uncommon abbreviations (might be exception for a variable used in a one-line lambda expression).

<!-- markdownlint-disable MD046 -->
=== "Markdown"

    ````plain
    ```python
    from selene import browser
    from selene import by, be, have

    browser.open('https://google.com/ncr')
    browser.element(by.name('q')).should(be.blank)\
    .type('selenium').press_enter()
    browser.all('.srg .g').should(have.size(10))\
    .first.should(have.text('Selenium automates browsers'))
    ``` 
    ````

=== "Result"

    ```python
    from selene import browser
    from selene import by, be, have

    browser.open('https://google.com/ncr')
    browser.element(by.name('q')).should(be.blank)\
    .type('selenium').press_enter()
    browser.all('.srg .g').should(have.size(10))\
    .first.should(have.text('Selenium automates browsers'))
    ```
<!-- markdownlint-enable MD046 -->

### Horizontal Rule

- Use three hyphens (minuses) `---` between to blank lines
to insert horizontal rule
(if you really need to do that)

<!-- markdownlint-disable MD046 -->
=== "Markdown"

    ```plain
    text above the line

    ---

    text under the line
    ```

=== "Result"

    text above the line

    ---

    text under the line
<!-- markdownlint-enable MD046 -->

### Line Breaks

- Use **two trailing space every time**
when you want to insert new line in the same paragraph
on rendered page too (analog `<br>` in HTML).
- Use [semantic linefeeds][semantic-linefeeds],
wrapping lines by 72-80 characters
==except== for links and images and .md files in project root
(unfortunately, GitHub renders each newline character).
- Paragraphs are separated by a blank line.

[semantic-linefeeds]: https://rhodesmill.org/brandon/2012/one-sentence-per-line/

<!-- markdownlint-disable MD046 -->
=== "Markdown"

    ```plain
    Selene was inspired by Selenide from Java world.

    Tests with Selene can be built either in
    a simple straightforward "selenide' style
    or with PageObjects composed from Widgets
    i.e.  
    reusable element components.
    ```

=== "Result"

    Selene was inspired by Selenide from Java world.

    Tests with Selene can be built either in
    a simple straightforward "selenide' style
    or with PageObjects composed from Widgets
    i.e.  
    reusable element components.
<!-- markdownlint-enable MD046 -->

### Footnotes, Tables, Blockquotes

<!-- markdownlint-disable MD046 -->
!!! info

    Such blocks as: **Footnotes**, **Tables**, **Blockquotes**, **Inline HTML**
    are the same as described in the [cheat sheet][markdown-cheatsheet], mentioned at the beginning of this page.
    Please, refer to it.
<!-- markdownlint-enable MD046 -->

### Material theme blocks

#### Admonitions

Admonitions, also known as *call-outs*,
are an excellent choice for including side content
without significantly interrupting the document flow.
How to use them, please, refer to the
[Admonitions][admonitions-reference] reference page.

[admonitions-reference]: https://squidfunk.github.io/mkdocs-material/reference/admonitions/

Our recommendations:

- Try to avoid several admonitions in a row
(even with different types).
- Place link definition after the content of the block
followed by one blank line (indented by four spaces, as the content).

<!-- markdownlint-disable MD046 -->
=== "Markdown"

    ```markdown
    <!-- markdownlint-disable MD046 -->
    !!! info "Example of inserting a link into admonition"

        There are several [types][admontion-types] of admonitions

        [admontion-types]: https://squidfunk.github.io/mkdocs-material/reference/admonitions/#supported-types
    <!-- markdownlint-enable MD046 -->
    ```
    <!-- markdownlint-disable MD046 -->

=== "Result"

    !!! info "Example of inserting a link into admonition"

        There are several [types][admontion-types] of admonitions

        [admontion-types]: https://squidfunk.github.io/mkdocs-material/reference/admonitions/#supported-types
<!-- markdownlint-enable MD046 -->

#### Other

There are many other special formatting blocks,
supported by Material theme for MkDocs.
You can see all of them on [Reference page][material-reference-page].
Before using available (free) blocks,
check that they are enabled (configured) in `mkdocs.yml` configuration file
(`markdown_extensions:` setting for most of them)
and discuss with project owner or other contributors
should you insert (use) them or not.

[material-reference-page]: https://squidfunk.github.io/mkdocs-material/reference/
