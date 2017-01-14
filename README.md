# Selene - Concise API for Selenium in Python 
(Selenide port in Python)

Main features:
- Concise API for Selenium
- jQuery-style selectors
- Ajax support
- PageObjects support
- Automatic driver management


Selene was inspired by [Selenide](http://selenide.org/) from Java world.

Tests with Selene can be built either in a simple straightforward "selenide' style or with PageObjects composed from Widgets i.e. reusable element components.

NOTE: This is still a pre-alpha version and API is nut fully finalized. Lately selene was completely refactored, and have changed API a bit. So if you have been using it before (versions <= 0.0.8), then upgrading to next version may break your tests. Read changelog before upgrading to be prepared;)

## Installation

### latest development version (currently this is recommended option unless selene 1.0 will be released):

    $ git clone https://github.com/yashaka/selene.git
    $ python setup.py install

[It is preferable also to use  local virtualenv](https://gist.github.com/yashaka/a547c6e0df5f6c973acc04655b6e3072).

### latest released version (versions <= 0.0.8 will become outdated soon)

    pip install selene

## Usage

### Basic example

```python
from selene.tools import s, ss, visit
from selene.support.conditions import be, have

def test_selene_demo():
    tasks = ss("#todo-list>li")
    active_tasks = tasks.filtered_by(have.css_class("active"))

    visit('http://todomvc4tasj.herokuapp.com')

    for task_text in ["1", "2", "3"]:
        s("#new-todo").set_value(task_text).press_enter()

    tasks.should(have.texts("1", "2", "3")).should_each(have.css_class("active"))
    s("#todo-count").should(have.text("3"))

    tasks[2].element(".toggle").click()


    active_tasks.should(have.texts("1", "2"))
    active_tasks.should(have.size(2))

    tasks.filtered_by(have.css_class("completed")).should(have.texts("3"))

    s("a[href='#/active']").click()
    tasks[:2].should(have.texts("1", "2"))
    tasks[2].should(be.hidden)

    s("#toggle-all").click()
    s("#clear-completed").click()
    tasks.should(be.empty)
```

This should be completely enough to start writing your tests.
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

### Configuring shared browser

By default all "search elements" methods (`s`, `ss`) and other browser actions methods like `visit` - use shared driver.
Shared driver is initialized automatically and uses Firefox driver. 

If you wont other shared browser's driver, you can customize it explicitly:
```python
from selene import config
from selene.browsers import Browser

config.browser_name = Browser.CHROME
```

You also can disable automatic driver initialization by providing your driver instance:

```python
from selene.tools import set_driver, get_driver
from selenium import webdriver

# this allows you to provide additional driver customization
def setup_module(m):
    driver = webdriver.Remote(
        command_executor='http://127.0.0.1:4444/wd/hub',
        desired_capabilities={'browserName': 'htmlunit',
                              'version': '2',
                              'javascriptEnabled': True})
    set_driver(driver)


# then you have to close driver manually
def teardown_module(m):
    get_driver().quit()
```

### Explicit SeleneDriver

In addition to s, ss "static" methods (from selene.tools) to represent elements on the page, you can use their "object oriented" alternatives from SeleneDriver:

```python
driver = SeleneDriver.wrap(FirefoxDriver())
#...
def test_selene_demo():
    tasks = driver.ss("#todo-list>li")

    visit('http://todomvc4tasj.herokuapp.com')

    for task_text in ["1", "2", "3"]:
        driver.s("#new-todo").set_value(task_text).press_enter()

    tasks.should(have.texts("1", "2", "3"))
```

or even in more readable way:

```python
driver = SeleneDriver.wrap(FirefoxDriver())
#...
def test_selene_demo():
    tasks = driver.all("#todo-list>li")

    visit('http://todomvc4tasj.herokuapp.com')

    for task_text in ["1", "2", "3"]:
        driver.element("#new-todo").set_value(task_text).press_enter()

    tasks.should(have.texts("1", "2", "3"))
```

This approach may be useful in case you need to deal with different webdriver instances at the same time. (todo: examples will be provided later)

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
    search.results[0].assure(text("In Greek mythology, Selene is the goddess of the moon"))  # :D
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
E.g. one more [PageObject with Widgets example](https://github.com/yashaka/selene/blob/master/tests/examples/order/app_model/order_widgets.py) and its [acceptance test](https://github.com/yashaka/selene/blob/master/tests/examples/order/order_test.py).

## TODO list

* consider automatic webdriver management implementation
* make browser management support parallel testing
* see more ideas at [see todo.md](https://github.com/yashaka/selene/blob/master/todo.md)

## Changelog

[see CHANGELOG.md](https://github.com/yashaka/selene/blob/master/CHANGELOG.md)

## Contributing

Before implementing your ideas, it is recommended first to create a corresponding issue and discuss the plan to be approved;)
Also consider first to help with issues marked with help_needed label ;)

1. Add a "feature request" Issue to this project.
2. Discuss its need and possible implementation. And once approved...
2. Fork the project ( https://github.com/[my-github-username]/selene/fork )
3. Create your feature branch (`git checkout -b my-new-feature`)
4. Commit your changes (`git commit -am 'Add some feature'`)
5. Push to the branch (`git push origin my-new-feature`)
6. Create a new Pull Request