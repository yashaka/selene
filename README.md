<!-- --8<-- [start:githubSection] -->
# Selene: User-Oriented Web UI Browser Tests in Python

![Pre-release Version](https://img.shields.io/github/v/release/yashaka/selene?label=latest)
[![tests](https://github.com/yashaka/selene/actions/workflows/tests.yml/badge.svg)](https://github.com/yashaka/selene/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/yashaka/selene/branch/master/graph/badge.svg)](https://codecov.io/gh/yashaka/selene)
![Free](https://img.shields.io/badge/free-open--source-green.svg)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/yashaka/selene/blob/master/LICENSE)

[![Downloads](https://pepy.tech/badge/selene)](https://pepy.tech/project/selene)
[![web tests template](https://img.shields.io/badge/web-template-9cf.svg)](https://github.com/yashaka/python-web-test)
[![mobile cross-platform tests template](https://img.shields.io/badge/mobile-template-9cf.svg)](https://github.com/yashaka/python-web-test)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![Join telegram chat https://t.me/selene_py](https://img.shields.io/badge/chat-telegram-blue)](https://t.me/selene_py)
[![Присоединяйся к чату https://t.me/selene_py_ru](https://img.shields.io/badge/%D1%87%D0%B0%D1%82-telegram-red)](https://t.me/selene_py_ru)

## Overview of Selene

Selene is a concise and powerful library for writing browser UI tests in Python. It was built as a Pythonic port of the popular Selenide project from the Java world. 
Selene helps developers write readable and maintainable tests that "speak" in common English, making them easier to understand and share across teams.

Selene’s core strength is its user-oriented API, which abstracts the complexity of working with Selenium WebDriver. Tests can be written using simple, expressive syntax and support features like lazy-evaluated elements, automatic retry mechanisms for smarter implicit waiting for Ajax-like loading. With built-in PageObject support, it enables the reusability of web elements through Widgets.

## Table of Contents

- [Main Features](https://github.com/yashaka/selene#main-features)
- [Versions](https://github.com/yashaka/selene#versions)
  - [Migration Guide](https://github.com/yashaka/selene#migration-guide)
- [Prerequisites](https://github.com/yashaka/selene#prerequisites)
- [Installation](https://github.com/yashaka/selene#installation)
- [Usage](https://github.com/yashaka/selene#usage)
  - [Quick Start](https://github.com/yashaka/selene#quick-start)
  - [Core API](https://github.com/yashaka/selene#core-api)
  - [Automatic Driver and Browser Management](https://github.com/yashaka/selene#automatic-driver-and-browser-management)
  - [Advanced API](https://github.com/yashaka/selene#advanced-api)
- [Tutorials](https://github.com/yashaka/selene#tutorials)
- [Examples](https://github.com/yashaka/selene#Examples)
- [Contribution](https://github.com/yashaka/selene#contribution)
- [Release Workflow](https://github.com/yashaka/selene#release-workflow)
- [Changelog](https://github.com/yashaka/selene#changelog)

## Main Features

- **User-oriented API**: Write test scripts in natural language with simple syntax that reads like common English.
- **Ajax-like loading support**: Built-in smart implicit waiting and retry mechanisms to handle dynamically loaded web elements.
- **PageObjects support**: Lazy-evaluated elements allows to build PageObjects composing elements over selectors or `By.*` tuple-like locators, allowing also to create reusable elements for different components.
- **Extended list of expected conditions**: Much bigger list of conditions aka matchers than in raw Selenium allows to implement more readable and concise assertions in tests.
- **Extended list of predefined commands on element**: Reduces the need of composing custom commands with `ActionChains`. 
- **Out of the box support of frames and shadow root**.
- **Flexible filtering of collections**: Allows to build composable locators reducing the need of complex XPath-selectors and results in much more detailed error messages that helps with tests maintenance.
- **Very detailed error messages**: For both actions and assertions on elements.
- **Automatic driver management**: Automatically handles browser driver setup and teardown for quick, local executions.
- **Highly customizable**: Advanced users can configure or extend Selene for specific requirements. For example, you can customize your own selector templates. You also can customize same options (for example timeout) via same API on all levels: 1) globally; 2) on specific browser instance; 3) on specific element or collection of elements stored in a variable 4) for specific action or assertion on element.
- **Support for both local and remote drivers**: Selene supports a variety of environments, including local browsers, headless setups, and cloud services like Selenium Grid – in a similar way that Selenium supports it – by providing the corresponding driver options.
- **Multiplatform support**: Works with web and Appium's mobile or desktop drivers. Though, some options in config are platform-specific.

## Versions

Selene currently supports two major versions:

- **Latest Recommended Pre-Release Version (v2.0.0rc9)**:
  - Python versions: `3.8+`
  - Selenium support: `>=4.12.0`
  - This version introduces an improved API, better performance, and is recommended for new projects.
  - Though is in alpha/beta stage, refining API, improving "migratability" and testing
  - Most active Selene users already upgraded to 2.0 alpha/beta and have been using it in production during last 2 years
  - The only risk is API changes, some commands are in progress of deprecation and renaming

- **Stable Version (v1.0.2)**:
  - Python versions: `2.7, 3.5, 3.6, 3.7`
  - Selenium support: `<4.0.0`
  - Use this version if your project requires compatibility with older Python versions.
  
For migration from v1.x to v2.x, follow the [migration guide](https://github.com/yashaka/selene#migration-guide).

### Migration Guide

From `1.0.2` to `2.0.0rc<LATEST>`:
- Upgrade to Python 3.8+
- Update selene to `2.0.0rc<LATEST>`
  - Replace the `collection.first()` method from `.first()` to `.first`
  - Ensure all conditions like `text('foo')` use the `be.*` or `have.*` syntax
  - Update other deprecated methods as needed

Examples of potential refactoring during migration:
- find&replace all
  - `(text('foo'))` to `(have.text('foo'))`
  - `(visible)` to `(be.visible)`
- smarter find&replace (with some manual refactoring)
  - `.should(x, timeout=y)` to `.with_(timeout=y).should(x)`
  - `.should_not(be.*)` to `.should(be.not_.*)` or `.should(be.*.not_)`
  - `.should_not(have.*)` to `.should(have.no.*)` or `.should(have.*.not_)`
  - `.should_each(condition)` to `.should(condition.each)`
- and add corresponding imports:
  `from selene import be, have`

## Prerequisites

[Python 3.8+][python-38] is required.

Given [pyenv][pyenv] is installed, installing the needed version of Python is simple:
```bash
$ pyenv install 3.8.13
$ pyenv global 3.8.13
$ python -V
Python 3.8.13
```

## Installation

### via Poetry + Pyenv (Recommended)

Ensure [poetry][poetry] and [pyenv][pyenv] are installed, then:
```bash
poetry new my-tests-with-selene
cd my-tests-with-selene
pyenv local 3.8.13
poetry add selene --allow-prereleases  # for pre-release version
poetry install
```

### via Pip

For the pre-release version (recommended for new projects):
```bash
pip install selene --pre
```

For the latest stable version:
```bash
pip install selene
```

### from Sources

If you prefer to install Selene directly from the source code:

```bash
git clone https://github.com/yashaka/selene.git
cd selene
python setup.py install
```

Or using poetry:

```bash
poetry add git+https://github.com/yashaka/selene.git
```

Or using pip:

```bash
pip install git+https://github.com/yashaka/selene.git
```

## Usage

### Quick Start

Automate a simple Google search using Selene:

```python
from selene import browser, be, have

browser.open('https://google.com/ncr')
browser.element('[name=q]').should(be.blank)\
    .type('selenium').press_enter()
browser.all('#rso>div').should(have.size_greater_than(5))\
    .first.should(have.text('Selenium automates browsers'))

# not mandatory, because will be closed automatically:
# browser.quit()
```

### Core API

- Selene provides an intuitive API for interacting with web elements using modules like `be`, `have` or `by`.
- Lazy and Dynamic Elements: Selene elements are lazy and dynamic, meaning they are located each time an action is performed. This ensures interaction with the most up-to-date element.

- Here is a basic element interaction:

```python
from selene import browser, by, be

# because elements are "lazy",
# you can store them in variable:
search_box = browser.element(by.name('q'))

# – even before the actual page will be loaded:
browser.open('https://google.com/ncr')
search_box.should(be.blank).type('Selenium').press_enter()
```

### Selecting Element Locators

Choosing the correct element locators is crucial for reliable tests. Here are some tips:

1. **Inspect the Element:** Right-click on the web element and select Inspect to view its HTML in the browser's developer tools.

2. **Use Unique Attributes:** Look for unique attributes like id, name, or custom attributes to use in your selectors. Best practice is to negotiate with developers on using unique `data-*` attributes specifically for testing needs, like `data-test-id`.

3. **Construct CSS or XPath Selectors:** Build selectors that uniquely identify elements. For example, using conciser css-selectors `#elementId`, `.className`, or `[name="q"]`, or using XPath for things that CSS can't handle: `//*[text()="Submit"]/..`. Selene will automatically detect whether you provide a CSS or XPath selector.

4. **Utilize Selene's Selector Helpers (optional):** If you need most human-readable code, you can use `by.name('q')`, `by.text('Submit')` and other `by.*` helpers. Notice, that someone would prefer raw css selector like `[name=q]` over `by.name('q')` for the purpose of [KISS](https://en.wikipedia.org/wiki/KISS_principle) principle.

5. **Break down long selectors into smaller parts for better readability and maintainability:** If to find an element you have a complex selector like in:  `browser.element('//*[@role="row" and contains(.,"Jon")]//*[@data-field="select-row"]')`, decomposing it utilizing Selene's filtering collections API to `browser.all('[role=row]').element_by(have.text('Jon')).element('[data-field=select-row]')` will make it easier to understand and maintain, because if something changes in the structure of the page, and your test fails, you will see exactly where it fails among "decomposed parts" of the selector, while in case of longer XPath selector you will see only that it fails somewhere in the middle of the long selector with the following need to double-check each potential reason of failure.
  
6. **Create custom selector strategy (optional):** Imagine your frontend developers follow best practices and use `data-test-id` attributes for all elements that need to be covered in tests, and there is a followed naming convention for such element to be snake_case_OR-kebab-case-words. With Selene's `browser.config.selector_to_by_strategy` option you can define a custom selector strategy to automatically detect all such `"snake_kebab-words"` passed as selectors and transform them into `[data-test-id="snake_kebab-words"]` locators. Then an example like `
browser.all('[data-testid=result]').first.element('[data-testid=result-title-a]').click()` can be simplified to `browser.all('result').first.element('result-title-a').click()`. See [How to simplify search by Test IDs?](https://yashaka.github.io/selene/faq/custom-test-id-selectors-howto/) guide for more details.

    *❗This feature will be available in the next release of Selene.️*

### Automatic Driver and Browser Management

Selene can automatically manage the browser driver for you, but you can customize it if needed.

#### **Automatic Driver Management**

- Use the predefined browser instance without manually creating a driver:

```python
from selene import browser

browser.config.base_url = 'https://google.com'
browser.config.timeout = 2

browser.open('/ncr')
```

#### **Custom Driver Setup**

- If you need custom driver settings, such as using a remote driver or adding options, configure the driver accordingly:

```python
from selenium import webdriver
from selene import browser

options = webdriver.ChromeOptions()
options.add_argument('--headless')
# Add other options as needed

# Selene will automatically detect the browser type (Chrome, Firefox, etc.)
# based on the options passed
browser.config.driver_options = options
browser.config.driver_remote_url = 'http://localhost:4444/wd/hub'
browser.config.base_url = 'https://google.com'
browser.config.timeout = 2

browser.open('/ncr')
```

- Alternatively, create and assign your own driver instance:

```python
from selenium import webdriver
from selene import browser

options = webdriver.ChromeOptions()
options.add_argument('--headless')
# Add other options as needed

browser.config.driver = webdriver.Remote(
    command_executor='http://localhost:4444/wd/hub',
    options=options
)

browser.config.base_url = 'https://google.com'
browser.config.timeout = 2

browser.open('/ncr')
```

## Tutorials

- [Selene: Quick Start](https://yashaka.github.io/selene/selene-quick-start-tutorial/)
- [Selene in action](https://yashaka.github.io/selene/selene-in-action-tutorial/)
- [Selene for PageObjects](https://yashaka.github.io/selene/selene-for-page-objects-guide/)

## Tips for Effective Test Automation

- **Use Readable and Stable Selectors:** Aim for selectors that are unique, expressive and minimally coupled with DOM structure to make your tests more maintainable.

- **Encapsulate Reusable Components:** Utilize the Page Object Model to encapsulate elements and actions, promoting code reuse.

- **Leverage Built-in Waiting:** Selene automatically waits for elements to be in the desired state, reducing the need for explicit waits.

- *Explore the API:* Dive into Selene's source code or [documentation](https://yashaka.github.io/selene) to understand the available methods and configurations better.

## Contribution

We welcome contributions to Selene! Here's how you can get involved:

1. **Fork the repository** and clone it locally.
2. Make sure to follow the project’s style and conventions.
3. Submit a pull request (PR) with a clear description of the changes.

For more details, refer to our [contribution guide](https://yashaka.github.io/selene/contribution/to-source-code-guide/).

## Changelog

See the [Changelog](https://yashaka.github.io/selene/changelog/) for more details about recent updates.

<!-- References -->
[selenide]: http://selenide.org/
[latest-recommended-version]: https://pypi.org/project/selene/2.0.0rc9/
[brunch-ver-1]: https://github.com/yashaka/selene/tree/1.x
[selene-stable]: https://pypi.org/project/selene/1.0.2/
[python-38]: https://www.python.org/downloads/release/python-380/
[pyenv]: https://github.com/pyenv/pyenv
[poetry]: https://python-poetry.org/
[project-template]: https://github.com/yashaka/python-web-test
<!-- --8<-- [end:githubSection] -->

<!-- GitHub only references -->
[contribution]: https://yashaka.github.io/selene/contribution/to-source-code-guide/
[release-workflow]: https://yashaka.github.io/selene/contribution/release-workflow-guide/
[changelog]: https://yashaka.github.io/selene/changelog/
