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

from selene.common.helpers import to_by
from selene.core.entity import Element, Collection
from selene.core._browser import Browser
from selene.core.locator import Locator
from selene.core.wait import Query, Command


def attribute(name: str) -> Query[Element, str | None]:
    def fn(element: Element) -> str | None:
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


# --- Pseudo-queries --- #


class _frame_context:
    """A context manager to work with frames (iframes).
    Has an additional decorator to adapt context manager to step-methods
    when implementing a PageObject pattern.
    Partially serves as entity similar to Element
    allowing to find element or collection inside frame.
    Experimental feature.

    This is a "pseudo-query", i.e. it does not "get something" from entity.
    It's implemented as a query to be more readable in usage.

    ## Laziness on query application

    On `get(query._frame_context)`
    it actually just wraps an element into context manager and so is lazy,
    i.e. you can store result of such query into a variable
    even before opening a browser and use it later.
    Thus, unlike for other queries, there is no difference
    between using the query directly as `query._frame_context(element)`
    or via `get` method as `element.get(query._frame_context)`.

    The "lazy result" of the query is also a "lazy search context"
    similar to Element entity
    – it allows to find elements or collections inside the frame
    by using `self._element(selector)` or `self._all(selector)` methods.
    This allows the easiest and most implicit way to work with frames in Selene
    without bothering about switching to the frame and back:

    ### Example: Using query result as "search context" with fully implicit frame management

    ```python
    from selene import browser, command, have, query
    ...
    iframe = browser.element('#editor-iframe').get(query._frame_context)
    iframe._all('strong').should(have.size(0))
    iframe._element('.textarea').type('Hello, World!').perform(command.select_all)
    browser.element('#toolbar').element('#bold').click()
    iframe._all('strong').should(have.size(1))
    ```

    !!! warning

        But be aware that such syntax will force to switch to the frame and back
        for each command executed on element or collection of elements
        inside the frame. This might result in slower tests
        if you have a lot of commands to be executed all together inside the frame.

    !!! tip

        We recommend to stay
        [YAGNI](https://enterprisecraftsmanship.com/posts/yagni-revisited/)
        and use this syntax by default, but when you notice performance drawbacks,
        consider choosing an explicit way to work with frame context
        as a context manager passed to `with` statement
        or as a decorator `_within` applied to step-methods of PageObject
        as described below.

    ## Laziness ends on with statement

    On passing the "lazy result" of the query to `with` statement
    it actually transforms from "lazy query" into "actual command",
    that performs an action on the entity –
    the action of switching to the element's frame
    with the corresponding implicit waiting.

    On exiting the `with` statement it switches back to the default content,
    without any additional implicit waiting.
    This behavior might change in the future, and some waiting might be added.

    ## Example: Straightforward usage of the query (in with statement):

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

    ## Example: Usage utilizing the lazy nature of the query (in with statement)

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

    ## Example: Nested with statements for nested frames

    ```python
    from selene import browser, have, query, be

    # GIVEN even before opened browser
    browser.open('https://the-internet.herokuapp.com/nested_frames')

    # WHEN
    with browser.element('[name=frame-top]').get(query._frame_context):
        with browser.element('[name=frame-middle]').get(query._frame_context):
            browser.element(
                '#content',
                # THEN
            ).should(have.exact_text('MIDDLE'))
        # AND
        browser.element('[name=frame-right]').should(be.visible)
    ```

    ## Example: Usage utilizing the [_within][selene.core.query._frame_context._within] decorator for PageObjects:

    See example at [_within][selene.core.query._frame_context._within] section.
    """

    def __init__(self, element: Element):
        self._container = element

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
        self._container.perform(
            Command(
                'switch to frame',
                lambda entity: entity.config.driver.switch_to.frame(entity.locate()),
            )
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        driver = self._container.config.driver

        # driver.switch_to.default_content()

        # the following is kind of same but will work for nested frames too;)
        driver.switch_to.parent_frame()

    @property
    def __as_wait_decorator(self):

        # TODO: consider implementing utility function to compose decorator factories
        #       won't it be overcomplicated and not KISS then?

        def composed_wait_decorator(wait):
            def decorator(for_):
                original_wait_decorator = self._container.config._wait_decorator
                context_wait_decorator = support._wait.with_(context=self)

                for_decorator_after_context = context_wait_decorator(wait)
                for_decorator_after_original = original_wait_decorator(wait)

                # by applying context decorator first (i.e. closer to the function call)
                # we actually make it second in the chain
                for_after_context = for_decorator_after_context(for_)

                # – because lastly applied decorator will contain the first code
                # to be executed before the decorated function
                for_after_context_then_original = for_decorator_after_original(
                    for_after_context
                )

                # – so, given original decorator is a logging decorator
                # first we log the command,
                # and then we actually switch to context before running the command
                # ! This is very important because switching context for us
                # ! is a low level command, that's why it should be "logged as second"
                # ! that in reports like allure will also be "nested" on a deeper level
                return for_after_context_then_original

            return decorator

        return composed_wait_decorator

    def _element(self, selector: str | typing.Tuple[str, str]) -> Element:
        """Allows to search for a first element by selector inside the frame context
        with implicit switching to the frame and back for each method execution.

        Is lazy, i.e. does not switch to the frame immediately on calling this method,
        and so can be stored in a variable and used later.

        Args:
            selector: css or xpath as string or classic selenium tuple-like locator,
            e.g. `('css selector', '.some-class')` or `(By.CSS_SELECTOR, '.some-class')`
        """
        by = to_by(selector)

        return Element(
            Locator(
                f'{self._container}: element({by})',
                # f'{self._container} {{ element({by}) }}',  # TODO: maybe this?
                lambda: self._container.config.driver.find_element(*by),
            ),
            self._container.config.with_(_wait_decorator=self.__as_wait_decorator),
        )

    def _all(self, selector: str | typing.Tuple[str, str]) -> Collection:
        """Allows to search for all elements by selector inside the frame context
        with implicit switching to the frame and back for each method execution.

        Is lazy, i.e. does not switch to the frame immediately on calling this method,
        and so can be stored in a variable and used later.

        Args:
            selector: css or xpath as string or classic selenium tuple-like locator,
            e.g. `('css selector', '.some-class')` or `(By.CSS_SELECTOR, '.some-class')`
        """
        by = to_by(selector)

        return Collection(
            Locator(
                f'{self._container}: all({by})',
                lambda: self._container.config.driver.find_elements(*by),
            ),
            self._container.config.with_(_wait_decorator=self.__as_wait_decorator),
        )


# The following is not needed once we now have switch_to.parent_frame()
# in _frame_context itself
# class _nested_frame_context(_frame_context):
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         driver = self._container.config.driver
#         driver.switch_to.parent_frame()


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
