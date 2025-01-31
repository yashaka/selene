
# Selene for PageObjects

*Libraries like Selene have one important feature that fundamentally changes the approach to [refactoring](https://en.wikipedia.org/wiki/Code_refactoring) tests with the goal of “encapsulating technical details of interaction with elements on the page in the browser” ( <=> [“PageObject pattern”](https://martinfowler.com/bliki/PageObject.html))...*


## Simple test in Selene and Selenium WebDriver

Let's remember a simple test for searching in Google from the [“Selene: Quick Start”](./selene-quick-start-tutorial.md) tutorial:

```python
# imports ...
# ...


def test_finds_selene():

    browser.open('https://google.com/ncr')
    browser.element(by.name('q')).should(be.blank)

    browser.element(by.name('q')).type('python selene')
        .press_enter()
    browser.all('#rso>div').should(have.size_greater_than_or_equal(6))
    browser.all('#rso>div').first.should(have.text('selene'))

    browser.all('#rso>div').first.element('h3').click()
    browser.should(have.title_containing('selene'))
 
```

And here is the approximate analog of the above code – fully rewritten in raw Selenium WebDriver:

```python
# selenium-demo/tests/test_google.py
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as match

driver: WebDriver | None


def setup_function():
    global driver
    driver = webdriver.Chrome()


def teardown_function():
    driver.quit()


def test_finds_selene_webdriver_version():
    driver.get('https://google.com/ncr')
    WebDriverWait(driver, 4).until(match.presence_of_element_located(By.NAME, 'q'))
    assert driver.find_element(By.NAME, 'q').get_attribute('value') == ''

    driver.find_element(By.NAME, 'q').send_keys('github yashaka selene')
    driver.find_element(By.NAME, 'q').send_keys(Keys.ENTER)
    WebDriverWait(driver, 4).until(match.presence_of_element_located(By.CSS_SELECTOR, '#rso>div'))
    assert len(driver.find_elements(By.CSS_SELECTOR, '#rso>div')) >= 6
    assert 'yashaka/selene' in driver.find_elements(By.CSS_SELECTOR, '#rso>div')[0].text

    driver.find_elements(By.CSS_SELECTOR, '#rso>div')[0].find_element(By.CSS_SELECTOR, 'h3').click()
    WebDriverWait(driver, 4).until(match.title_contains('yashaka/selene'))
```

## API comparison: Selenium WebDriver vs Selene

The analog is really approximate, because Selenium WebDriver does not do everything that Selene does in the context of the logic of our test:

### driver vs browser

`driver.*` – is an approximate analog of `browser.*` from Selene.

### driver.get vs browser.open

`driver.get(absolute_url)` loads a page as `browser.open(absolute_or_relative_url)`...

But in `browser.open('/HERE/relative/partial-url')` you can pass a relative URL – relative to the base URL saved before in `browser.config.base_url = 'https://here.base-domain.url'` (respectively, in fact, will be loaded – `https://here.base-domain.url/HERE/relative/partial-url`).

### driver.find_element vs browser.element

driver.find_element finds the desired element using By locators. For example, to find the element "#rso>div", you will need the locator `By.CSS_SELECTOR`:  `driver.find_element(By.CSS_SELECTOR(#rso>div))`

browser.element can also use `By` locators: `browser.element(by.css(#rso>div))`. But there is also a much simpler way: just pass the CSS or XPath selector as a string: `browser.element('#rso>div')`.


### driver.find_elements vs browser.all 

The same applies to selectors for collections: driver.find_elements needs a `By` locator, while browser.all is able to find a collection of elements by a selector as a string.

### webelement.browser.config.base_url vs element.get(query.attribute(name))

webelement.get_attribute(name) is used to check a specific attribute of the element, in this test value to check that the input field is empty.

Selene can do the same, but in this test there is no need for this, because the logic of checking value is built into `browser.element(by.name('q)).should(be.blank)`.

### driver.wait and assert vs browser.should

`driver.wait(expected_conditions.*, 4000)`, officially named “explicit wait” – is approximately the same (i.e. “waiting check”), as `browser.should(have.*)` or `browser.should(be.*)`, which in Selene can be explained as “waiting checks”.

Accordingly, `expected_conditions.*` does the same as `have.*`or `be.*` – encapsulates the “check logic”, in other words – the checked condition (“condition”).

However, the available conditions among these `expected_conditions.*` are much less than in `have.*` and `be.*`. They are given little attention in Selenium WebDriver, because “conditions”, being **high-level** abstractions for **testing** purposes – do not quite correspond to the philosophy of Selenium WebDriver – “to be a **low-level** universal driver for **browser** automation” (i.e. not only for testing tasks).

Accordingly, for asserts, for example, over elements, you have to use `assert`, which is less reliable than `should`, because `assert` does not know how to wait by timeout until the assert passes. Therefore, in the test, as the easiest solution (a more complex, but also powerful solution will be considered later) – you have to make an additional `driver.wait` before such `assert`, which waits at least partially (for completeness, not all conditions are among `expected_conditions.*`) to the desired state of the element before the assert.

But the worst thing is that `expected_conditions.*` out of the box does not help in analyzing failing test errors – the most important part of the test development process, which affects the speed of their writing and maintenance. Pay attention to the difference in errors when failing:

```python
browser.should(have.title_containing('selenium'))   # FAIL with: ↙️
# Timed out after 4s, while waiting for:
# browser.has title containing 'selenium'
#                    
# Reason: AssertionError: actual title: GitHub – yashaka/selene: User-oriented Web UI browser tests in Python

# VS

WebDriverWait(driver, 4).until(match.title_contains('selenium')) # FAIL with: ↙️
# >  raise TimeoutException(message, screen, stacktrace)
#    selenium.common.exceptions.TimeoutException: Message:
```

Also, as we can see, in `should` we are not required to pass the timeout `4000` as in `wait` – in Selene its default value is 4 seconds and can be changed either globally through `browser.config.timeout = new_value` or as needed through `with` at the time of the call, as in the following examples:

```python
browser.with_(timeout=10).should(condition)

browser.element(selector_or_by).with_(timeout=10).should(condition)

browser.all(selector_or_by).with_(timeout=10).should(condition)
```

### Commands over elements

<p style="color:red;"><b>Waiting to be documented...</b></p>

### Implicit waits

<p style="color:red;"><b>Waiting to be documented...</b></p>

### Explicit waits instead of implicit waits

<p style="color:red;"><b>Waiting to be documented...</b></p>

### Key difference in the nature of locators and elements

But the main difference lies in how we get the elements for further work with them:

* in Selenium WebDriver a way of finding elements is represented by locators like `By.NAME('q')` or `By.CSS_SELECTOR('#rso>div')`, which we pass to methods like `driver.find_element(locator)` and `driver.find_elements(locator)`, which **immediately** perform search for corresponding actual elements on the page.

* In Selene a way of finding elements is represented by methods `browser.element(selector_or_by)` and `browser.all(selector_or_by)` – they themselves play the role of “locators” and **only describe the element** that will be found in the future by the corresponding method (by CSS-selector in a string like `'#rso>div'` or “selenium locator” like `by.name('q')`) – the actual search is not performed until we call either the `should` method or some action like `click`. Such “element-locators” are also called “lazy elements”, because their search is “postponed for later”, not performed at the moment of “describing the element” (if to be precise – at the moment of “creating an object representing the element”).

## Refactoring locators

Now, let's say we decided to refactor our tests in order to increase the readability of the code responsible for the ways of finding elements, encapsulate (hide) the corresponding details of the HTML structure, and remove the duplication of the corresponding code fragments that may potentially change in the future. The easiest way to do this is to extract locators into variables (or constants) and remove them from the test (to hide technical details from the test, increasing readability in the context of following the test logic).

Based on what we already know about the differences between Selene and Selenium WebDriver, in the case of the latter, only the `By.*` locators can be moved to variables:

```python
# imports ...

# ...

# we can't call and save: 
# query = driver.find_element(By.NAME, 'q')
# because we have not opened any page yet
query = (By.NAME, 'q')
results = (By.CSS_SELECTOR, '#rso>div')
result_header = (By.CSS_SELECTOR, 'h3')


def test_finds_selene_webdriver_version():
    driver.get('https://google.com/ncr')
    WebDriverWait(driver, 4).until(match.presence_of_element_located(query))
    assert driver.find_element(*query).get_attribute('value') == ''

    driver.find_element(*query).send_keys('github yashaka selene')
    driver.find_element(*query).send_keys(Keys.ENTER)
    WebDriverWait(driver, 4).until(match.presence_of_element_located(results))
    assert len(driver.find_elements(*results)) >= 6
    assert 'yashaka/selene' in driver.find_elements(*results)[0].text

    driver.find_elements(*results)[0].find_element(*result_header).click()
    WebDriverWait(driver, 4).until(match.title_contains('yashaka/selene'))
```

In the case of Selene we can immediately assign its “lazy” elements (playing the role of locators):

```python
# imports ...

query = browser.element(by.name('q'))
results = browser.all('#rso>div')
first_result_header = results.first.element('h3')

def test_finds_selene():
    browser.open('https://google.com/ncr')
    query.should(be.blank)

    query.type('python selene').press_enter()
    results.should(have.size_greater_than_or_equal(6))
    results.first.should(have.text('selene'))

    first_result_header.click()
    browser.should(have.title_containing('yashaka/selene'))
```

Well, how was it? It seems that in the case of Selenium WebDriver it is very difficult to see the difference before and after refactoring, and even more so to see how the result of refactoring differs between Selenium WebDriver and Selene... Heh, that's right, because in addition to locators there is a lot of other complexity that, unlike in Selene, continues to stick the guts out of Selenium :).

Let's, at least, simplify the result of refactoring to the code that concerns only locators... Here is an example of what can be achieved by encapsulating locators in variables for Selenium WebDriver:

```python
from selenium.webdriver.common.by import By

query = (By.NAME, 'q')

# ... create driver instance

driver.get('https://google.com/ncr')

driver.find_element(*query).send_keys('selenium')

driver.find_element(*query).send_keys(Keys.ENTER)

# ...

driver.find_element(*query).clear()
```

And here is the version for Selene, when we assign whole elements:

```python
query = browser.element(by.name('q'))

# ... maybe configure browser instance

browser.open('https://google.com/ncr')


query.send_keys('python selene')

query.press_enter()

# ...

query.clear()
```

– getting in the end when reusing much more concise and clean code in comparison with Selenium WebDriver! Now the difference is obvious :)

