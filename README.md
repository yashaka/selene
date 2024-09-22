<!-- --8<-- [start:githubSection] -->
# Selene - User-oriented Web UI browser tests in Python (Selenide port)

![Pre-release Version](https://img.shields.io/github/v/release/yashaka/selene?label=latest)
[![tests](https://github.com/yashaka/selene/actions/workflows/tests.yml/badge.svg)](https://github.com/yashaka/selene/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/yashaka/selene/branch/master/graph/badge.svg)](https://codecov.io/gh/yashaka/selene)
![Free](https://img.shields.io/badge/free-open--source-green.svg)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/yashaka/selene/blob/master/LICENSE)

[![Downloads](https://pepy.tech/badge/selene)](https://pepy.tech/project/selene)
[![Project Template](https://img.shields.io/badge/project-template-9cf.svg)](https://github.com/yashaka/python-web-test)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![Join telegram chat https://t.me/selene_py](https://img.shields.io/badge/chat-telegram-blue)](https://t.me/selene_py)
[![Присоединяйся к чату https://t.me/selene_py_ru](https://img.shields.io/badge/%D1%87%D0%B0%D1%82-telegram-red)](https://t.me/selene_py_ru)

## Overview of Selene

Selene is a concise and powerful library for writing browser UI tests in Python. It was built as a Pythonic port of the popular Selenide project from the Java world. 
Selene helps developers write readable and maintainable tests that "speak" in common English, making them easier to understand and share across teams.

Selene’s core strength is its user-oriented API, which abstracts the complexity of working with Selenium WebDriver. Tests can be written using simple, expressive syntax and support features like lazy-evaluated elements, automatic retry mechanisms, and Ajax-based waits. With built-in PageObject support, it enables the reusability of web elements through Widgets. 

## Table of Contents
- [Main Features](#main-features)
- [Versions](#versions)
  - [Migration Guide](#migration-guide)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Quick Start](#quick-start)
  - [Core API](#core-api)
  - [Advanced API](#advanced-api)
- [Tutorials](#tutorials)
- [Expanded Examples](#expanded-examples)
- [Contribution](#contribution)
- [Changelog](#changelog)

## Main Features

- **User-oriented API**: Write test scripts in natural language with simple syntax that reads like common English.
- **Ajax support**: Built-in smart implicit waiting and retry mechanisms to handle dynamic web elements.
- **PageObjects support**: Lazy-evaluated PageObjects allow creating reusable elements for different components.
- **Automatic driver management**: Automatically handles browser driver setups for quick, local executions.
- **Highly customizable**: Advanced users can configure or extend Selene for specific requirements.
- **Support for both local and remote drivers**: Selene supports a variety of environments, including local browsers, headless setups, and cloud services like Selenium Grid.

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
  
For migration from v1.x to v2.x, follow the [migration guide](#migration-guide).

### Migration Guide

From `1.0.2` to `2.0.0b<LATEST>`:
- Upgrade to Python 3.7+
- Update selene to `2.0.0b<LATEST>`
  - Replace the `collection.first()` method from `.first()` to `.first`
  - Ensure all conditions like `text('foo')` use the `be.*` or `have.*` syntax
  - Update other deprecated methods as needed

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
For the pre-release version:
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

Or using pip:

```bash
pip install git+https://github.com/yashaka/selene.git
```

## Usage

### Quick Start
- Automate a simple Google search using Selene:

```python
from selene import browser, by, be, have

browser.open('https://google.com/ncr')
browser.element(by.name('q')).should(be.blank)\
    .type('selenium').press_enter()
browser.all('#rso > div').should(have.size_greater_than(5))\
    .first.should(have.text('Selenium automates browsers'))

browser.quit()
```

### Core API
- Selene provides an intuitive API for interacting with web elements using conditions like `be`, `have`, and `commands`.
- Lazy and Dynamic Elements: Selene elements are lazy and dynamic, meaning they are located each time an action is performed. This ensures interaction with the most up-to-date element.

- Here is a basic element interaction:

```python
from selene import browser, by, be

browser.open('https://google.com/ncr')
search_box = browser.element(by.name('q')).should(be.blank)\
    .type('Selenium').press_enter()
```

### Selecting Element Locators
- Choosing the correct element locators is crucial for reliable tests. Here are some tips:

  1. **Inspect the Element:** Right-click on the web element and select Inspect to view its HTML in the browser's developer tools.

  2. **Use Unique Attributes:** Look for unique attributes like id, name, or custom attributes to use in your selectors.

  3. **Construct CSS or XPath Selectors:** Build selectors that uniquely identify elements. For example, #elementId, .className, or [name="q"].

  4. **Utilize Selene's Selector Helpers:** Selene offers helper methods like by.name('q'), by.text('Submit') for cleaner code.


### Automatic Driver and Browser Management
- Selene can automatically manage the browser driver for you, but you can customize it if needed.

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

Here's a quick guide to get you up and running with Selene:

1. **Installation**:
    Install Selene using pip:
    ```bash
    pip install selene --pre
    ```

2. **Setting Up Your First Test**:
    Create a Python file and add the following code to run a basic test:
    ```python
    from selene import browser, by, be

    browser.open('https://google.com/ncr')
    search_box = browser.element(by.name('q')).should(be.blank).type('Selenium').press_enter()
    browser.all('#rso>div').should(have.size_greater_than(5))        .first.should(have.text('Selenium automates browsers'))

    browser.quit()
    ```

3. **Running the Test**:
    Run the script using Python:
    ```bash
    python my_test.py
    ```

This setup covers searching on Google and validating that results are displayed.

## Examples

#### Example 1: Handling AJAX Elements
- This example demonstrates how Selene's built-in waiting system handles AJAX-based web applications
- Selene’s implicit waits will handle AJAX-based loading, retrying actions until elements are ready.

```python
from selene import browser, by, be, have

browser.open('https://example.com/')
browser.element(by.name('search')).type('dynamic content').press_enter()

# Handling AJAX-based elements
browser.all('.results').should(have.size_greater_than(5)).first.should(have.text('Example result'))
```

#### Example 2: Page Object Model with Widgets

- Page Objects in Selene allow you to modularize tests and reuse common components
- This approach makes the test code cleaner and reusable for different scenarios.

```python
from selene import browser, by
from selene.support.shared import config
from selene.support.shared.jquery_style import s, ss

config.browser_name = 'firefox'
config.base_url = 'https://example.com'
config.timeout = 2

class SearchWidget:
    def __init__(self):
        self.search_box = s(by.name('q'))
        self.results = ss('#results')

    def search(self, query):
        self.search_box.should(be.blank).type(query).press_enter()

    def verify_results(self):
        self.results.should(have.size_greater_than(3))

search_widget = SearchWidget()
browser.open('/')
search_widget.search('Selenium automation')
search_widget.verify_results()
browser.quit()
```

## Tips for Effective Test Automation

- **Use Readable Selectors:** Aim for selectors that are both unique and expressive to make your tests more maintainable.

- **Encapsulate Reusable Components:** Utilize the Page Object Model to encapsulate elements and actions, promoting code reuse.

- **Leverage Built-in Waiting:** Selene automatically waits for elements to be in the desired state, reducing the need for explicit waits.

- *Explore the API:* Dive into Selene's source code or documentation to understand the available methods and configurations better.

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