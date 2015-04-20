# Selene - Concise API for Selenium in Python 
(Selenide/Capybara + Widgeon alternative)

Main features:
- Concise API for Selenium
- jQuery-style selectors
- Ajax support
- Automatic webdriver management
- SinglePage app friendly PageObjects
-- composed with reusable and loadable Widgets


Selene was inspired by [Selenide](http://selenide.org/) in Java and [Widgeon](https://github.com/yashaka/widgeon) gem in Ruby.
Tests with Selene can be built either in a simple straightforward "selenide' style or with PageObjects composed from Widgets i.e. reusable element components (aka selements), that support [LoadableComponent](https://code.google.com/p/selenium/wiki/LoadableComponent)
pattern.

NOTE: This is still a pre-alpha version and have some stability issues

## Installation

    pip install selene

## Usage

### Basic example

```python
from selene.tools import *
from selene.conditions import text, texts, absent


def setup_module():
    config.app_host = ''


def test_create_task():

    tasks = ss("#todo-list>li")
    active = css_class("active")
    completed = css_class("completed")

    visit("http://todomvc.com/examples/troopjs_require/#/")

    for task_text in ["1", "2", "3"]:
        s("#new-todo").set(task_text).press_enter()
    tasks.insist(texts("1", "2", "3")).insist_each(active)
    s("#todo-count").insist(text(3))

    tasks[2].s(".toggle").click()
    tasks.filter(active).insist(texts("1", "2"))
    tasks.filter(completed).insist(texts("3"))

    s("#filters a[href='#/active']").click()
    tasks[:2].insist(texts("1", "2"))
    tasks[2].insist(hidden)
```

This should be completely enough to start writing your tests.
In case you need to reuse some parts elsewhere - go ahead and move your locators:
```python
    tasks = ss("#todo-list>li")
    active = css_class("active")
    completed = css_class("completed")
```
to some class and so implement a PageObject pattern.

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
ss("#todo-list>li")[2].insist(hidden) 
```
in case of failure will result in exception raised with message:
```
Timeout reached while waiting...
During: 4s
For: {#todo-list>li[2]}
Until: hidden
Screenshot: /Users/ayia/projects/yashaka/selene/tests/reports/screenshots/1429532551.16.png
```

### PageObjects composed with Widgets (aka SElements)
Sometimes your UI is build with many "reusable" widgets or components. If you follow general "Test Automation Pyramid" guidelines, most probably you have not too much of automated selenium tests. And "simple pageobjects" will be pretty enough for your tests.
But in case you need to write a tone of UI tests, and you need correspondent DRY solution for your reusable components then this section may be for you. 

Selene encourages to use [composition over inheritance](http://en.wikipedia.org/wiki/Composition_over_inheritance) to reuse parts of web application like sidepanels, headers, footers, main contents, search forms, etc. This especially may be usefull in the case of single-page applications. Consequently we can naturally model our app under test even with a SinglePageObject composed with Widgets which can be loaded by demand like common PageObjects via their urls.

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
        
        self.shop = MainPage.Shop("#blog")
                    .to_open(lambda: s("#menu .shop-lnk").click())
        
        self.blog = MainPage.Blog("#blog")
                    .to_open(lambda: s("#menu .blog-lnk").click())
        
        self.show_side_panel = s("#show-side-panel")
        self.side_panel = MainPage.SidePanel("#side-panel")
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
                self.fill_will(**mail_and_pass)
                signin.click()
```

So then, somewhere in the tests:

```python
main = MainPage.get();
main.side_panel.do_signin(mail="user@example.com", pass="ytrewq654321")
main.blog.articles.insist(size(10))

shop = main.shop
shop.add_to_cart("Product FooBar")
# ...
```

#### Example Explained

Make your class a 'selene' Widget
```python
class Article(SElement):
```


Inits its sub-elements
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


Configure sub-widgets as LoadableComponents via `to_open` method
```python
        self.blog = MainPage.Blog("#blog")
                    .to_open(lambda: s("#menu .blog-lnk").click())
        
        self.shop = MainPage.Shop("#blog")
                    .to_open(lambda: s("#menu .shop-lnk").click())
        
        # side panel may be used separately, 
        # so it's defined as separate sub-element of the MainPage
        self.show_side_panel = s("#show-side-panel")  
        self.side_panel = MainPage.SidePanel("#side-panel")
                          .to_open(lambda: self.show_side_panel.click())
```
So when you try to use e.g. blog:
```python
MainPage.get().blog.articles[1].heading.insist(text("Hello Bob!"))
```
It will be automatically loaded via `s("#menu .blog-lnk").click()` in case yet not visible.


Declare a collection of widgets
```python
            self.articles = self.ss("[id^='article']").of(Article)
```


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


Use factory method `PageObject#get` in order to instantiate PageObject and load it via `open`
```python
main = MainPage.get();
```


Or the same way with widgets:
```python
main.blog.insist(hidden)
main.blog.get().insist(visible)
```
Since, `insist` will not load widget if it's yet not loaded
Instead, you can use `assure` which is "smart" `insist`, i.e. loading widget.
```python
main = MainPage.get();

# main.blog.assure(hidden)  # >> this line will FAIL 
# because assure will try to load blog until it's visible before asserting the "hidden" condition on it

main.blog.assure(visible)
```
It's up to the user what to use:
- more pythonic `get` + `insist` (read: "explicit is better then implicit") 
- or more laconic but "magical" `assure`

### More examples

See [/tests/](https://github.com/yashaka/selene/tree/master/tests) files for more examples of usage.
E.g. one more [PageObject example](https://github.com/yashaka/selene/blob/master/tests/resources/pages/order.py) and its [acceptance test](https://github.com/yashaka/selene/blob/master/tests/pageobject_acceptance_test.py).

## TODO list

* Improve and stabilize automatic webdriver management
* Improve and stabilize screenshooting
* add support of multiple browsers (only Firefox is supported so far)
* add support of xpath locators (only css selectores so far)
* add more convenient methods to SElement and SElementsCollection impl.
* consider implementing conditions as hamcrest matchers (in addition to simple functions or lambdas)
* improve general "autocompletion in IDE" capabilities (reduce "magic" in implementation)
* make browser management support parallel testing
* simplify implementation, at least decouple as much as possible some parts...
* see more ideas at todo.md

## Contributing

1. Fork it ( https://github.com/[my-github-username]/selene/fork )
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create a new Pull Request
