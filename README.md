# Selene - User-oriented Web UI browser tests in Python (Selenide port)

[![Build Status](https://travis-ci.org/yashaka/selene.svg?branch=master)](https://travis-ci.org/yashaka/selene)
[![codecov](https://codecov.io/gh/yashaka/selene/branch/master/graph/badge.svg)](https://codecov.io/gh/yashaka/selene)
![Free](https://img.shields.io/badge/free-open--source-green.svg)
[![MIT License](http://img.shields.io/badge/license-MIT-green.svg)](https://github.com/yashaka/selene/blob/master/LICENSE)

[![Gitter](https://badges.gitter.im/gitterHQ/gitter.svg)](https://gitter.im/automician/selene)
[![Присоединяйся к чату https://t.me/selene_py_ru](https://img.shields.io/badge/%D1%87%D0%B0%D1%82-telegram-blue)](https://t.me/selene_py_ru)
[![Учи Selene https://leanpub.com/selene-automation-ru](https://img.shields.io/badge/%D0%BA%D0%BD%D0%B8%D0%B3%D0%B0-leanpub-9cf)](https://leanpub.com/selene-automation-ru)


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
  
* Latest recommended version to use is [2.0.0a18](https://pypi.org/project/selene/2.0.0a18/
)
  * it's a completely new version of selene, with improved API and speed
  * supports python >= 3.7
  * it's incompatible with [1.x](https://github.com/yashaka/selene/tree/1.x)
  * current master branch is pointed to 2.x
  * yet in pre-alpha stage, refining API, improving "migratability", and testing
  * it looks pretty stable, but not fully proven yet
    * mainly tested on production code base of a few users who successfully migrated from 1.x to 2.x

* Latest version marked as stable is: [1.0.1](https://pypi.org/project/selene/1.0.1/)
  * it is main version used by most selene users during last 2 years
  * it was proven to be stable for production use
  * its sources can be found at [1.x](https://github.com/yashaka/selene/tree/1.x) branch.
  * supports python 2.7, 3.5, 3.6, 3.7
  
### Migration guide

GIVEN on 1.0.1:
* upgrade to python 3.7
* update selene to 2.0.0aLATEST
  * find&replace the collection.first() method from `.first()` to `.first`
  * ensure all conditions like `text('foo')` are used via `be.*` or `have.*` syntax
    * example: 
      * find&replace all 
        * `(text('foo'))` to `(have.text('foo'))`
        * `(be.visible)` to `(be.visible)`
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

### poetry + pyenv (recommended)

GIVEN [poetry](https://poetry.eustace.io/) and [pyenv](https://github.com/pyenv/pyenv) installed ...

AND

    $ poetry new my-tests-with-selene
    $ cd my-tests-with-selene
    $ pyenv local 3.7.3
    
WHEN latest stable version:

    $ poetry add selene

WHEN latest pre-release version:

    $ poetry add selene --allow-prereleases

THEN

    $ poetry install

### pip

Latest stable version:

    $ pip install selene

Latest pre-release version:

    $ pip install selene --pre

### from sources

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

    from selenium.webdriver import Chrome

AND chromedriver executable available in $PATH

WHEN:

    from selene import Browser, Config

    browser = Browser(Config(
        driver=Chrome(),
        base_url='https://google.com',
        timeout=2))

AND (uncomment if needed):

    # import atexit
    # atexit.register(browser.quit)

AND:

    browser.open('/ncr')

AND:

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
        
AND (in case we need to filter collection of items by some condition like visibility):

    from selene import be
    
    results = browser.all('.srg .g').filtered_by(be.visible)
    
THEN:
    from selene import have
    
    # results.should(have.size(10))
    # results.first.should(have.text('Selenium automates browsers'))
    # OR...
    
    results.should(have.size(10))\
        .first.should(have.text('Selenium automates browsers'))
        
FINALLY (if not registered "atexit" before):
    
    browser.quit()


### Automatic Driver and Browser Management

Instead of:

    from selene import Browser, Config

    browser = Browser(Config(
        driver=Chrome(),
        base_url='https://google.com',
        timeout=2))
        
You can simply use the browser and config instance predefined for you in `selene.support.shared` module:

    from selene.support.shared import browser, config

    # ... do the same with browser.*
    
So you don't need to create you driver instance manually. It will be created for you automatically. 

Yet, if you need some special case, like working with remote driver, etc., you can still use shared browser object, while providing driver to it through: 

    config.driver = my_remote_driver_instance
    # or
    browser.config.driver = my_remote_driver_instance
    
### Advanced API
    
Sometimes you might need some extra actions on elements, e.g. for workaround something through js:

    from selene import command

    browser.element('#not-in-view').perform(command.js.scroll_into_view)
    
Probably you think that will need something like:

    from selene import query

    product_text = browser.element('#to-assert-something-non-standard').get(query.text)
    price = my_int_from(product_text)
    assert price > 100

But usually it's either better to implement your custom condition:

    browser.element('#to-assert-something-non-standard').should(have_in_text_the_int_number_more_than(100))

Where the ``have_in_text_the_int_number_more_than`` is your defined custom condition. Such condition-based alternative will be less fragile, because python's assert does not have "implicit waiting", like selene's should ;)


Furthermore, the good test is when you totally control your test data, and instead:


    product = browser.element('#to-remember-for-future')

    product_text_before = product.get(query.text)
    price_before = my_int_from(product_text_before)

    # ... do something

    product_text_after = product.get(query.text)
    price_after = my_int_from(product_text_after)

    assert price_after > price_before


Normally, better would be to refactor to something like:

    product = browser.element('#to-remember-for-future')

    product.should(have.text('100$'))

    # ... do something

    product.should(have.text('125$'))


You might think you need something like:

    from selene import query

    if browser.element('#i-might-say-yes-or-no').get(query.text) == 'yes':
        # do something...

Or:

    from selene import query

    if browser.all('.option').get(query.size) >= 2:
        # do something...


Maybe one day, you really find a use case:) But for above cases, probably easier would be:

    if browser.element('#i-might-say-yes-or-no').wait_until(have.text('yes'):
        # do something

    # ...

    if browser.all('.i-will-appear').wait_until(have.size_greater_than_or_equal(2)):
        # do something

Or, by using non-waiting versions, if "you are in a rush:)":

    if browser.element('#i-might-say-yes-or-no').matching(have.text('yes'):
        # do something

    # ...

    if browser.all('.i-will-appear').matching(have.size_greater_than_or_equal(2)):
        # do something



## Tutorials


TBD

## More examples

TBD

## Changelog

[see CHANGELOG.md](https://github.com/yashaka/selene/blob/master/CHANGELOG.md)

## Contributing

Before implementing your ideas, it is recommended first to create a corresponding issue and discuss the plan to be approved;)
Also consider first to help with issues marked with help_needed label ;)

1. Clone project git clone https://github.com/yashaka/selene.git
2. Install pipenv via pip install pipenv
3. cd selene
4. pipenv install --dev

5. Add a "feature request" Issue to this project.
6. Discuss its need and possible implementation. And once approved...
7. Fork the project ( https://github.com/[my-github-username]/selene/fork )
8. Create your feature branch (`git checkout -b my-new-feature`)
9. Commit your changes (`git commit -am 'Add some feature'`)
10. Push to the branch (`git push origin my-new-feature`)
11. Create a new Pull Request

## Release process

1. python setup.py bdist_wheel
2. twine upload dist/*
