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

Selene encourages to use [composition over inheritace](http://en.wikipedia.org/wiki/Composition_over_inheritance) to reuse parts of web application like sidepanels, headers, footers, main contents, search forms, etc. This especially may be usefull in the case of single-page applications. Consequently we can naturally model our app under test even with a SinglePageObject composed with Widgets which can be loaded by demand like common PageObjects via their urls.

```python
from selene.page_object import PageObject

# We can define our Widget externally to main PageObject in case we want to reuse its elsewhere
class Article(SElement):
    def init(self):
        self.heading = self.s("heading")
        self.text = self.s("article")

class MainPage(PageObject):
    def open(self):
        visit("/main")
    
    def init(self):
        self.blog = MainPage.Blog("#blog").to_open(lambda: s("#menu .blog-lnk").click())
        
        self.shop = MainPage.Shop("#blog").to_open(lambda: s("#menu .shop-lnk").click())
        
        self.show_side_panel = s("#show-side-panel")
        self.side_panel = MainPage.SidePanel("#side-panel")
                          .to_open(lambda: self.show_side_panel.click())
                          
    # Assuming our "widgets" exist only on single main page their classes are defined internally
                          
    class Blog(SElement):
        def init(self):
            self.articles = self.ss("[id^='article']").of(Article)
            # other elements...
            
    
    class Shop(Selement):
        def init(self):
            # shop elements...
        
        def add_to_cart(self, product):
            # implementation...
    
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

**TBD**

### More examples

See **/tests** files for more examples of usage.

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

1. Fork it ( https://github.com/[my-github-username]/py-widgeon/fork )
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create a new Pull Request
