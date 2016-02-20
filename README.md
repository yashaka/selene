# Selene - Concise API for Selenium in Python 
(Selenide/Capybara + htmlelements/Widgeon alternative)

Main features:
- Concise API for Selenium
- jQuery-style selectors
- Ajax support
- SinglePage App friendly PageObjects
  - composed with reusable and loadable Widgets


Selene was inspired by [Selenide](http://selenide.org/) and [htmlelements](https://github.com/yandex-qatools/htmlelements) in Java and [Widgeon](https://github.com/yashaka/widgeon) gem in Ruby.

Tests with Selene can be built either in a simple straightforward "selenide' style or with PageObjects composed from Widgets i.e. reusable element components (aka selements).

NOTE: This is still a pre-alpha version and may have some issues

NOTE: **Latest version - 0.0.5 - changed API a lot :)**

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


def test_selene_demo(self):
    tasks = ss("#todo-list>li")
    active_tasks = tasks.filter(css_class("active"))

    visit('http://todomvc4tasj.herokuapp.com')

    for task_text in ["1", "2", "3"]:
        s("#new-todo").set_value(task_text).press_enter()

    tasks.assure(texts("1", "2", "3")).assure_each(css_class("active"))
    s("#todo-count").assure(text("3"))

    tasks[2].s(".toggle").click()


    active_tasks.assure(texts("1", "2"))
    active_tasks.assure(size(2))

    tasks.filter(css_class("completed")).assure(texts("3"))

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

We can pretify the code a bit:
```python
from selene.page_object import PageObject
from selene.tools import s, ss, visit
from selene.conditions import text

class GooglePage(PageObject):
    def open(self):
        visit("http://google.com/ncr")

    def search(self, text):
        s("[name='q']").set(text).press_enter()
        return SearchResultsPage()

class SearchResultsPage(PageObject):
    def init(self):
        self.results = ss("#ires li.g")

def test_google_search():
    google = GooglePage().get()
    search = google.search("selene")
    search.results[0].insist(text("In Greek mythology, Selene is the goddess of the moon"))
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

### PageObjects composed with Widgets (aka SElements)
Sometimes your UI is build with many "reusable" widgets or components. If you follow general "Test Automation Pyramid" guidelines, most probably you have not too much of automated selenium tests. And "simple pageobjects" will be pretty enough for your tests.
But in case you need to write a tone of UI tests, and you need correspondent DRY solution for your reusable components then this section may be for you. 

Selene encourages to use [composition over inheritance](http://en.wikipedia.org/wiki/Composition_over_inheritance) to reuse parts of web application like sidepanels, headers, footers, main contents, search forms, etc. This especially may be usefull in the case of over-complicated single-page applications. Consequently we can naturally model our app under test even with a SinglePageObject composed with Widgets, that can be loaded on demand.

```python
from selene.elements import SElement
from selene.page_object import PageObject
from selene.tools import visit, ss, s
from selene.widgets import SelectList

# We can define our Widget externally to main PageObject
# in case we want to reuse it elsewhere
class Article(SElement):
    def init(self):
        self.heading = self.s("heading")
        self.text = self.s("article")

class MainPage(PageObject):
    def open(self):
        visit("/main")
    
    def init(self):
        self.lang = SelectList("#lang-selector")
        
        self.shop = MainPage.Shop("#shop")\
                    .to_open(lambda: s("#menu .shop-lnk").click())
        
        self.blog = MainPage.Blog("#blog")\
                    .to_open(lambda: s("#menu .blog-lnk").click())
        
        self.show_side_panel = s("#show-side-panel")
        self.side_panel = MainPage.SidePanel("#side-panel")\
                          .to_open(lambda: self.show_side_panel.click())
                          
    # Assuming our "widgets" exist only on single main page
    # their classes are defined internally   
    
    class Shop(Selement):
        def init(self):
            # shop elements...
        
        def add_to_cart(self, product):
            # implementation...
                          
    class Blog(SElement):
        def init(self):
            self.articles = self.ss("[id^='article']").of(Article)
            # other elements...
    
    class SidePanel(SElement):
        def init(self):
            self.sign_in_form = self.s(MainPage.SidePanel.SignInForm("#sign-in-form"))
            self.other_element = self.s("#other-element")
        
        class SignInForm(SElement):
            def init(self):
                self.mail = self.s("#mail")
                self.pass = self.s("#pass")
                self.signin = self.s("#sign_in")
            
            def do_signin(self, **mail_and_pass):
                self.fill_with(**mail_and_pass)
                self.signin.click()
