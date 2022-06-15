# Selene - User-oriented Web UI browser tests in Python (Selenide port)

[![tests](https://github.com/yashaka/selene/actions/workflows/tests.yml/badge.svg)](https://github.com/yashaka/selene/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/yashaka/selene/branch/master/graph/badge.svg)](https://codecov.io/gh/yashaka/selene)
![Free](https://img.shields.io/badge/free-open--source-green.svg)
[![MIT License](http://img.shields.io/badge/license-MIT-green.svg)](https://github.com/yashaka/selene/blob/master/LICENSE)
[![Project Template](http://img.shields.io/badge/project-template-9cf.svg)](https://github.com/yashaka/python-web-test)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Downloads](https://pepy.tech/badge/selene)](https://pepy.tech/project/selene)

![GitHub stats in](https://raw.githubusercontent.com/yashaka/selene/traffic/traffic-selene/in_2021.svg)
![GitHub views](https://raw.githubusercontent.com/yashaka/selene/traffic/traffic-selene/views.svg)
![GitHub views per week](https://raw.githubusercontent.com/yashaka/selene/traffic/traffic-selene/views_per_week.svg)
![GitHub clones](https://raw.githubusercontent.com/yashaka/selene/traffic/traffic-selene/clones.svg)
![GitHub clones per week](https://raw.githubusercontent.com/yashaka/selene/traffic/traffic-selene/clones_per_week.svg)

[![Join telegram chat https://t.me/selene_py](https://img.shields.io/badge/chat-telegram-blue)](https://t.me/selene_py)
[![Присоединяйся к чату https://t.me/selene_py_ru](https://img.shields.io/badge/%D1%87%D0%B0%D1%82-telegram-red)](https://t.me/selene_py_ru)

[![Sign up for a course http://autotest.how/selene](https://img.shields.io/badge/course-sign_up-blue)](http://autotest.how/selene)
[![Запишись на курс http://autotest.how/selene-ru](https://img.shields.io/badge/%D0%BD%D0%B0%D0%B1%D0%BE%D1%80-%D0%BD%D0%B0%20%D0%BA%D1%83%D1%80%D1%81-red)](http://autotest.how/selene-ru)
[![Учи Selene https://leanpub.com/selene-automation-ru](https://img.shields.io/badge/%D0%BA%D0%BD%D0%B8%D0%B3%D0%B0-leanpub-red)](https://leanpub.com/selene-automation-ru)
[![Реєструйся на курс http://autotest.how/selene-uk](https://img.shields.io/badge/%D0%BD%D0%B0%D0%B1%D1%96%D1%80-%D0%BD%D0%B0_%D0%BA%D1%83%D1%80%D1%81-yellow)](http://autotest.how/selene-uk)


Main features:

- **User-oriented API for Selenium Webdriver** (code like speak common English)
- **Ajax support** (Smart implicit waiting and retry mechanism)
- **PageObjects support** (all elements are lazy-evaluated objects)
- **Automatic driver management** (no need to install and setup driver for quick local execution)


Selene was inspired by [Selenide](http://selenide.org/) from Java world.

Tests with Selene can be built either in a simple straightforward "selenide' style or with PageObjects composed from Widgets i.e. reusable element components.

## Table of content

* [Versions](#versions)
    * [Migration Guide](#migration-guide)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Usage](#usage)
    * [Quick Start](#quick-start)
    * [Core API](#core-api)
    * [Automatic Driver and Browser Management](#automatic-driver-and-browser-management)
    * [Advanced API](#advanced-api)
* [Tutorials](#tutorials)
* [Examples](#more-examples)
* [Contributing](#contributing)
* [Release Process](#release-process)
* [Changelog](#changelog)

## Versions
  
* Latest recommended version to use is >= [2.0.0b4](https://pypi.org/project/selene/2.0.0b4/)
  * it's a completely new version of selene, with improved API and speed
  * supports 3.7 <= python <= 3.9,
  * bundled with Selenium = 4.1
  * it's incompatible with [1.x](https://github.com/yashaka/selene/tree/1.x)
  * current master branch is pointed to 2.x
  * yet in alpha/beta stage, refining API, improving "migratability", and testing
  * it looks pretty stable, most users already upgraded to 2.0 alpha/beta

* Latest version marked as stable is: [1.0.2](https://pypi.org/project/selene/1.0.2/)
  * it is main version used by most selene users during last 2 years
  * it was proven to be stable for production use
  * its sources and corresponding README version can be found at [1.x](https://github.com/yashaka/selene/tree/1.x) branch.
  * supports python 2.7, 3.5, 3.6, 3.7
  
THIS README DESCRIBES THE USAGE OF THE PRE-RELEASE version of Selene. For older docs look at [1.x](https://github.com/yashaka/selene/tree/1.x) branch.
  
### Migration guide

From 1.0.1 to 2.0.0aLATEST:
* upgrade to python 3.7
* update selene to 2.0.0aLATEST
  * find&replace the `collection.first()` method from `.first()` to `.first`
  * ensure all conditions like `text('foo')` are used via `be.*` or `have.*` syntax
    * example:
      * find&replace all
        * `(text('foo'))` to `(have.text('foo'))`
        * `(visible)` to `(be.visible)`
      * smarter find&replace (with some manual refactoring)
        * `.should(x, timeout=y)` to `.with_(timeout=y).should(x)`
      * and add corresponding imports: `from selene import be, have`
  * fix another broken imports if available
  * run tests, read deprecation warnings, and refactor to new style recommended in warning messages

## Prerequisites

[Python >= 3.7](https://www.python.org/downloads/release/python-370/)

Given [pyenv](https://github.com/pyenv/pyenv) installed, installing needed version of Python is pretty simple:

    $ pyenv install 3.7.3
    $ pyenv global 3.7.3
    $ python -V
    Python 3.7.3

## Installation

### via poetry + pyenv (recommended)

GIVEN [poetry](https://poetry.eustace.io/) and [pyenv](https://github.com/pyenv/pyenv) installed ...

AND

    $ poetry new my-tests-with-selene
    $ cd my-tests-with-selene
    $ pyenv local 3.7.3

WHEN latest pre-release recommended version:

    $ poetry add selene --allow-prereleases

WHEN latest stable version:

    $ poetry add selene

THEN

    $ poetry install

### via pip

Latest recommended pre-release alpha version:

    $ pip install selene --pre

Latest stable version:

    $ pip install selene

### from sources

GIVEN webdriver and webdriver_manager are already installed

THEN

    $ git clone https://github.com/yashaka/selene.git
    $ python setup.py install

or using pip:

    $ pip install git+https://github.com/yashaka/selene.git
    

## Usage

### Quick Start

Simply...

```python
from selene.support.shared import browser
from selene import by, be, have

browser.open('https://google.com/ncr')
browser.element(by.name('q')).should(be.blank)\
    .type('selenium').press_enter()
browser.all('.srg .g').should(have.size(10))\
    .first.should(have.text('Selenium automates browsers'))
```

OR with custom setup

```python
from selene.support.shared import browser
from selene import by, be, have

browser.config.browser_name = 'firefox'
browser.config.base_url = 'https://google.com'
browser.config.timeout = 2
# browser.config.* = ...

browser.open('/ncr')
browser.element(by.name('q')).should(be.blank)\
    .type('selenium').press_enter()
browser.all('.srg .g').should(have.size(10))\
    .first.should(have.text('Selenium automates browsers'))
```

OR more Selenide from java style:

```python
from selene.support.shared import config, browser
from selene import by, be, have
from selene.support.shared.jquery_style import s, ss


config.browser_name = 'firefox'
config.base_url = 'https://google.com'
config.timeout = 2
# config.* = ...

browser.open('/ncr')
s(by.name('q')).should(be.blank)\
    .type('selenium').press_enter()
ss('.srg .g').should(have.size(10))\
    .first.should(have.text('Selenium automates browsers'))
```

### Core Api

Given:

```python
from selenium.webdriver import Chrome
```

AND chromedriver executable available in $PATH

WHEN:
```python
from selene import Browser, Config

browser = Browser(Config(
    driver=Chrome(),
    base_url='https://google.com',
    timeout=2))
```

AND (uncomment if needed):

```python
# import atexit
# atexit.register(browser.quit)
```

AND:

```python
browser.open('/ncr')
```

AND:

```python
# browser.element('//*[@name="q"]')).type('selenium').press_enter()
# OR...

# browser.element('[name=q]')).type('selenium').press_enter()
# OR...

from selene import by

# browser.element(by.name('q')).type('selenium').press_enter()
# OR...for total readability

query = browser.element(by.name('q'))  # actual search doesn't start here, the element is "lazy"          
     # here the actual webelement is found
query.type('selenium').press_enter()       
                      # and here it's located again, i.e. the element is "dynamic"
```

AND (in case we need to filter collection of items by some condition like visibility):

```python
from selene import be

results = browser.all('.srg .g').filtered_by(be.visible)
```

THEN:

```python
from selene import have

# results.should(have.size(10))
# results.first.should(have.text('Selenium automates browsers'))
# OR...

results.should(have.size(10))\
    .first.should(have.text('Selenium automates browsers'))
```

FINALLY (if not registered "atexit" before):

```python
browser.quit()
```

### Automatic Driver and Browser Management

Instead of:

```python
from selene import Browser, Config

browser = Browser(Config(
    driver=Chrome(),
    base_url='https://google.com',
    timeout=2))
```
You can simply use the browser and config instance predefined for you in `selene.support.shared` module:

```python
from selene.support.shared import browser, config

# ... do the same with browser.*
```
So you don't need to create you driver instance manually. It will be created for you automatically.

Yet, if you need some special case, like working with remote driver, etc., you can still use shared browser object, while providing driver to it through:

```python
config.driver = my_remote_driver_instance
# or
browser.config.driver = my_remote_driver_instance
```

### Advanced API

Sometimes you might need some extra actions on elements, e.g. for workaround something through js:

```python
from selene import command

browser.element('#not-in-view').perform(command.js.scroll_into_view)
```

Probably you think that will need something like:

```python
from selene import query

product_text = browser.element('#to-assert-something-non-standard').get(query.text)
price = my_int_from(product_text)
assert price > 100
```

But usually it's either better to implement your custom condition:

```python
browser.element('#to-assert-something-non-standard').should(have_in_text_the_int_number_more_than(100))
```

Where the `have_in_text_the_int_number_more_than` is your defined custom condition. Such condition-based alternative will be less fragile, because python's assert does not have "implicit waiting", like selene's should ;)


Furthermore, the good test is when you totally control your test data, and instead:

```python
product = browser.element('#to-remember-for-future')

product_text_before = product.get(query.text)
price_before = my_int_from(product_text_before)

# ... do something

product_text_after = product.get(query.text)
price_after = my_int_from(product_text_after)

assert price_after > price_before
```

Normally, better would be to refactor to something like:

```python
product = browser.element('#to-remember-for-future')

product.should(have.text('100$'))

# ... do something

product.should(have.text('125$'))
```
You might think you need something like:

```python
from selene import query

if browser.element('#i-might-say-yes-or-no').get(query.text) == 'yes':
    # do something...
```

Or:

```python
from selene import query

if browser.all('.option').get(query.size) >= 2:
    # do something...
```

Maybe one day, you really find a use case:) But for above cases, probably easier would be:

```python
if browser.element('#i-might-say-yes-or-no').wait_until(have.text('yes')):
    # do something

# ...

if browser.all('.i-will-appear').wait_until(have.size_greater_than_or_equal(2)):
    # do something
```

Or, by using non-waiting versions, if "you are in a rush:)":

```python
if browser.element('#i-might-say-yes-or-no').matching(have.text('yes')):
    # do something

# ...

if browser.all('.i-will-appear').matching(have.size_greater_than_or_equal(2)):
    # do something
```


## Tutorials

TBD

## More examples

* [Project template](https://github.com/yashaka/python-web-test)

TBD

## Contributing

[see CONTRIBUTING.md](https://github.com/yashaka/selene/blob/master/CONTRIBUTING.md)

## Release Process

[see CONTRIBUTING.md#release-process](https://github.com/yashaka/selene/blob/master/CONTRIBUTING.md#release-process)

## Changelog

[see CHANGELOG.md](https://github.com/yashaka/selene/blob/master/CHANGELOG.md)
