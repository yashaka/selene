# MIT License
#
# Copyright (c) 2015 Iakiv Kramarenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
# Module overview

This module contains a set of advanced functionality that can be used in addition
to the standard Selene method like `entity.locate()`
when you need to acquire some information from a Selene entity.
Functions defined in this module are called "queries",
because they get and return some information about the entity,
unlike [advanced commands][selene.core.command--module-overview]
that perform some actions and return the entity itself.
Thus, an advanced queries are defined outside the entity class, here in this module,
and given named as `advanced_query` then can be executed on entity
via `entity.get(advanced_query)`.

The idiomatic way to use advanced queries is to import the whole module:

```python
from selene import browser, have, query  # ❗️over from selene.core.query import text

# GIVEN
...
current_price = browser.element('#cart-price').get(query.text)  # ⬅️ used via module

# WHEN
browser.all('.product').element_by(have.text('Apple')).element('#add-to-cart').click()

# THEN
browser.element('#cart-price').should(
    have.exact_text(str(float(current_price) + 1.99))
)
```

Thus, you don't need to remember all available queries,
you just import the module and select the one you need
from the list of suggestions among `query.*`.

# Why do we need a separate module for queries, why not element.text?

– Because the test in previous example
that asserts final price based on original price – is not a perfect test.
A good test case is a "case with strictly defined preconditions",
where we know for sure what will happen, after what,
and with exact expected results.
Therefore, in the example above,
we should know in-forward the final price of the cart,
there is no need to "store original price" and then "calculate final".
And here, in Selene, we follow the principle:
"A good design is one that makes it easy to do the right thing
and hard to do the wrong thing".

That's why all "queries" were intentionally removed from entities
and moved to the separate module,
so that it's harder to use them on regular basis.
As by default, we allways should try to implement "the perfect test"
that implies we know in forward the exact state of the system on each test step.
Then we don't need to "get from entity" and "store" intermediate results,
like "current price", and once we do assertion,
we already have expected conditions:

```python
from selene import browser, have  # ❗️ have.* are expected conditions;)

...
# THEN
browser.element('#cart-price').should(have.exact_text('11.99'))
```

Expected conditions like `have.exact_text` or `be.visible`
are better than using "assert + get query":

```python
from selene import browser

...
# THEN
assert browser.element('#cart-price').text == '11.99'
```

– because such "simple assertion" does now support smart implicit waiting,
that is crucial for stable and fast tests of modern web applications
that are dynamic in nature.

That's why there is no easy syntax like `element.text` in Selene.
If you really need to get some information from the entity
(sometimes you really do need it, in case of some limitations on the project, etc.),
at least, you have to think twice to use available but less handy syntax in Selene –
like `element.get(query.text)`.

!!! tip

    Yet you can always [extend Selene][how-to-extend-selene] entities
    with your own queries built in.

# Why and how to implement custom queries?

The list of advanced queries in this module is far from exhaustive,
and there is no goal to make it complete, because in many cases, the end user
will need his own list of custom queries specific to his application context.
But this list can be a good starting point for such custom queries.
Taking the latter into account we try to keep implementation of the queries
in this module – as simple as possible,
so that the end user can easily understand them
and use as examples to implement own custom queries.
That's why we avoid following DRY principle here,
and prefer pure selenium code
over reusing already implemented in Selene helpers.

The pattern to implement a custom query is
[same as described for Selene custom commands][selene.core.command--how-to-implement-custom-advanced-commands].

Here are just a simple example:

```python
# Full path can be: my_tests_project/extensions/selene/command.py

from selene.core.query import *
from selene.core.wait import Query
from selene import Browser


def __get_browser_logs(browser: Browser):
    return browser.driver.get_log('browser')


logs: Query[Browser, list] = Query('browser logs', __get_browser_logs)

```

– to be used as

```python
from selene import browser,
from my_project_root.extensions.selene import query

browser.open('https://todomvc-emberjs-app.autotest.how/')
print(browser.get(query.logs))
...
```

And here are a few implementation examples of already available queries in Selene:

```python
def attribute(name: str) -> Query[Element, str]:
    def fn(element: Element):
        return element.locate().get_attribute(name)

    return Query(f'attribute {name}', fn)


inner_html = attribute('innerHTML')
text_content = attribute('textContent')
value = attribute('value')

tag: Query[Element, str] = Query('tag name', lambda element: element().tag_name)
```

– As you can see, it all comes simply to define a function or lambda on entity object
and wrap it into Query😇.

For more examples of how to build your own custom queries
see the actual implementation of Selene's queries in this module.

