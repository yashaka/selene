# MIT License
#
# Copyright (c) 2015-2022 Iakiv Kramarenko
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
import typing
from typing import List, Dict, Any, Union

from selenium.webdriver.remote.webelement import WebElement

from selene.core.entity import Browser, Element, Collection
from selene.core.wait import Query


def attribute(name: str) -> Query[Element, str]:
    def fn(element: Element) -> str:
        return element().get_attribute(name)

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
        else len(entity())
        if isinstance(entity, Collection)
        else typing.cast(Browser, entity).driver.get_window_size()
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