```

So then, somewhere in the tests:

```python
main = MainPage.get();
main.side_panel.open().do_signin(mail="user@example.com", pass="ytrewq654321")
main.blog.open().articles.assure(size(10))

shop = main.shop.open()
shop.add_to_cart("Product FooBar")
# ...
```

#### Example Explained

Make your class a 'selene' Widget
```python
class Article(SElement):
```

---

Init its sub-elements
```python
    def init(self):
        self.heading = self.s("heading")
        self.text = self.s("article")
```
The following selement definition
```python
        self.heading = self.s("heading")
```
is a shortcut to:
```python
        self.heading = s("heading", self)
```
telling: search this element by locator `"heading"` inside the `self` context, i.e. selenium will search for `"heading"` not among all page but only inside the article, found by its own `"#article-1"` locator which may be definied like `Article("#article-1")`

---

Make your class a 'selene' PageObject
```python
class MainPage(PageObject):
```


Specify how to load your page via implementing #open method
```python
    def open(self):
        visit("/main")
```


Specify its sub-elements
```python
    def init(self):
        # declaring lang as 'SelectList' widget
        self.lang = SelectList("#lang-selector")  
        
        #...
        
        # declaring show_side_panel as "simple" SElement
        self.show_side_panel = s("#show-side-panel")  
        #...
```

---

Configure sub-widgets as "pseudo" LoadableComponents via `to_open` method
```python
        self.blog = MainPage.Blog("#blog")
                    .to_open(lambda: s("#menu .blog-lnk").click())
        
        self.shop = MainPage.Shop("#shop")
                    .to_open(lambda: s("#menu .shop-lnk").click())
        
        # side panel may be used separately, 
        # so it's defined as separate sub-element of the MainPage
        self.show_side_panel = s("#show-side-panel")  
        self.side_panel = MainPage.SidePanel("#side-panel")
                          .to_open(lambda: self.show_side_panel.click())
```
So when you try to use e.g. blog:
```python
MainPage.get().blog.open().articles[1].heading.insist(text("Hello Bob!"))
```
You have the ability to open it "along the way".
It was called "pseudo" LoadableComponent, because the real loadable component would be automatically loaded via `s("#menu .blog-lnk").click()` in case yet not visible.

Such "explicit over implicit" loading were implemented in selene in order to match python ZEN. Nevertheless test should explicitly state its test logic, not hide it internally. Though somewhere in the future it is possible to see such "implicit loading feature" available via additional configuration.

Remember that this feature is far from being silver bullet. Actually you can have pretty handy code without using it:
```python
main = MainPage.get();
main.open_side_panel()
main.side_panel.do_signin(mail="user@example.com", pass="ytrewq654321")
main.open_blog()
main.blog.articles.assure(size(10))

main.open_shop()
shop = main.shop
shop.add_to_cart("Product FooBar")
# ...
```
or even:
```python
# ...
shop = main.open_shop()
shop.add_to_cart("Product FooBar")
# ...
```
;)

---

Declare a collection of widgets
```python
            self.articles = self.ss("[id^='article']").of(Article)
```

---

Use SElement#fill_with to do a bulk set of fields
```python
        class SignInForm(SElement):
            def init(self):
                self.mail = self.s("#mail")
                self.pass = self.s("#pass")
                self.signin = self.s("#sign_in")
            
            def do_signin(self, **mail_and_pass):
                self.fill_will(**mail_and_pass)
                signin.click()
```
So somewhere in the tests:
```python
signform.do_signin(mail="user@example.com", pass="ytrewq654321")
```

---

Use factory method `PageObject#get` in order to instantiate PageObject and load it via `open`
```python
main = MainPage.get();
```

### More examples

See [/tests/](https://github.com/yashaka/selene/tree/master/tests) files for more examples of usage.
E.g. one more [PageObject with Widgets example](https://github.com/yashaka/selene/blob/master/tests/order/pages/order.py) and its [acceptance test](https://github.com/yashaka/selene/blob/master/tests/order/custom_selements_and_collections_end_to_end_test.py).

## TODO list

* consider automatic webdriver management implementation
* add screenshooting
* add more convenient methods to SElement and SElementsCollection impl.
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