# The actual list of queries ↙️
"""
from __future__ import annotations

import functools
import typing
from typing import List, Dict, Any, Union

from selenium.webdriver.remote.webelement import WebElement

from selene.core.entity import Element, Collection
from selene.core._browser import Browser
from selene.core.wait import Query, Command


def attribute(name: str) -> Query[Element, str]:
    def fn(element: Element):
        return element.locate().get_attribute(name)

    return Query(f'attribute {name}', fn)


inner_html = attribute('innerHTML')


outer_html = attribute('outerHTML')


text_content = attribute('textContent')
"""
full text of element without space normalization
"""


value = attribute('value')

tag: Query[Element, str] = Query('tag name', lambda element: element().tag_name)

text: Query[Element, str] = Query('text', lambda element: element().text)
"""
normalized text of element
"""

# TODO: do we need condition for the following?
location_once_scrolled_into_view: Query[Element, Dict[str, int]] = Query(
    'location once scrolled into view',
    lambda element: element().location_once_scrolled_into_view,
)

# TODO: what to do now with have.size* ? o_O
size: Query[Union[Element, Collection, Browser], Union[dict, int]] = Query(
    'size',
    lambda entity: (
        entity().size
        if isinstance(entity, Element)
        else (
            len(entity())
            if isinstance(entity, Collection)
            else typing.cast(Browser, entity).driver.get_window_size()
        )
    ),
)

# TODO: do we need condition for the following?
location: Query[Element, Dict[str, int]] = Query(
    'location', lambda element: element().location
)

# TODO: do we need condition for the following?
rect: Query[Element, Dict[str, Any]] = Query('rect', lambda element: element().rect)

screenshot_as_base64: Query[Element, Any] = Query(
    'screenshot as base64', lambda element: element().screenshot_as_base64
)

screenshot_as_png: Query[Element, Any] = Query(
    'screenshot as png', lambda element: element().screenshot_as_png
)


def screenshot(filename: str) -> Query[Element, bool]:
    def func(element: Element) -> bool:
        return element().screenshot(filename)

    return Query(f'screenshot {filename}', func)


# not needed, because interfere with "parent element" meaning and usually can be workaround via element.config.driver
# parent: Query[Element, Any] = \
#     Query('parent', lambda element: element().parent)
# TODO: but should we add it with another name?


internal_id: Query[Element, Any] = Query('internal id', lambda element: element().id)


def css_property(name: str) -> Query[Element, str]:
    def fn(element: Element) -> str:
        return element().value_of_css_property(name)

    return Query(f'css property {name}', fn)


def js_property(
    name: str,
) -> Query[Element, Union[str, bool, WebElement, dict]]:
    def func(element: Element) -> Union[str, bool, WebElement, dict]:
        return element().get_property(name)

    return Query(f'js property {name}', func)


class _frame_context:
    """A context manager to work with frames (iframes).
    Has an additional decorator to adapt context manager to step-methods
    when implementing a PageObject pattern. Experimental feature.

    This is a "pseudo-query", i.e. it does not "get something" from entity.
    It's implemented as a query to be more readable in usage.

    On `get(query._frame_context)`
    it actually just wraps an element into context manager and so is lazy,
    i.e. you can store result of such query into a variable
    even before opening a browser and use it later.

    On passing the "lazy result" of the query to `with` statement
    it actually transforms from "lazy query" into "actual command",
    that performs an action on the entity –
    the action of switching to the element's frame
    with the corresponding implicit waiting.

    On exiting the `with` statement it switches back to the default content,
    without any additional implicit waiting.
    This behavior might change in the future, and some waiting might be added.

    ## Example: Straightforward usage of the query

    ```python
    from selene import browser, query, command, have

    toolbar = browser.element('.tox-toolbar__primary')
    text_area_frame = browser.element('.tox-edit-area__iframe')
    text_area = browser.element('#tinymce')  # ❗️ inside the frame

    browser.open('https://the-internet.herokuapp.com/iframe')

    with text_area_frame.get(query._frame_context):
        text_area.perform(command.select_all)

    toolbar.element('[title=Bold]').click()

    with text_area_frame.get(query._frame_context):
        text_area.element('p').should(
            have.js_property('innerHTML').value(
                '<strong>Your content goes here.</strong>'
            )
        )
    ```

    ## Example: Usage utilizing the lazy nature of the query:

    ```python
    from selene import browser, query, command, have

    toolbar = browser.element('.tox-toolbar__primary')
    text_area_frame = browser.element('.tox-edit-area__iframe')
    text_area_frame_context = text_area_frame.get(query._frame_context)  # 💡↙️
    text_area = browser.element('#tinymce')

    browser.open('https://the-internet.herokuapp.com/iframe')

    with text_area_frame_context:  # ⬅️
        text_area.perform(command.select_all)

    toolbar.element('[title=Bold]').click()

    with text_area_frame_context:  # ⬅️
        text_area.element('p').should(
            have.js_property('innerHTML').value(
                '<strong>Your content goes here.</strong>'
            )
        )
    ```

    ## Example: Usage utilizing the lazy nature of the query without get method:

    Since the query application is fully lazy
    (laziness ends only on `with` statement),
    you can use it directly, without `get` method:

    ```python
    from selene import browser, query, command, have

    toolbar = browser.element('.tox-toolbar__primary')
    text_area_frame = browser.element('.tox-edit-area__iframe')
    text_area_frame_context = query._frame_context(text_area_frame)  # 💡↙️
    text_area = browser.element('#tinymce')

    browser.open('https://the-internet.herokuapp.com/iframe')

    with text_area_frame_context:  # ⬅️
        text_area.perform(command.select_all)

    toolbar.element('[title=Bold]').click()

    with text_area_frame_context:  # ⬅️
        text_area.element('p').should(
            have.js_property('innerHTML').value(
                '<strong>Your content goes here.</strong>'
            )
        )
    ```

    ## Example: Usage utilizing the [_within][selene.core.query._frame_context._within] decorator for PageObjects:

    See example at [_within][selene.core.query._frame_context._within] section.
    """

    def __init__(self, element: Element):
        self.element = element

    def decorator(self, func):
        """A decorator to mark a function as a step within context manager

        See example of usage at [_within][selene.core.query._frame_context._within] section.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper

    # aliases :) TODO: not sure which to keep
    _step = decorator
    _steps = decorator
    _content = decorator
    _inside = decorator
    _inner = decorator
    _within = decorator
    """An alias to [`decorator`][selene.core.query._frame_context.decorator]

    Example of usage:

    ```python
    from selene import browser, command, have, query


    def teardown_function():
        browser.quit()


    class WYSIWYG:
        toolbar = browser.element('.tox-toolbar__primary')
        text_area_frame = query._frame_context(  # 💡⬇️
            browser.element('.tox-edit-area__iframe')
        )
        text_area = browser.element('#tinymce')

        def open(self):
            browser.open('https://the-internet.herokuapp.com/iframe')
            return self

        def set_bold(self):
            self.toolbar.element('[title=Bold]').click()
            return self

        @text_area_frame._within  # ⬅️
        def should_have_text_html(self, text_html):
            self.text_area.should(have.js_property('innerHTML').value(text_html))
            return self

        @text_area_frame._within  # ⬅️
        def select_all_text(self):
            self.text_area.perform(command.select_all)
            return self

        @text_area_frame._within  # ⬅️
        def reset_to(self, text):
            self.text_area.perform(command.select_all).type(text)
            return self


    def test_page_object_steps_within_frame_context():
        wysiwyg = WYSIWYG().open()

        wysiwyg.should_have_text_html(
            '<p>Your content goes here.</p>',
        ).select_all_text().set_bold().should_have_text_html(
            '<p><strong>Your content goes here.</strong></p>',
        )

        wysiwyg.reset_to('New content').should_have_text_html(
            '<p><strong>New content</strong></p>',
        )
    ```
    """

    def __enter__(self):
        self.element.perform(
            Command(
                'switch to frame',
                lambda entity: entity.config.driver.switch_to.frame(entity.locate()),
            )
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        driver = self.element.config.driver
        driver.switch_to.default_content()


# --- Collection queries --- #

# --- Browser queries --- #


url: Query[Browser, str] = Query('url', lambda browser: browser.driver.current_url)

title: Query[Browser, str] = Query('title', lambda browser: browser.driver.title)

tabs: Query[Browser, List[str]] = Query(
    'tabs', lambda browser: browser.driver.window_handles
)

tabs_number: Query[Browser, int] = Query(
    'tabs number', lambda browser: len(browser.driver.window_handles)
)


def tab(index: int) -> Query[Browser, str]:
    def fn(browser: Browser) -> str:
        return browser.driver.window_handles[index]

    return Query(f'tab by index {index}', fn)


current_tab: Query[Browser, str] = Query(
    'current tab (window handle)',
    lambda browser: browser.driver.current_window_handle,
)


def __next_tab_fn(browser: Browser) -> str:
    tabs = browser.driver.window_handles
    current = browser.driver.current_window_handle
    current_index = tabs.index(current)
    return tabs[0] if current_index >= len(tabs) - 1 else tabs[current_index + 1]


next_tab: Query[Browser, str] = Query('next tab', __next_tab_fn)


def __previous_tab_fn(browser: Browser) -> str:
    tabs = browser.driver.window_handles
    current = browser.driver.current_window_handle
    current_index = tabs.index(current)
    return tabs[-1] if current_index == 0 else tabs[current_index - 1]


previous_tab: Query[Browser, str] = Query('previous tab', __previous_tab_fn)


page_source: Query[Browser, str] = Query(
    'page source', lambda browser: browser.driver.page_source
)


# TODO: consider changing entity.get signature to accept query builders,
#       not jus query objects
def screenshot_saved(
    path: typing.Optional[str] = None,
) -> Query[Browser, typing.Optional[str]]:
    query: Query[Browser, typing.Optional[str]] = Query(
        'save and get screenshot',
        lambda browser: browser.config._save_screenshot_strategy(browser.config, path),
    )

    if isinstance(path, Browser):
        # somebody passed query as `.get(query.save_screenshot)`
        # not as `.get(query.save_screenshot())`
        browser = path
        return query.__call__(browser)  # type: ignore

    return query


def page_source_saved(
    path: typing.Optional[str] = None,
) -> Query[Browser, typing.Optional[str]]:
    query: Query[Browser, typing.Optional[str]] = Query(
        'save and get page source',
        lambda browser: browser.config._save_page_source_strategy(browser.config, path),
    )

    if isinstance(path, Browser):
        # somebody passed query as `.get(query.save_screenshot)`
        # not as `.get(query.page_source_saved())`
        browser = path
        return query.__call__(browser)  # type: ignore

    return query
