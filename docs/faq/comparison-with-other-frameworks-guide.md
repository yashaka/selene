# How Selene compares to other frameworks

There are several Selenium Python frameworks (also known as *"wrappers"*).
We will focus on five of them:
[Splinter][splinter-docs],
[Helium][helium-docs],
[SeleniumBase][seleniumbase-docs],
[Pylenium][pylenium-docs] and
[Selene][selene-docs].

[splinter-docs]: https://splinter.readthedocs.io/
[helium-docs]: https://selenium-python-helium.readthedocs.io/
[seleniumbase-docs]: https://seleniumbase.io/
[pylenium-docs]: https://docs.pylenium.io/
[selene-docs]: https://yashaka.github.io/selene/

Their main goal is to simplify interaction with native Selenium Webdriver API.
All of them let you write more readable and reliable web UI (end-to-end)
browser tests in Python.
But they use different approaches and have their own architecture under the hood.

We will provide you with a **subjective** description of the advantages and disadvantages of using each of them.
However, we want to lead off by demonstrating code style
(for each framework and Selenium itself)
and making a test that does simple logic:

1. Starts a Chrome session
and navigates to [https://google.com/ncr](https://google.com/ncr)
2. Asserts that query input is blank.
3. Searches for "selenium" (i.e. types "selenium" and presses Enter key).
4. Asserts the number of search results.
5. Asserts that the first result contains text "Selenium automates browsers".

<!-- markdownlint-disable MD046 -->
=== "Selene"

    ```python
    def test_compare_api_style_example_selene():
        from selene import browser, have, be, by

        browser.open('https://google.com/ncr')

        search_input = browser.element(by.name('q'))
        search_input.should(be.blank).type('selenium').press_enter()

        browser.all('#search .MjjYud').should(have.size(11))\
            .first.should(have.text('Selenium automates browsers'))
    ```

=== "Pylenium"

    ```python
    def test_compare_api_style_example_pylenium(py):
        from selenium.webdriver.common.keys import Keys

        py.visit('https://google.com/ncr')

        search_input = py.get('[name="q"]')
        search_input.should().have_value('').type('selenium', Keys.ENTER)

        search_results = py.find('#search .MjjYud')
        assert search_results.should().have_length(11)
        assert search_results.first().should().contain_text('Selenium automates browsers')
    ```

=== "SeleniumBase"

    ```python
    def test_compare_api_style_example_seleniumbase(sb):
        sb.open("https://google.com/ncr")

        sb.assert_attribute('[name="q"]', 'value', '')
        sb.type('[name="q"]', 'selenium\n')

        assert len(sb.find_elements('#search .MjjYud')) == 11
        assert 'Selenium automates browsers' in sb.find_elements('#search .MjjYud')[0].text
    ```

=== "Helium"

    ```python
    def test_compare_api_style_example_helium():
        from helium import start_chrome, find_all, S, write, press, kill_browser
        from selenium.webdriver.common.keys import Keys

        start_chrome('https://google.com/ncr')

        assert not find_all(S('@q'))[0].web_element.text
        write('selenium')
        press(Keys.ENTER)

        search_results = find_all(S('#search .MjjYud'))
        assert len(search_results) == 11
        assert 'Selenium automates browsers' in search_results[0].web_element.text

        kill_browser()
    ```

=== "Splinter"

    ```python
    def test_compare_api_style_example_splinter():
        from splinter import Browser
        from selenium.webdriver.common.keys import Keys

        with Browser("chrome") as browser:
            browser.visit('https://google.com/ncr')

            search_input = browser.find_by_name('q')
            assert not search_input.value
            search_input.fill('selenium')
            search_input.type(Keys.RETURN)

            search_results = browser.find_by_css('#search .MjjYud')
            assert len(search_results) == 11
            assert 'Selenium automates browsers' in search_results.first.value
    ```

=== "Selenium"

    ```python
    def test_compare_api_style_example_selenium():
        from selenium.webdriver import Chrome
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys

        browser = Chrome()
        browser.get('https://google.com/ncr')

        search_input = browser.find_element(By.NAME, 'q')
        assert search_input.text == ''
        search_input.send_keys('selenium', Keys.ENTER)

        search_results = browser.find_elements(By.CSS_SELECTOR, '#search .MjjYud')
        assert len(search_results) == 11
        assert 'Selenium automates browsers' in search_results[0].text
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
!!! info "Some info might be outdated"

    Keep in mind that this document was written in March-April 2023.
    It's hard to maintain the relevance of our observations and remarks.
    But if you think that things have been changed significantly since then,
    please edit this page using the link at the top.
<!-- markdownlint-enable MD046 -->

## Splinter

The Splinter is the oldest Python framework (from the ones listed above).
Regardless of its long-term history, it remains to be a lightweight package:
you install what you need via extras (even Selenium is not included by default).
Also it does not support Python 2.7 anymore
*(in 2023, we think, this is a virtue worth cultivating)*.

**PROS:**

- Splinter will wait for an element to be in a safe state for interaction.
This prevents common errors where elements may be found before
the web application is ready.
- It supports multiple web automation back-ends.
For headless testing (WSGI applications), Splinter has drivers for
zope.testbrowser, Django and Flask clients.
- There is essential documentation with code examples and
API reference page.
- A separate plugin for pytest runner,
but with abandoned Release Notes section on GitHub.

**CONS:**

- In latest version *(`0.19.0` at the time of writing)* the Installation link
was broken on their README page.
They have divided this page and forgot to update the link.
It's not a big issue, but in the same version developers dropped support
of Selenium 3, but PyPI still thinks that there are two extras
"selenium3" and "selenium4". That's why if you want to install Selenium,
the command from docs `python -m pip install splinter[selenium]` won't work
as expected.
- There is no WebDriver manager support (this is a drawback for new users),
because even on the Tutorial page there are no words about additional
webdriver installation.
Be ready to spend time for your first test with Splinter.
Also outdated instructions for Firefox Webdriver configuration
(at least, about specifying profile).
- Not always a good choice for the name of the method (not so intuitive),
for example:
`.fill('red')`, `.mouse_out()` or `.is_text_present('<!-- Am I present? -->')`  
==TODO: the latter is my personal opinion, maybe we should not mention it, because the similar name is used in almost every framework==
- ==TODO: Add words about API (internal architecture)==  
redundant methods (each method for each type of search).  
Is API fragile?  
Or even combine with the previous list item.

## Helium

This framework also has ten years' history
(although as open source since 2019) and several hundreds of active users.
Unfortunately, it is not maintained by the author
(he accepts only PRs from users).
By the way, the author uses tabs over spaces for indentation
*(in my opinion, this fact is hardly encouraging for potential contributors)*.

The main feature of Helium is
referring to elements by user-visible labels.
*(in the modern multilingual world some people have an objection to this)*.
For common elements you can use specific classes
and find elements relative to others (below, above, to_right_of, to_left_of).
Here are several examples:

```python
Button('Sign in')
TextField('First name')
CheckBox('I accept')
RadioButton('Windows')

Text(above='Balance', below='Transactions').value
Link(to_right_of='Invoice:')
Image(to_right_of=Link('Sign in', below=Text('Navigation')))
```

**PROS:**

==These PROS from Heliums's README "as-is". (without verification)==

- iframes: Unlike Selenium, Helium lets you interact with elements inside nested iFrames, without having to first "switch to" the iFrame.
- Window management. ==Is it an advantage at all?== Helium notices when popups open or close and focuses / defocuses them like a user would. You can also easily switch to a window by (parts of) its title. No more having to iterate over Selenium window handles.
- Implicit waits. By default, if you try click on an element with Selenium and that element is not yet present on the page, your script fails. Helium by default waits up to 10 seconds for the element to appear.
Waiting time can be configured: `Config.implicit_wait_secs = 30`
- Explicit waits. Helium gives you a much nicer API for waiting for a condition on the web page to become true. For example: To wait for an element to appear in Selenium, you would write:

    ```python
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'myDynamicElement'))
    )
    ```

    With Helium, you can write:

    ```python
    wait_until(Button('Download').exists)
    ```

    ==Stay? OR Remove? example above, because there is no API example (Explicit waits) for other frameworks yet==

- Easy to switch to Selenium WebDriver API.

**CONS:**

- Due to *"lazy"* maintenance status the only old (3rd) version of Selenium is supported.
- No webdriver auto management (instead Helium ships with its own (and old) copies of ChromeDriver and geckodriver).
- Temptation to use implicit imports from one module (i.e. `from helium import *`).
- The documentation website contains only auto generated API reference page
and installation steps.
But it is worth mentioning that docstrings for API are quite well written
*(it might be enough for the vast majority of users)*.

## SeleniumBase

A powerful Python framework for browser automation and E2E UI testing.
SeleniumBase provides a lot of additional useful tools
and console scripts for getting things done quickly.
It looks like a large all-in-one combine
*(some people don't need all this "cool" stuff)*.

**PROS:**

- The great documentation with illustrative examples.
- SeleniumBase automatically downloads web drivers as needed.
And also has detailed doc page how to manually download a webdriver
(and even own CLI command for that).
- Supports pytest, unittest, nose, and behave for finding/running tests.
The latter lets you write tests with BDD Gherkin structure.
- Concise API methods *(but with several caveats, see below)*.
There is auto-detection between CSS Selectors and XPath,
which means you don't need to specify the type of selector in your commands
(but optionally you could).
SeleniumBase methods often perform multiple actions in a single method call.
(`.type()` for example).
- SeleniumBase gives you clean error output when a test fails. With raw Selenium, error messages can get very messy.
- It has its own Recorder & Test Generator that can create tests from manual browser actions.
- SeleniumBase methods automatically wait for page elements to finish loading
before interacting with them (up to a timeout limit).
This means you no longer need random time.sleep() statements in your scripts.
No more flaky tests!
- iframes follow the same principle as new windows - you need to specify the iframe if you want to take action on something in there:

    ```python
    self.switch_to_frame('ContentManagerTextBody_ifr')
    # Now you can act inside the iframe
    # .... Do something cool (here)
    self.switch_to_default_content()  # Exit the iframe when you're done
    ```

- There are deferred asserts.

    ==|Are there deferred asserts in Selene? (when test does not fail immediately after first fail, i.e. accumulate fails).==

- Easy access to raw Selenium WebDriver  
`self.driver.find_elements("partial link text", "GitHub")`

**CONS:**

- API was designed without concerns about composition fundamentals.  
==TODO: Check my translation for this remark from chat:==  
"в корне АПИ задизайнено не учитывая гибкость в контексте применения композиции - что есть основой кодинга"
- Strange choice for argument order in method `.type(selector, text)`, while in assertions methods in reverse `.assert_text(text, selector)`
- Poor API in terms of elements collection ==TODO: Or it's OK and remove?==  
because:

    > В общем - то что есть коллекция отдельная - это не факт что плюс. Более того - ну селениум же тоже находит коллекцию элементов через find_elements, в чем разница то? Она то есть конечно. Вопрос только в том - как это объяснить.

## Pylenium

This framework was created in 2020 (the youngest one).
The author has tried to bring the best of existing frameworks,
including Cypress from JS world.
That's why the Pylenium's syntax is close to Selene's.

**PROS:**

- Pylenium looks to bring more Cypress-like bindings and techniques to Selenium.
- Automatic waiting and synchronization.
- Automatic driver installation so you don't need to manage drivers.
- Nice documentation with examples.

**CONS:**

- Designed for pytest only.
- Now way to configure driver programmatically (only JSON configuration file and pytest command-line options).
- URLs are open with HTTP (not HTTPS) even URL is specified with `https://`
*(author [says][pylenium-ssl-issue] that is WebDriver issue,
however other frameworks have no such problem)*.
- Separate methods for CSS selectors and XPath.

