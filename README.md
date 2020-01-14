# Selene - Concise API for Selenium in Python 
(Selenide port in Python)

[![Build Status](https://travis-ci.org/yashaka/selene.svg?branch=master)](https://travis-ci.org/yashaka/selene) [![codecov](https://codecov.io/gh/yashaka/selene/branch/master/graph/badge.svg)](https://codecov.io/gh/yashaka/selene) [![Gitter](https://badges.gitter.im/gitterHQ/gitter.svg)](https://gitter.im/automician/selene)

community in russian: [![Join the chat at https://t.me/selene_py_ru](https://img.shields.io/badge/join%20chat-telegram-blue.svg)](https://t.me/selene_py_ru)


Main features:

- Concise API for Selenium
- jQuery-style selectors
- Ajax support
- PageObjects support
- Automatic driver management


Selene was inspired by [Selenide](http://selenide.org/) from Java world.

Tests with Selene can be built either in a simple straightforward "selenide' style or with PageObjects composed from Widgets i.e. reusable element components.

NOTE: This is still an alpha version. Lately selene was completely refactored, and have changed API a bit. So if you have been using it before (versions <= 0.0.8), then upgrading to next version may break your tests. Read changelog before upgrading to be prepared;)

## Installation

### latest development version 

    $ git clone https://github.com/yashaka/selene.git
    $ python setup.py install

or using pip:

    $ pip install git+https://github.com/yashaka/selene.git

[It is preferable also to use  local virtualenv](https://gist.github.com/yashaka/a547c6e0df5f6c973acc04655b6e3072).

### latest published pre-release version (currently this is recommended option unless selene 1.0 will be released):

    pip install selene --pre

### latest release version (versions <= 0.0.8 will become outdated soon)

    pip install selene

## Quick Start

### Basic Usage: 4 pillars of Selene

All Selene API consists just from 4 pillars:

1. Browser Actions (including finding elements)
2. Custom Selectors
3. Assertion Conditions
4. Custom Configuration

And one more not mandatory bonus:

`5.` concise jquery-style shortcuts for finding elements

All pillars are reflected in corresponding selene python modules and their methods.

#### 1. Browser Actions: [browser.*](https://github.com/yashaka/selene/blob/master/selene/browser.py)
e.g. `browser.open_url('https://todomvc4tasj.herokuapp.com')`

e.g. `browser.element('#new-todo')`

e.g. `browser.all('#todo-list>li')`

Once you have the elements, of course you can do some actions on them:

e.g. `browser.element('#new-todo').set_value('do something').press_enter()`

e.g. `browser.all('#todo-list>li').first().find('.toggle').click()`

#### 2. Custom Selectors: [by.*](https://github.com/yashaka/selene/blob/master/selene/support/by.py)
By default element finders (`browser.element`, `browser.all`) accept css selectors as strings, but you can use any custom selector from the `by` module.

e.g. `browser.element(by.link_text("Active")).click()`

#### 3. Assertion Conditions: [be.*](https://github.com/yashaka/selene/blob/master/selene/support/conditions/be.py) and [have.*](https://github.com/yashaka/selene/blob/master/selene/support/conditions/have.py)
Assertion conditions are used in "assertion actions" on elements.

e.g. `browser.element("#new-todo").should(be.blank)` or the same `browser.element("#new-todo").should(have.value(''))`

e.g. `browser.all('#todo-list>li').should(have.exact_texts('do something', 'do more'))`

e.g. `browser.all('#todo-list>li').should(be.empty)`

#### 4. Custom Configuration: [config.*](https://github.com/yashaka/selene/blob/master/selene/config.py)
e.g. `config.browser_name = 'chrome'`

You can omit custom configuration and Selene will use default values, e.g. browser_name is equal to `'firefox'` by default

Config options can be also overriden with corresponding system variables (see [#51](https://github.com/yashaka/selene/issues/51) for more details)

#### 5. Concise jquery-style shortcuts for finding elements:
e.g. `s('#new-todo')` instead of `browser.element('#new-todo')`

e.g. `ss('#todo-list>li')` instead of `browser.all('#todo-list>li')`

#### Imports

You can access to all main Selene API via single "wildcard" import:
```
from selene.api import *
```

If you don't like "wildcard" imports, you can use direct module imports or direct module functions import;) no problem:)

### OOP sidenotes...
If you did not like the "non-OOP" module functions from above, don't panic, you can use the same API via creating SeleneDriver objects...

You can find more explanations a bit further in this Readme.

### Basic example

```python
from selene.api import *


class TestTodoMVC(object):

    def test_selene_demo(self):
        tasks = ss("#todo-list>li")
        active_tasks = tasks.filtered_by(have.css_class("active"))

        browser.open_url('https://todomvc4tasj.herokuapp.com')

        s("#new-todo").should(be.blank)

        for task_text in ["1", "2", "3"]:
            s("#new-todo").set_value(task_text).press_enter()
        tasks.should(have.exact_texts("1", "2", "3")).should_each(have.css_class("active"))
        s("#todo-count").should(have.text('3'))

        tasks[2].s(".toggle").click()
        active_tasks.should(have.texts("1", "2"))
        active_tasks.should(have.size(2))

        tasks.filtered_by(have.css_class("completed")).should(have.texts("3"))

        s(by.link_text("Active")).click()
        tasks[:2].should(have.texts("1", "2"))
        tasks[2].should(be.hidden)

        s("#toggle-all").click()
        s("#clear-completed").click()
        tasks.should(be.empty)
```

This should be completely enough to start writing your tests.

### Next steps...

In case you need to reuse some parts elsewhere - go ahead and move your locators:
```python
    tasks = ss("#todo-list>li")
    active = have.css_class("active")
    completed = have.css_class("completed")
```
to some class and so implement a PageObject pattern.

You can also use alias methods for your taste:

```python
tasks[2].s(".toggle").click()
```
instead of
```python
tasks[2].element(".toggle").click()
```

---

```python
s("#todo-list").ss("li")
```
instead of
```python
s("#todo-list").all("li")
```

---

```python
tasks.assure(empty)
```
or
```python
tasks.should_be(empty)
```
instead of
```python
tasks.should(be.empty)
```

---

all the following names means the same: `assure`, `should`, `should_be`, `should_have`
Just the first `assure` sounds good with any condition:
* `assure(visible)` :)
* `assure(text('foo')` :)

but others may not:

* `should(visible)` :(
* `should(text('foo'))` :(

so you have to choose proper "condition" version each time:

* `should(be.visible` :)
* `should(have.text('foo'))` :)

or proper "should" alias:

* `should_be(visible)` :)
* `should_have(text('foo'))` :)

though these versions are less laconic than when using `assure`.
Compare:

* `assure(text('foo')` :)
* `should_have(text('foo'))` :|
* `should(have.text('foo'))` :|

But regardless being less concise, the latest version gives you better autocomplete abilities when you don't remember all conditions:

* `assure(.` :(
* `should(have. ...` :)

There seems to be no "the only best option". You can use the style you prefer more;)

### Automatic driver management

By default all "search elements" methods (`s`, `ss`) and other browser actions methods like `open_url` - use shared driver.
Shared driver is initialized automatically and uses Firefox driver by default.

#### Configuring shared browser and automatic driver executable installation

If you want other shared browser's driver, you can customize it explicitly:
```python
from selene import config
from selene.browsers import Browser

config.browser_name = Browser.CHROME
```

In order to make it work, you only need to have Chrome browser installed. 

But you don't need to install chromedriver executable, it will be installed automatically for you, if neeeded, thanks to integrated [webdriver_manager](https://github.com/SergeyPirogov/webdriver_manager)

#### Disabling automatic driver executable installation

In case you want to use your own executable, you can install it by you own and configure [webdriver_manager correspondingly](https://github.com/SergeyPirogov/webdriver_manager#configuration)

#### Disabling automatic driver management

You also can disable automatic driver initialization by providing your own driver instance:

```python
from selene import browser 
from selenium import webdriver

# this allows you to provide additional driver customization
def setup_module(m):
    driver = webdriver.Remote(
        command_executor='http://127.0.0.1:4444/wd/hub',
        desired_capabilities={'browserName': 'htmlunit',
                              'version': '2',
                              'javascriptEnabled': True})
    browser.set_driver(driver)


# then you have to close driver manually
def teardown_module(m):
    browser.quit()
```

### Explicit SeleneDriver

In addition to s, ss "static" methods (from selene.tools) to represent elements on the page, you can use their "object oriented" alternatives from SeleneDriver:

```python
from selene.driver import SeleneDriver
from selenium.webdriver import Firefox
from selene.support.conditions import have

driver = SeleneDriver.wrap(Firefox())
#...
def test_selene_demo():
    tasks = driver.ss("#todo-list>li")

    driver.get('http://todomvc4tasj.herokuapp.com')

    for task_text in ["1", "2", "3"]:
        driver.s("#new-todo").set_value(task_text).press_enter()

    tasks.should(have.texts("1", "2", "3"))
```

or even in more readable way:

```python
from selene.driver import SeleneDriver
from selenium.webdriver import Firefox
from selene.support.conditions import have

driver = SeleneDriver.wrap(Firefox())
#...
def test_selene_demo():
    tasks = driver.all("#todo-list>li")

    driver.get('http://todomvc4tasj.herokuapp.com')

    for task_text in ["1", "2", "3"]:
        driver.element("#new-todo").set_value(task_text).press_enter()

    tasks.should(have.texts("1", "2", "3"))
```

This approach may be useful in case you need to deal with different webdriver instances at the same time. (todo: examples will be provided later)

### Simple PageObjects Example
Here is a simple example of PageObjects implementation (inspired by [selenide google search example](https://github.com/selenide-examples/google/tree/master/test/org/selenide/examples/google/selenide_page_object)):

```python
from selene.browser import open_url
from selene.support.jquery_style_selectors import s, ss
from selene.support.conditions import have

class GooglePage(object):
    def open(self):
        open_url("http://google.com/ncr")
        return self

    def search(self, text):
        s("[name='q']").set(text).press_enter()
        return SearchResultsPage()

class SearchResultsPage(object):
    def __init__(self):
        self.results = ss(".srg .g")

def test_google_search():
    google = GooglePage().open()
    search = google.search("selene")
    search.results[0].should(have.text("In Greek mythology, Selene is the goddess of the moon"))  # :D
```

That's it. Selene encourages to start writing tests in the simplest way. And add more layers of abstraction only by real demand. 

### Reporting
So far reporting capabilities are reflected only in a detailed error messages.
For example the following code
```python
from selene.support.jquery_style_selectors import ss
from selene.support.conditions import be
#...
ss("#todo-list>li")[2].should(be.hidden)
```
in case of failure will result in exception raised with message:
```
       TimeoutException: Message:
                   failed while waiting 4 seconds
                   to assert Hidden
                   for element found by: ('css selector', '#new-todo')
```

---

And the the following "more complex" locating code
```python
from selene.support.jquery_style_selectors import ss
from selene.support.conditions import be
#...
ss("#todo-list>li")[2].should(be.hidden)
```
in case of failure will result in exception raised with message:
```
       TimeoutException: Message:
                   failed while waiting 4 seconds
                   to assert Hidden
                   for element found by: ('By.Selene', ('css selector', '#todo-list>li')[2]")
```

Here the "stringified locator" is a bit more complicated for eyes. You can decode from it the following information:
_"inside the list of elements available by css selector '#todo-list>li' selene was trying to find element with index [2]"_

**NOTE** 
If you use pytest, it is recommended to [disable too detailed traceback printing](http://doc.pytest.org/en/latest/usage.html#modifying-python-traceback-printing), e.g. by using one of the following command-line options:
```
pytest --tb=short   # shorter traceback format
pytest --tb=native  # Python standard library formatting
```

### PageObjects composed with Widgets
Sometimes your UI is build with many "reusable" widgets or components. If you follow general "Test Automation Pyramid" guidelines, most probably you have not too much of automated selenium tests. And "simple pageobjects" will be pretty enough for your tests.
But in case you need to write a tone of UI tests, and you need correspondent DRY solution for your reusable components then this section may be for you. 

Selene encourages to use [composition over inheritance](http://en.wikipedia.org/wiki/Composition_over_inheritance) to reuse parts of web application like sidepanels, headers, footers, main contents, search forms, etc. This especially may be usefull in the case of over-complicated single-page applications. Consequently we can naturally model our app under test even with a SinglePageObject composed with Widgets, that can be loaded on demand.

Below you can find an example of Widgets (aka ElementObjects, aka "[PageObjects by Fowler](http://martinfowler.com/bliki/PageObject.html)".
The application under test - [TodoMvc](todomvc4tasj.herokuapp.com) is very simple. It is completely does not make sense to use Widgets here:). But we use it just as an example of implementation.
```python
from selene.conditions import exact_text, hidden, exact_texts
from selene.browser import set_driver, driver
from selene.support.jquery_style_selectors import ss, s
from selenium import webdriver
from selene.support.conditions import have, be

from helpers.todomvc import given_active


def setup_module(m):
    set_driver(webdriver.Firefox())


def teardown_module(m):
    driver().quit()

class Task(object):

    def __init__(self, container):
        self.container = container

    def toggle(self):
        self.container.element(".toggle").click()
        return self


class Tasks(object):

    def _elements(self):
        return ss("#todo-list>li")

    def _task_element(self, text):
        return self._elements().element_by(have.exact_text(text))

    def task(self, text):
        return Task(self._task_element(text))

    def should_be(self, *texts):
        self._elements().should(have.exact_texts(*texts))


class Footer(object):
    def __init__(self):
        self.container = s("#footer")
        self.clear_completed = self.container.element("#clear-completed")

    def should_have_items_left(self, number_of_active_tasks):
        self.container.element("#todo-count>strong").should(have.exact_text(str(number_of_active_tasks)))


class TodoMVC(object):
    def __init__(self):
        self.container = s("#todoapp")
        self.tasks = Tasks()
        self.footer = Footer()

    def clear_completed(self):
        self.footer.clear_completed.click()
        self.footer.clear_completed.should(be.hidden)
        return self


def test_complete_task():
    given_active("a", "b")

    app = TodoMVC()

    app.tasks.task("b").toggle()
    app.clear_completed()
    app.tasks.should_be("a")
    app.footer.should_have_items_left(1)

```

### More examples

See [/tests/](https://github.com/yashaka/selene/tree/master/tests) files for more examples of usage.
E.g. one more [PageObject with Widgets example](https://github.com/yashaka/selene/blob/master/tests/examples/order/app_model/order_widgets.py) and its [acceptance test](https://github.com/yashaka/selene/blob/master/tests/examples/order/order_test.py).

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
