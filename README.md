# Selene - Concise API for Selenium in Python 
(Selenide/Capybara + htmlelements/Widgeon alternative)

Main features:
- Concise API for Selenium
- jQuery-style selectors
- Ajax support
- PageObjects support



Selene was inspired by [Selenide](http://selenide.org/) from Java world.

Tests with Selene can be built either in a simple straightforward "selenide' style or with PageObjects composed from Widgets i.e. reusable element components.

NOTE: This is still a pre-alpha version and may have some issues

## Installation

    pip install selene

## Usage

### Basic example

```python
from selenium import webdriver

from selene.conditions import *
from selene.tools import *


def setup_module(m):
    set_driver(webdriver.Firefox())


def teardown_module(m):
    get_driver().quit()


def test_selene_demo():
    tasks = ss("#todo-list>li")
    active_tasks = tasks.filter_by(css_class("active"))

    visit('http://todomvc4tasj.herokuapp.com')

    for task_text in ["1", "2", "3"]:
        s("#new-todo").set_value(task_text).press_enter()

    tasks.assure(texts("1", "2", "3")).assure_each(css_class("active"))
    s("#todo-count").assure(text("3"))

    tasks[2].s(".toggle").click()


    active_tasks.assure(texts("1", "2"))
    active_tasks.assure(size(2))

    tasks.filter_by(css_class("completed")).assure(texts("3"))

    s("a[href='#/active']").click()
    tasks[:2].assure(texts("1", "2"))
    tasks[2].assure(hidden)

    s("#toggle-all").click()
    s("#clear-completed").click()
    tasks.assure(empty)
```

This should be completely enough to start writing your tests.
In case you need to reuse some parts elsewhere - go ahead and move your locators:
```python
    tasks = ss("#todo-list>li")
    active = css_class("active")
    completed = css_class("completed")
```
to some class and so implement a PageObject pattern.

You can also use alias methods for your taste:

```python
tasks[2].find(".toggle").click()
```
instead of
```python
tasks[2].s(".toggle").click()
```

---

```python
s("#todo-list").find_all("li")
```
instead of
```python
s("#todo-list").ss("li")
```

---

```python
tasks.insist(empty)
```
or
```python
tasks.should_be(empty)
```
instead of
```python
tasks.assure(empty)
```

---

all the following names means the same: `insist`, `assure`, `should_be`, `should`, `should_be`, `should_have`
Just the first two can sound good with any condition, but others depend.


### Simple PageObjects Example
Here is a simple example of PageObjects implementation (inspired by [selenide google search example](https://github.com/selenide-examples/google/tree/master/test/org/selenide/examples/google/selenide_page_object)):

```python
from selene.tools import s, ss, visit
from selene.conditions import text

class GooglePage(object):
    def open(self):
        visit("http://google.com/ncr")
        return self

    def search(self, text):
        s("[name='q']").set(text).press_enter()
        return SearchResultsPage()

class SearchResultsPage(object):
    def __init__(self):
        self.results = ss("#ires li.g")

def test_google_search():
    google = GooglePage().open()
    search = google.search("selene")
    search.results[0].insist(text("In Greek mythology, Selene is the goddess of the moon"))  # :D
```

That's it. Selene encourages to start writing tests in the simplest way. And add more layers of abstraction only by real demand. 

### Reporting
So far reporting capabilities are reflected only in a detailed error messages.
For example the following code
```python
ss("#todo-list>li")[2].should_be(hidden)
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
ss("#todo-list>li")[2].should_be(hidden)
```
in case of failure will result in exception raised with message:
```
       TimeoutException: Message:
                   failed while waiting 4 seconds
                   to assert Hidden
                   for element found by: ('selene', "('css selector', '#todo-list>li')[2]")
```

Here the "stringified locator" is a bit more complicated for eyes. You can decode from it the following information:
_"inside the list of elements available by css selector '#todo-list>li' selene was trying to find element with index [2]"_

### PageObjects composed with Widgets
Sometimes your UI is build with many "reusable" widgets or components. If you follow general "Test Automation Pyramid" guidelines, most probably you have not too much of automated selenium tests. And "simple pageobjects" will be pretty enough for your tests.
But in case you need to write a tone of UI tests, and you need correspondent DRY solution for your reusable components then this section may be for you. 

Selene encourages to use [composition over inheritance](http://en.wikipedia.org/wiki/Composition_over_inheritance) to reuse parts of web application like sidepanels, headers, footers, main contents, search forms, etc. This especially may be usefull in the case of over-complicated single-page applications. Consequently we can naturally model our app under test even with a SinglePageObject composed with Widgets, that can be loaded on demand.

Below you can find an example of Widgets (aka ElementObjects, aka "[PageObjects by Fowler](http://martinfowler.com/bliki/PageObject.html)".
The application under test - [TodoMvc](todomvc4tasj.herokuapp.com) is very simple. It is completely does not make sense to use Widgets here:). But we use it just as an example of implementation.
```python
from selene.conditions import exact_text, hidden, exact_texts
from selene.tools import set_driver, get_driver, ss, s
from selenium import webdriver

from helpers.todomvc import given_active


def setup_module(m):
    set_driver(webdriver.Firefox())


def teardown_module(m):
    get_driver().quit()

class Task(object):

    def __init__(self, container):
        self.container = container

    def toggle(self):
        self.container.find(".toggle").click()
        return self


class Tasks(object):

    def _elements(self):
        return ss("#todo-list>li")

    def _task_element(self, text):
        return self._elements().findBy(exact_text(text))

    def task(self, text):
        return Task(self._task_element(text))

    def should_be(self, *texts):
        self._elements().should_have(exact_texts(*texts))


class Footer(object):
    def __init__(self):
        self.container = s("#footer")
        self.clear_completed = self.container.find("#clear-completed")

    def should_have_items_left(self, number_of_active_tasks):
        self.container.find("#todo-count>strong").should_have(exact_text(str(number_of_active_tasks)))


class TodoMVC(object):
    def __init__(self):
        self.container = s("#todoapp");
        self.tasks = Tasks()
        self.footer = Footer()

    def clear_completed(self):
        self.footer.clear_completed.click()
        self.footer.clear_completed.should_be(hidden)
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
E.g. one more [PageObject with Widgets example](https://github.com/yashaka/selene/blob/master/tests/order/pages/order.py) and its [acceptance test](https://github.com/yashaka/selene/blob/master/tests/order/custom_selements_and_collections_end_to_end_test.py).

## TODO list

* consider automatic webdriver management implementation
* add screenshooting
* add more convenient methods to SElementsCollection impl.
* improve general "autocompletion in IDE" capabilities (reduce "magic" in implementation)
* make browser management support parallel testing
* simplify implementation, at least decouple as much as possible some parts...
* see more ideas at [see todo.md](https://github.com/yashaka/selene/blob/master/todo.md)

## Changelog

[see CHANGELOG.md](https://github.com/yashaka/selene/blob/master/CHANGELOG.md)

## Contributing

1. Add a "feature request" Issue to this project.
2. Discuss its need and possible implementation. And once approved...
2. Fork the project ( https://github.com/[my-github-username]/selene/fork )
3. Create your feature branch (`git checkout -b my-new-feature`)
4. Commit your changes (`git commit -am 'Add some feature'`)
5. Push to the branch (`git push origin my-new-feature`)
6. Create a new Pull Request