[pylenium-ssl-issue]: https://github.com/ElSnoMan/pyleniumio/issues/294#issuecomment-1300993916

## Selene

Selene was inspired by [Selenide][selenide] from Java world.
It was designed as essential framework but with a composable approach,
that makes Selene powerful and flexible at the same time.
As well designed piece of software it requires less changes in source code
and updates to new version.

[selenide]: http://selenide.org/

**PROS:**

==TODO: Add API examples for items below where it's needed or for each item==

- User-oriented API for Selenium Webdriver (code like speak common English)
with convenient, effective ==| I replaced "powerful" to avoid repetition==  selectors.
- Smart implicit waiting and retry mechanism.
- PageObjects support (all elements are lazy-evaluated objects)
- More adequate ==| Is it right word here?==  implementation of expected conditions
with more detailed and understandable error messages.
- Elements collection filter by condition.
It lets you avoid ugly XPath expressions
and get more precise failure spot during test debug.
- Special method `.matching()` for work with HTML element as source code
(just check, without waiting).  ==TODO: Remove? OR Stay? reason: too nerdy?==
- Custom command, conditions and query ==| TODO: Remove or describe==  
I inserted it because of user feedback:  

    > Особенно с кастомных command, condition и query. За них отдельный респект

- Automatic driver management (no need to install and setup driver for quick local execution)
- Quick switching to native Selenium API in your test, at any time.

**CONS:**

- Lack of documentation and examples with detailed explanation for
each feature.
- No API reference page.
- No Safari browser support out of the box (only via Selenium WebDriver configuration).  ==TODO: Stay? OR Remove? reason: should be disadvantages but this is not so important==

## Frameworks from Java and JS worlds

==TODO: Need to write==

### Selenide

==TODO: Need to write==

### Playwright

==TODO: Need to write==