## The path to PageObject

The described above nature of Selene elements laziness does define the implementation of the PageObject pattern.

Actually, remembering that the main principle on which the PageObject is built is encapsulation...

> *Page objects are a classic example of encapsulation – they hide the details of the UI structure and widgetry from other components (the tests).*  
(c) Martin Fowler in [“PageObject”](https://martinfowler.com/bliki/PageObject.html) from 10 September 2013

– then we can say that we have already achieved the goal, hiding the implementation details of the locators inside the variables (more precisely constants) outside the test:

```python
# imports ...

# ...

query = (By.NAME, 'q')
results = (By.CSS_SELECTOR, '#rso>div')
result_header = (By.CSS_SELECTOR, 'h3')


def test_finds_selene_webdriver_version():
    driver.get('https://google.com/ncr')
    WebDriverWait(driver, 4).until(match.presence_of_element_located(query))
    assert driver.find_element(*query).get_attribute('value') == ''

    driver.find_element(*query).send_keys('github yashaka selene')
    driver.find_element(*query).send_keys(Keys.ENTER)
    WebDriverWait(driver, 4).until(match.presence_of_element_located(results))
    assert len(driver.find_elements(*results)) >= 6
    assert 'yashaka/selene' in driver.find_elements(*results)[0].text

    driver.find_elements(*results)[0].find_element(*result_header).click()
    WebDriverWait(driver, 4).until(match.title_contains('yashaka/selene'))
```

But let's expand the idea of encapsulation even further, coming to a more classic implementation of the well-known pattern.

So, we can go even further, encapsulating more low-level technical locators inside a separate module...

```python
# selene_demo/pages/google.py
# imports ...

query = browser.element(by.name('q'))
results = browser.all('#rso>div')
first_result_header = results.first.element('h3')
```

– to use which...

![](../assets/images/selene-for-page-objects-guide.md/without-autocomplete-py.png)

↗️ *(autocompletion does not work...)*

– you will have to add the import to the test manually 

```python
# selene-demo/tests/google_search_test.py
# imports ...
from selene_demo.pages import google

# ...

def test_finds_selene():
    browser.open('https://google.com/ncr')
    google.query.should(be.blank)

    google.query.type('python selene').press_enter()
    google.results.should(have.size_greater_than_or_equal(6))
    google.results.first.should(have.text('selene'))

    google.first_result_header.click()
    browser.should(have.title_containing('yashaka/selene'))
```
or with the help of the Quick Fix function by Command + . on Mac or Ctrl + . on Windows

![](../assets/images/selene-for-page-objects-guide.md/with-quick-fix-py.png)


– so that the autocompletion starts to work in the IDE for `google`:


![](../assets/images/selene-for-page-objects-guide.md/with-autocomplete-py.png)


Another friendly for IDE option is to encapsulate the locators


* as fields of an **class** object (without intermediate variables inside the module, and **with the ability to use access to neighboring fields right in the moment of initializing fields**):

```python
# selene_demo/pages/google.py
# imports ...

class Google:
    query = browser.element(by.name('q'))
    results = browser.all('#rso>div')
    first_result_header = results.first.element('h3')

google = Google()
```

The test code remains the same even after introducing classes:

```python
# selene-demo/__tests__/google_search_test.py
# ...
from selene_demo.pages.google import google


def test_finds_selene():
    browser.open('https://google.com/ncr')
    google.query.should(be.blank)

    google.query.type('python selene').press_enter()
    google.results.should(have.size_greater_than_or_equal(6))
    google.results.first.should(have.text('selene'))

    google.first_result_header.click()
    browser.should(have.title_containing('yashaka/selene'))
```

The last code:

```python
# selene-demo/__tests__/google_search_test.py
# ...
from selene_demo.pages.google import google


def test_finds_selene():
    browser.open('https://google.com/ncr')
    google.query.should(be.blank)

    google.query.type('python selene').press_enter()
    google.results.should(have.size_greater_than_or_equal(6))
    google.results.first.should(have.text('selene'))

    google.first_result_header.click()
    browser.should(have.title_containing('yashaka/selene'))
```

– you can make it even more “high-level”, encapsulating the interaction logic with the corresponding elements in the context of the relevant business steps of the user...

```python
# selene-demo/__tests__/google_search_test.py
# ...
from selene_demo.pages.google import google

# ...


def test_finds_selene():
    browser.open('https://google.com/ncr')
    google.query.should(be.blank)

    google.search('python selene')
    google.results.should(have.size_greater_than_or_equal(6))
    google.result(1).should(have.text('selene'))

    google.follow_link_of_result(number=1)
    browser.should(have.title_containing('yashaka/selene'))
```

in the class:


```python
# selene_demo/pages/google.py
# ...

class Google:
    query = browser.element(by.name('q'))
    results = browser.all('#rso>div')
    first_result_header = results.first.element('h3')

    def result(self, number):
        return self.results[number - 1]

    def search(self, text):
        self.query.type(text)
        self.query.press_enter()

    def follow_link_of_result(self, number):
        self.result(number).element('h3').click()


google = Google()
```

Perhaps someone will be tempted to implement a certain pattern to simulate “private fields of an object” that are not planned to be accessed from tests:


```python
# selene_demo/pages/google.py
# imports ...

class Google:
    query = browser.element(by.name('q'))
    results = browser.all('#rso>div')
    first_result_header = results.first.element('h3')
    __submit_button = browser.all(by.name('btnK')).first

    def result(self, number):
        return self.results[number - 1]

    def search(self, text):
        self.query.type(text)
        self.__submit_button.click()

    def follow_link_of_result(self, number):
        self.result(number).element('h3').click()


google = Google()
```

↗️ using a class

And here it is important that in most cases such premature encapsulation contradicts KISS. Why do we really need to hide something here? :) From whom? :) On some project, if some manual testers write these tests, and we want to allow them to use only step functions – then yes, it could be... But if not, why this premature optimization? (which is the root of all evil). Why not simplify your life and embed everything in one object returned from a function (or class).

For the possibility of refactoring elements and actions on them, or more precisely – for the ability to use all the power and variability of Python without restrictions from the automation tool of user steps in the browser – just corresponds to the peculiarity of Selene elements to be “lazy”, that is, “not to be found immediately at the moment of their definition”, which equates them to locators of the type `(By.NAME,'q')`.

Amen ;)  
