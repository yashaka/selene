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

[![Sign up for a course https://autotest.how/sdet-start](https://img.shields.io/badge/course-sign_up-blue)](https://autotest.how/sdet-start)
[![Запишись на курс https://autotest.how/sdet-start-ru](https://img.shields.io/badge/%D0%BD%D0%B0%D0%B1%D0%BE%D1%80-%D0%BD%D0%B0%20%D0%BA%D1%83%D1%80%D1%81-red)](https://autotest.how/sdet-start-ru)
[![Реєструйся на курс https://autotest.how/sdet-start-uk](https://img.shields.io/badge/%D0%BD%D0%B0%D0%B1%D1%96%D1%80-%D0%BD%D0%B0_%D0%BA%D1%83%D1%80%D1%81-yellow)](https://autotest.how/sdet-start-uk)

Main features:

- **User-oriented API for Selenium Webdriver** (code like speak common English)
- **Ajax support** (Smart implicit waiting and retry mechanism)
- **PageObjects support** (all elements are lazy-evaluated objects)
- **Automatic driver management** (no need to install and setup driver for quick local execution)

Selene was inspired by [Selenide][selenide] from Java world.

Tests with Selene can be built either in a simple straightforward "selenide" style or with PageObjects composed from Widgets i.e. reusable element components.

- [Versions](#versions)
    - [Migration Guide](#migration-guide)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
    - [Quick Start](#quick-start)
    - [Core API](#core-api)
    - [Automatic Driver and Browser Management](#automatic-driver-and-browser-management)
    - [Advanced API](#advanced-api)
- [Tutorials](#tutorials)
- [Examples](#more-examples)
- [Contribution](#contribution)
- [Release Workflow](#release-workflow)
- [Changelog](#changelog)

## Versions

- Latest recommended version to use is [2.0.0b17+][latest-recommended-version]
    - it's a completely new version of selene, with improved API and speed
    - supports Python `3.7+`
    - bundled with Selenium `4.1+`
    - it's incompatible with [1.x][brunch-ver-1]
    - current master branch is pointed to 2.x
    - yet in alpha/beta stage, refining API, improving "migratability" and testing
    - most active Selene users already upgraded to 2.0 alpha/beta 
      and have been using it in production during last 2 years
    - the only risk is API changes, 
      some commands are in progress of deprecation and renaming
- Latest version marked as stable is: [1.0.2][selene-stable]
    - its sources and corresponding README version
    can be found at [1.x][brunch-ver-1] branch.
    - supports python `2.7, 3.5, 3.6, 3.7`

THIS README DESCRIBES THE USAGE OF THE PRE-RELEASE version of Selene. For older docs look at [1.x][brunch-ver-1] branch.

### Migration guide

From `1.0.2` to `2.0.0b<LATEST>`:

- upgrade to Python 3.7+
- update selene to `2.0.0b<LATEST>`
    - find&replace the `collection.first()` method from `.first()` to `.first`
    - ensure all conditions like `text('foo')` are used via `be.*` or `have.*` syntax
        - example:
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
    - fix another broken imports if available
    - run tests, read deprecation warnings, and refactor to new style recommended in warning messages

## Prerequisites

[Python 3.7+][python-37]

Given [pyenv][pyenv] installed, installing needed version of Python is pretty simple:

```plain
$ pyenv install 3.7.3
$ pyenv global 3.7.3
$ python -V
Python 3.7.3
```

## Installation

### via poetry + pyenv (recommended)

GIVEN [poetry][poetry] and [pyenv][pyenv] installed ...

AND

```plain
poetry new my-tests-with-selene
cd my-tests-with-selene
pyenv local 3.7.3
```

WHEN latest pre-release recommended version:

```plain
poetry add selene --allow-prereleases
```

WHEN latest stable version:

```plain
poetry add selene
```

THEN

```plain
poetry install
```

### via pip

Latest recommended pre-release alpha version:

```plain
pip install selene --pre
```

Latest stable version:

```plain
pip install selene
```

### from sources

GIVEN webdriver and webdriver_manager are already installed

THEN

```plain
git clone https://github.com/yashaka/selene.git
python setup.py install
```

or using pip:

```plain
pip install git+https://github.com/yashaka/selene.git
```

## Usage

### Quick Start

Simply...

```python
from selene import browser, by, be, have

browser.open('https://google.com/ncr')
browser.element(by.name('q')).should(be.blank)\
    .type('selenium').press_enter()
browser.all('#rso>div').should(have.size_greater_than(5))\
    .first.should(have.text('Selenium automates browsers'))
```

OR with custom setup

```python
from selene import browser, by, be, have

browser.config.driver_name = 'firefox'
browser.config.base_url = 'https://google.com'
browser.config.timeout = 2
# browser.config.* = ...

browser.open('/ncr')
browser.element(by.name('q')).should(be.blank) \
    .type('selenium').press_enter()
browser.all('#rso>div').should(have.size_greater_than(5)) \
    .first.should(have.text('Selenium automates browsers'))
```

OR more Selenide from java style:

```python
from selene import browser, by, be, have
from selene.support.shared import config
from selene.support.shared.jquery_style import s, ss


config.browser_name = 'firefox'
config.base_url = 'https://google.com'
config.timeout = 2
# config.* = ...

browser.open('/ncr')
s(by.name('q')).should(be.blank) \
    .type('selenium').press_enter()
ss('#rso>div').should(have.size_greater_than(5)) \
    .first.should(have.text('Selenium automates browsers'))
```

### Core Api


```python

# Given:
from selenium.webdriver import Chrome

# AND chromedriver executable available in $PATH

# WHEN:
from selene import Browser, Config

browser = Browser(
    Config(
        driver=Chrome(),
        base_url='https://google.com',
        timeout=2,
    )
)

# AND:
browser.open('/ncr')

# AND:
# browser.element('//*[@name="q"]')).type('selenium').press_enter()
# OR...
# browser.element('[name=q]')).type('selenium').press_enter()
# OR...
from selene import by
# browser.element(by.name('q')).type('selenium').press_enter()
# OR...for total readability
query = browser.element(by.name('q'))
# actual search doesn't start on calling browser.element above, 
# i.e. the element is "lazy"... or in other words it serves as locator         
# Below, on calling actual first action, 
#     ⬇ the actual webelement is located first time
query.type('selenium').press_enter()       
#                      ⬆
#                  and here it's located again, i.e. the element is "dynamic"

# AND in case we need to filter collection of items 
#     by some condition like visibility:

from selene import be
results = browser.all('#rso>div').by(be.visible)

# THEN we can assert some condition:
from selene import have
# results.should(have.size_greater_than(5))
# results.first.should(have.text('Selenium automates browsers'))
# OR...
results.should(have.size_greater_than(5))\
    .first.should(have.text('Selenium automates browsers'))

# FINALLY the browser can be quit:
browser.quit()
# but it's not mandatory, because by default Selenes kills all drivers on exit
# that can be disabled by:
browser.config.hold_driver_at_exit = True
```

### Automatic Driver and Browser Management

Instead of:

```python
from selenium.webdriver import Chrome
from selene import Browser, Config

browser = Browser(
    Config(
        driver=Chrome(),
        base_url='https://google.com',
        timeout=2
    )
)

browser.open('/ncr')
```

You can simply use the browser instance predefined for you in `selene` module:

```python
from selene import browser

browser.config.base_url = 'https://google.com'
browser.config.timeout = 2

browser.open('/ncr')
```

So you don't need to create you driver instance manually. It will be created for you automatically.

Yet, if you need some special case, like working with remote driver, etc., you can still use shared browser object with additional configuration:

```python
from selenium import webdriver
from selene import browser

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--disable-notifications')
options.add_argument('--disable-extensions')
options.add_argument('--disable-infobars')
options.add_argument('--enable-automation')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-setuid-sandbox')
browser.config.driver_options = options
browser.config.driver_remote_url = 'http://localhost:4444/wd/hub', 
browser.config.base_url = 'https://google.com'
browser.config.timeout = 2

browser.open('/ncr')
...
```

But if you like to create the driver on your own, you can do it too:

```python
from selenium import webdriver
from selene import browser

options = webdriver.ChromeOptions()
options.add_argument('--headless')
# ... other arguments
browser.config.driver = webdriver.Remote(
  'http://localhost:4444/wd/hub', 
  options=options
)
# Once you start to build and set the driver on your own,
# probably you are going to fully manage it life cycle,
# thus, consider disabling the automatic driver reset on browser.open
# if driver was crashed or quit:
browser.config._reset_not_alive_driver_on_get_url = False
# And consider disabling the automatic driver quit on exit:
browser.config.hold_driver_at_exit = True
# Other common options will still be useful:
browser.config.base_url = 'https://google.com'
browser.config.timeout = 2

browser.open('/ncr')
...

# Finally, you can quit the driver manually:
browser.quit()
```

### Advanced API

Sometimes you might need some extra things to reach your specific goals... Here go examples of Selene's `command`, `query`, custom conditions, `.matching(condition)` and `.wait_until(condition)`...

```python
from selene import browser, have

...

###################################################
# Maybe you need some advanced actions on elements,
# e.g. for workaround something through js:

from selene import command

browser.element('#not-in-view').perform(command.js.scroll_into_view)

...

###################################################
# Probably you think that will need something like:

from selene import query

...

def my_int_from(text):
    return int(text.split(' ')[0])

product_text = browser.element('#price-label').get(query.text)
# ... to assert something not standard:
price = my_int_from(product_text)
assert price > 100

# But such version is very unstable in dynamic web world...
# Usually it's...
# either better to implement your custom condition:

from selene.core.condition import Condition
from selene.core.conditions import ElementCondition
from selene.core.entity import Element


def have_in_text_the_int_number_more_than(number) -> Condition[Element]:
    def fn(element: Element) -> None:
        text = element.get(query.text)
        parsed_number = my_int_from(text)
        if not parsed_number > number:
            raise AssertionError(
                f'actual text was: {text}'
                f'with parsed int number: {parsed_number}'
            )
    return ElementCondition(
        f'has in text the int number more than: {number}', 
        fn
    )


browser.element('#price-label').should(
    have_in_text_the_int_number_more_than(100)
)
'''
# You even can create your own project_package/selene_extensions/have.py
# with the following content:

from selene.support.conditioins.have import *

def int_number_more_than(number) -> Condition[Element]:
    def fn(element: Element) -> None:
        text = element.get(query.text)
        parsed_number = my_int_from(text)
        if not parsed_number > number:
            raise AssertionError(
                f'actual text was: {text}'
                f'with parsed int number: {parsed_number}'
            )
    return ElementCondition(
        f'has in text the int number more than: {number}', 
        fn
    )
    
# And then in your test:

from project_package.selene_extensions import have

browser.element('#price-label').should(have.text('Price: ') \
    .should(have.int_number_more_than(100))

# i.e. using it same style as in selene,
# with also access to all original selene conditions
'''

# Such condition-based alternative to the original `assert price > 100` is less fragile,
# because Python's `assert` does not have "implicit waiting",
# while Selene's `should` command does have ;)

# Furthermore, the good test is when you totally control your test data, 
# and the code like below:

product = browser.element('#to-remember-for-future')

product_text_before = product.get(query.text)
price_before = my_int_from(product_text_before)

... # some test steps

product_text_after = product.get(query.text)
price_after = my_int_from(product_text_after)

assert price_after > price_before

# – normally, should be refactored to something like:

product = browser.element('#to-remember-for-future')

product.should(have.text('100$'))

... # some test steps

product.should(have.text('125$'))


###############################################
# You might also think you need something like:

from selene import query

if browser.element('#i-might-say-yes-or-no').get(query.text) == 'yes':
    ...  # do something...

# Or:

from selene import query

if browser.all('.option').get(query.size) >= 2:
    ...  # do something...

# – maybe, one day, you really find a use case:)

# But for above cases, probably easier would be:

if browser.element('#i-might-say-yes-or-no').wait_until(have.text('yes')):
    ...  # do something

...

if browser.all('.i-will-appear').wait_until(have.size_greater_than_or_equal(2)):
    ...  # do something

# Or, by using non-waiting versions, if "you are in a rush:)":

if browser.element('#i-might-say-yes-or-no').matching(have.text('yes')):
    ...  # do something

...

if browser.all('.i-will-appear').matching(have.size_greater_than_or_equal(2)):
    ... # do something
```

## Tutorials

TBD

## More Examples

- [Project template][project-template]

TBD

## Contribution

[see CONTRIBUTING.md][contribution]

## Release Workflow

[see Release workflow][release-workflow]

## Changelog

[see CHANGELOG.md][changelog]

<!-- References -->
[selenide]: http://selenide.org/
[latest-recommended-version]: https://pypi.org/project/selene/2.0.0rc2/
[brunch-ver-1]: https://github.com/yashaka/selene/tree/1.x
[selene-stable]: https://pypi.org/project/selene/1.0.2/
[python-37]: https://www.python.org/downloads/release/python-370/
[pyenv]: https://github.com/pyenv/pyenv
[poetry]: https://python-poetry.org/
[project-template]: https://github.com/yashaka/python-web-test
<!-- --8<-- [end:githubSection] -->

<!-- GitHub only references -->
[contribution]: https://yashaka.github.io/selene/contribution/to-source-code-guide/
[release-workflow]: https://yashaka.github.io/selene/contribution/release-workflow-guide/
[changelog]: https://yashaka.github.io/selene/changelog/
