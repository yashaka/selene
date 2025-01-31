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

tag: Query[Element, str] = Query('tag name', lambda element: element.locate().tag_name)
```

– As you can see, it all comes simply to define a function or lambda on entity object
and wrap it into Query😇.

For more examples of how to build your own custom queries
see the actual implementation of Selene's queries in this module.

# The actual list of queries ↙️
"""
from __future__ import annotations

import typing
import warnings

from typing_extensions import (
    List,
    Dict,
    Any,
    Union,
)

from selenium.webdriver.remote.webelement import WebElement

from selene.common._typing_functions import Query
from selene.core import entity
from selene.core.entity import Element, Collection
from selene.core._browser import Browser
from selene.core.locator import Locator
from selene.web._elements import _FrameContext


# TODO: should not we separate Query type from actual queries implementations?


def attribute(name: str) -> Query[Element, str]:
    """A query that gets the value of the attribute of the element

    Args:
        name (str): name of the attribute
    """

    def fn(element: Element):
        return element.locate().get_attribute(name)

    return Query(f'attribute {name}', fn)


def attributes(name: str) -> Query[Collection, List[str]]:
    """A query that gets the values of the attribute of all elements in the collection

    Args:
        name (str): name of the attribute
    """

    def fn(collection: Collection):
        return [element.get_attribute(name) for element in collection.locate()]

    return Query(f'{name} attributes', fn)


inner_html = attribute('innerHTML')
inner_htmls = attributes('innerHTML')


outer_html = attribute('outerHTML')
outer_htmls = attributes('outerHTML')


text_content = attribute('textContent')
"""
full text of element without space normalization
"""
texts_content = attributes('textContent')
"""
full text of element without space normalization
"""


value = attribute('value')
values = attributes('value')

tag: Query[Element, str] = Query('tag name', lambda element: element.locate().tag_name)
tags: Query[Collection, List[str]] = Query(
    'tag names',
    lambda collection: [element.tag_name for element in collection.locate()],
)

text: Query[Element, str] = Query('text', lambda element: element.locate().text)
"""normalized text of element"""
texts: Query[Collection, List[str]] = Query(
    'texts',
    lambda collection: (
        [element.text for element in collection.locate()]
        # [element.text for element in collection.locate() if element.is_displayed()]
        # if collection.config._filter_all_elements_for_visibility
        # else [element.text for element in collection.locate()]
    ),
)
"""list of normalized texts of all elements in collection"""
visible_texts: Query[Collection, List[str]] = Query(
    'visible texts',
    lambda collection: [
        element.text for element in collection.locate() if element.is_displayed()
    ],
)
"""list of normalized texts of all visible elements in collection"""

# TODO: add texts collection condition

# TODO: do we need condition for the following?
location_once_scrolled_into_view: Query[Element, Dict[str, int]] = Query(
    'location once scrolled into view',
    lambda element: element.locate().location_once_scrolled_into_view,
)

# TODO: what to do now with have.size* ? o_O
size: Query[Element | Collection | Browser, dict | int] = Query(
    'size',
    # TODO: refactor this to avoid using typing.cast or type: ignore
    #       by introducing isinstance based checks on some BaseClass for specific entity types
    lambda some_entity: (
        some_entity.driver.get_window_size()  # type: ignore
        if entity._wraps_driver(some_entity)
        else (
            some_entity.locate().size  # type: ignore
            if entity._is_element(some_entity)
            else (
                len(some_entity.locate())  # type: ignore
                if entity._is_collection(some_entity)
                # TODO: refactor this redundant else clause o_O
                else typing.cast(Browser, some_entity).driver.get_window_size()
            )
        )
    ),
)

# TODO: do we need condition for the following?
location: Query[Element, Dict[str, int]] = Query(
    'location', lambda element: element.locate().location
)

# TODO: do we need condition for the following?
rect: Query[Element, Dict[str, Any]] = Query(
    'rect', lambda element: element.locate().rect
)

screenshot_as_base64: Query[Element, Any] = Query(
    'screenshot as base64', lambda element: element.locate().screenshot_as_base64
)

screenshot_as_png: Query[Element, Any] = Query(
    'screenshot as png', lambda element: element.locate().screenshot_as_png
)


def screenshot(filename: str) -> Query[Element, bool]:
    def func(element: Element) -> bool:
        return element.locate().screenshot(filename)

    return Query(f'screenshot {filename}', func)


# not needed, because interfere with "parent element" meaning and usually can be workaround via element.config.driver
# parent: Query[Element, Any] = \
#     Query('parent', lambda element: element.locate().parent)
# TODO: but should we add it with another name?


internal_id: Query[Element, Any] = Query(
    'internal id', lambda element: element.locate().id
)


def css_property(name: str) -> Query[Element, str]:
    def fn(element: Element) -> str:
        return element.locate().value_of_css_property(name)

    return Query(f'css property {name}', fn)


def css_properties(name: str) -> Query[Collection, List[str]]:
    """A query that gets the values of the css properties of all elements
    in the collection

    Args:
        name (str): name of the attribute
    """

    def fn(collection: Collection):
        return [element.value_of_css_property(name) for element in collection.locate()]

    return Query(f'{name} css properties', fn)


def native_property(
    name: str,
) -> Query[Element, Union[str, bool, WebElement, dict]]:
    def func(element: Element) -> Union[str, bool, WebElement, dict]:
        return element.locate().get_property(name)

    return Query(f'native property {name}', func)


def native_properties(name: str) -> Query[Collection, List[str]]:
    """A query that gets the values of the native properties of all elements
    in the collection

    Args:
        name (str): name of the attribute
    """

    def fn(collection: Collection):
        return [element.get_property(name) for element in collection.locate()]

    return Query(f'{name} native properties', fn)


def js_property(
    name: str,
) -> Query[Element, Union[str, bool, WebElement, dict]]:
    warnings.warn('deprecated: use query.native_property instead', DeprecationWarning)
    return native_property(name)


# --- Pseudo queries --- #

frame_context = _FrameContext

# --- Browser queries --- #

url: Query[Browser, str] = Query('url', lambda browser: browser.driver.current_url)

title: Query[Browser, str] = Query('title', lambda browser: browser.driver.title)

# todo: should we use more low level name? actually... the 'window_handles' one?
#       or should we just provide an alias to query.tabs as query.window_handles?
#       to provide both option for the end user to choose depending on context?
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

    if entity._wraps_driver(path):
        # somebody passed query as `.get(query.save_screenshot)`
        # not as `.get(query.save_screenshot())`
        driver_wrapper = path
        return query.__call__(driver_wrapper)  # type: ignore

    return query


def page_source_saved(
    path: typing.Optional[str] = None,
) -> Query[Browser, typing.Optional[str]]:
    query: Query[Browser, typing.Optional[str]] = Query(
        'save and get page source',
        lambda browser: browser.config._save_page_source_strategy(browser.config, path),
    )

    if entity._wraps_driver(path):
        # somebody passed query as `.get(query.save_screenshot)`
        # not as `.get(query.page_source_saved())`
        driver_wrapper = path
        return query.__call__(driver_wrapper)  # type: ignore

    return query


class js:
    shadow_root: Query[Element, Element] = Query(
        'shadow root',
        # TODO: use _ElementsContext instead
        lambda element: Element(
            Locator(
                f'{element}.shadow root',
                lambda: element.config.driver.execute_script(
                    'return arguments[0].shadowRoot', element.locate()
                ),
            ),
            element.config,
        ),
    )
    """A lazy query that actually builds an Element entity
    based on element's shadow root acquired via JavaScript.
    """

    shadow_roots: Query[Collection, Collection] = Query(
        'shadow roots',
        lambda collection: Collection(
            Locator(
                f'{collection}.shadow roots',
                lambda: collection.config.driver.execute_script(
                    'return [...arguments[0]].map(arg => arg.shadowRoot)',
                    collection.locate(),
                ),
            ),
            collection.config,
        ),
    )
    """A lazy query that actually builds a Collection entity
    based on elements' shadow roots acquired via JavaScript.
    """
