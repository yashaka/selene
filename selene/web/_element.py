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
# type: ignore # TODO: remove finally
from __future__ import annotations

import functools

import typing_extensions as typing
from typing_extensions import (
    Union,
    Callable,
    Tuple,
    Optional,
    Self,
    override,
)

from selene import support
from selene.common.fp import pipe
from selene.common._typing_functions import Command
from selene.core.configuration import Config
from selene.core.locator import Locator
from selene.core.wait import Wait
from selene.core._elements_context import _ElementsContext
from selene.core._elements import All
from selene import core

from selene.core.exceptions import TimeoutException, _SeleneError

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


class Element(core.Element):
    def __init__(
        self,
        locator: Locator[WebElement],
        config: Config,
        **kwargs,
    ):
        _Element = kwargs.pop('_Element', self.__class__)
        _All = kwargs.pop('_All', core.All)
        super().__init__(
            locator=locator,
            config=config,
            _Element=_Element,
            _All=_All,
            **kwargs,
        )

    # --- _WaitingConfiguredEntity --- #

    @staticmethod
    def _log_webelement_outer_html_for(
        element: Element,
    ) -> Callable[[TimeoutException], Exception]:
        def log_webelement_outer_html(error: TimeoutException) -> Exception:
            from selene.core import query
            from selene.core.match import present_in_dom

            cached = element.cached

            if cached.matching(present_in_dom):
                return TimeoutException(
                    f'{error.msg}\n'
                    f'Actual webelement: {query.outer_html(element)}'  # type: ignore
                )
            else:
                return error

        return log_webelement_outer_html

    @override
    @property
    def wait(self) -> Wait[Self]:
        # TODO: fix that will disable/break shared hooks (snapshots)
        # return Wait(self,  # TODO:  isn't it slower to create it each time from scratch? move to __init__?
        #             at_most=self.config.timeout,
        #             or_fail_with=pipe(
        #                 Element._log_webelement_outer_html_for(self),
        #                 self.config.hook_wait_failure))
        if self.config.log_outer_html_on_failure:
            # TODO: remove this part completely from core.entity logic
            #       move it to support.shared.config
            return super().wait.or_fail_with(
                pipe(
                    Element._log_webelement_outer_html_for(self),
                    super().wait.hook_failure,
                )
            )
        else:
            return super().wait

    # --- _ElementsContext: Aliases --- #

    # TODO: should we add Locator to Union?
    # TODO: should we type hint return type as Self?
    def s(self, selector_or_by: Union[str, Tuple[str, str]], /) -> Element:
        """A JQuery-like alias (~ $) to
        [Element.element(selector_or_by)][selene.web._elements.Element.element].
        """
        return self.element(selector_or_by)

    def ss(self, selector_or_by: Union[str, Tuple[str, str]], /) -> All[Element]:
        """A JQuery-like alias (~ $$) to
        [Element.all(selector_or_by)][selene.web._elements.Element.all].
        """
        return self.all(selector_or_by)

    # --- _ElementsContext: Extensions --- #

    @property
    def shadow_root(self) -> _ElementsContext:
        return _ElementsContext(
            locator=Locator(f'{self}.shadow root', lambda: self.locate().shadow_root),
            config=self.config,
            _Element=self._Element,
            _All=self._All,
        )

    @property
    def frame_context(self) -> _FrameContext:
        """A context manager to work with frames (iframes).
        Has an additional decorator to adapt context manager to step-methods
        when implementing a PageObject pattern.
        Partially serves as entity similar to Element
        allowing to find element or collection inside frame.

        Technically it's a shortcut to `_FrameContext(element)`
        and also is pretty similar to `element.get(_FrameContext)` query.
        Find more details in the [_FrameContext][selene.web._elements._FrameContext] docs.
        """

        return _FrameContext(self)

    # --- Commands --- #

    def set_value(self, value: Union[str, int]) -> Element:
        # TODO: should we move all commands like following or queries like in conditions - to separate py modules?
        # TODO: should we make them webelement based (Callable[[WebElement], None]) instead of element based?
        def fn(element: Element):
            webelement = (
                element._actual_not_overlapped_webelement
                if self.config.wait_for_no_overlap_found_by_js
                else element()
            )
            webelement.clear()  # TODO: change to impl based not on clear, because clear generates post-events...
            webelement.send_keys(str(value))

        from selene.core import command

        # TODO: should we log the webelement source in the command name below?
        #       i.e. change from:
        #
        #   else Command(f'set value: {value}', fn)
        #
        #       to more low level:
        #
        #   else (
        #       Command(f'actual_not_overlapped_webelement.clear().send_keys({value})', fn)
        #       if self.config.wait_for_no_overlap_found_by_js
        #       else
        #       Command(f'actual_webelement.clear().send_keys({value})', fn)
        #   )
        #
        self.wait.for_(
            command.js.set_value(value)
            if self.config.set_value_by_js
            else Command(f'set value: {value}', fn)
        )

        # TODO: consider returning self.cached, since after first successful call,
        #       all next ones should normally pass
        #       no waiting will be needed normally
        #       if yes - then we should pass fn commands to wait.for_ so the latter will return webelement to cache
        #       also it will make sense to make this behaviour configurable...
        return self

    def set(self, value: Union[str, int]) -> Element:
        """
        Sounds similar to Element.set_value(self, value), but considered to be used in broader context.
        For example, a use can say «Set gender radio to Male» but will hardly say «Set gender radio to value Male».
        Now imagine, on your project you have custom html implementation of radio buttons,
        and want to teach selene to set such radio-button controls
        – you can do this via Element.set(self, value) method,
        after monkey-patching it according to your behavior;)
        """
        return self.set_value(value)

    def _actual_visible_webelement_and_maybe_its_cover(
        self, center_x_offset=0, center_y_offset=0
    ) -> Tuple[WebElement, WebElement]:
        # TODO: will it be faster render outerHTML via lazy rendered SeleneError
        #       instead of: throw `element ${element.outerHTML} is not visible`
        #       in below js
        results = self.execute_script(
            '''
                var centerXOffset = arguments[0];
                var centerYOffset = arguments[1];

                var isVisible = !!(
                    element.offsetWidth
                    || element.offsetHeight
                    || element.getClientRects().length
                ) && window.getComputedStyle(element).visibility !== 'hidden'

                if (!isVisible) {
                    throw `element ${element.outerHTML} is not visible`
                }

                var rect = element.getBoundingClientRect();
                var x = rect.left + rect.width/2 + centerXOffset;
                var y = rect.top + rect.height/2 + centerYOffset;

                // TODO: now we return [element, null]
                //       in case of elementFromPoint returns null
                //       (kind of – if we don't know what to do,
                //       let's at least not block the execution...)
                //       rethink this... and handle the iframe case
                //       read more in
// https://developer.mozilla.org/en-US/docs/Web/API/Document/elementFromPoint

                var elementByXnY = document.elementFromPoint(x,y);
                if (elementByXnY == null) {
                    return [element, null];
                }

                var isNotOverlapped = element.isSameNode(elementByXnY);

                return isNotOverlapped
                       ? [element, null]
                       : [element, elementByXnY];
            ''',
            center_x_offset,
            center_y_offset,
        )
        webelement = results[0]
        maybe_cover = results[1]

        return webelement, maybe_cover

    @property
    def _actual_not_overlapped_webelement(self):
        (
            webelement,
            maybe_cover,
        ) = self._actual_visible_webelement_and_maybe_its_cover()
        if maybe_cover is not None:
            raise _SeleneError(
                lambda: f'Element: {webelement.get_attribute("outerHTML")}\n'
                + '\tis overlapped by: '
                + maybe_cover.get_attribute("outerHTML")
            )

        return webelement

    def type(self, text: Union[str, int]) -> Element:
        """Simulates typing text into a text-like field element.
        A human readable alternative to pure Selenium's send_keys method.

        Will wait till the element is not covered by any other element like overlays, if
        [config.wait_for_no_overlap_found_by_js][selene.core.configuration.Config.wait_for_no_overlap_found_by_js]
        is set to True.
        """

        def fn(element: Element):
            if self.config.wait_for_no_overlap_found_by_js:
                webelement = element._actual_not_overlapped_webelement
            else:
                webelement = element()
            webelement.send_keys(str(text))

        from selene.core import command

        self.wait.for_(
            command.js.type(text)
            if self.config.type_by_js
            else Command(f'type: {text}', fn)
        )

        return self

    def send_keys(self, *value) -> Element:
        """To be used for more low level operations like «uploading files», etc.
        To simulate normal input of keys by user when typing - consider using
        [Element.type(self, text)][selene.web._elements.Element.type]
        that has additional customizaton to wait for the element
        to be not overlapped by other elements.
        """
        self.wait.command('send keys', lambda element: element().send_keys(*value))
        return self

    def press(self, *keys) -> Element:
        """Simulates pressing keys on the element.
        A human readable alternative to pure Selenium's send_keys method.

        Can be customized via
        [config.wait_for_no_overlap_found_by_js][selene.core.configuration.Config.wait_for_no_overlap_found_by_js].
        """

        def fn(element: Element):
            webelement = (
                element._actual_not_overlapped_webelement
                if self.config.wait_for_no_overlap_found_by_js
                else element()
            )
            webelement.send_keys(*keys)

        self.wait.command(f'press keys: {keys}', fn)

        return self

    def press_enter(self) -> Element:
        return self.press(Keys.ENTER)

    def press_escape(self) -> Element:
        return self.press(Keys.ESCAPE)

    def press_tab(self) -> Element:
        return self.press(Keys.TAB)

    def clear(self) -> Element:
        """Clears the text in a text-like field element.

        Can be customized via
        [config.wait_for_no_overlap_found_by_js][selene.core.configuration.Config.wait_for_no_overlap_found_by_js]
        """

        def fn(element: Element):
            webelement = (
                element._actual_not_overlapped_webelement
                if self.config.wait_for_no_overlap_found_by_js
                else element()
            )
            webelement.clear()

        self.wait.command('clear', fn)

        return self

    def submit(self) -> Element:
        """Submits a form-like element.

        Can be customized via
        [config.wait_for_no_overlap_found_by_js][selene.core.configuration.Config.wait_for_no_overlap_found_by_js].
        """

        def fn(element: Element):
            webelement = (
                element._actual_not_overlapped_webelement
                if self.config.wait_for_no_overlap_found_by_js
                else element()
            )
            webelement.submit()

        self.wait.command('submit', fn)

        return self

    # TODO: consider support of percentage in offsets (in command.js.click too)
    def click(self, *, xoffset=0, yoffset=0) -> Element:
        """Just a normal click with optional offset:)

        By default, if not offset is asked, will wait till the element is not
        covered by any other element like overlays, because this is a pure
        Selenium WebDriver behavior.

        If you start specifying offsets, then, if you still want to wait for no
        overlap, you should explicitly ask for it via setting to True the
        [config.wait_for_no_overlap_found_by_js][selene.core.configuration.Config.wait_for_no_overlap_found_by_js].

        If you want to simulate a click via JS, by turning on the
        [config.click_by_js][selene.core.configuration.Config.click_by_js],
        then unless [#566](https://github.com/yashaka/selene/issues/566) issue
        is resolved, you can't wait for no overlap. After you can use
        something like:
        `browser.element('#save').should(be.not_overlapped).with_(click_by_js=True).click()`
        """

        def raw_click(element: Element):
            element.locate().click()

        def click_with_offset_actions(element: Element):
            actions: ActionChains = ActionChains(self.config.driver)
            webelement = (
                element._actual_not_overlapped_webelement
                if self.config.wait_for_no_overlap_found_by_js
                else element.locate()
            )
            actions.move_to_element_with_offset(
                webelement, xoffset, yoffset
            ).click().perform()

        from selene.core import command

        self.wait.for_(
            command.js.click(xoffset=xoffset, yoffset=yoffset)
            if self.config.click_by_js
            else (
                Command('click', raw_click)
                if (not xoffset and not yoffset)
                else Command(
                    f'click(xoffset={xoffset},yoffset={yoffset})',
                    click_with_offset_actions,
                )
            )
        )

        return self

    def double_click(self) -> Element:
        """Double clicks on the element.

        Can be customized via
        [config.wait_for_no_overlap_found_by_js][selene.core.configuration.Config.wait_for_no_overlap_found_by_js].
        """
        actions: ActionChains = ActionChains(self.config.driver)

        def fn(element: Element):
            webelement = (
                element._actual_not_overlapped_webelement
                if self.config.wait_for_no_overlap_found_by_js
                else element.locate()
            )
            actions.double_click(webelement).perform()

        self.wait.command('double click', fn)

        return self

    def context_click(self) -> Element:
        """Context clicks (aka right-click to open a popup menu) on the element.

        Can be customized via
        [config.wait_for_no_overlap_found_by_js][selene.core.configuration.Config.wait_for_no_overlap_found_by_js].
        """
        actions: ActionChains = ActionChains(self.config.driver)

        def fn(element: Element):
            webelement = (
                element._actual_not_overlapped_webelement
                if self.config.wait_for_no_overlap_found_by_js
                else element()
            )
            actions.context_click(webelement).perform()

        self.wait.command('context click', fn)

        return self

    # --- Commands specific to Web context --- #

    # TODO: should we reflect (or move it) in command.execute_script?
    def execute_script(self, script_on_self: str, *arguments):
        """Executes JS script on self as webelement.

        The script can use predefined parameters:
        - `element` and `self` are aliases to this element handle, i.e. `self.locate()` or `self()`.
        - `arguments` are accessible from the script with same order and indexing as they are provided to the method

        Examples:

        ```
        browser.element('[id^=google_ads]').execute_script('element.remove()')
        # OR
        browser.element('[id^=google_ads]').execute_script('self.remove()')
        '''
        # are shortcuts to
        browser.execute_script('arguments[0].remove()', browser.element('[id^=google_ads]')())
        '''
        ```

        ```
        browser.element('input').execute_script('element.value=arguments[0]', 'new value')
        # OR
        browser.element('input').execute_script('self.value=arguments[0]', 'new value')
        '''
        # are shortcuts to
        browser.execute_script('arguments[0].value=arguments[1]', browser.element('input').locate(), 'new value')
        '''
        ```
        """
        driver: WebDriver = self.config.driver
        webelement = self.locate()
        # TODO: should we wrap it in wait or not?
        # TODO: should we add additional it and/or its aliases for element?
        return driver.execute_script(
            f'''
                let element = arguments[0]
                let self = arguments[0]
                return (function(...args) {{
                    {script_on_self}
                }})(...arguments[1])
            ''',
            webelement,
            arguments,
        )

    def hover(self) -> Element:
        """Hovers over the element.

        Can be customized via
        [config.wait_for_no_overlap_found_by_js][selene.core.configuration.Config.wait_for_no_overlap_found_by_js].
        """
        actions: ActionChains = ActionChains(self.config.driver)

        def fn(element: Element):
            webelement = (
                element._actual_not_overlapped_webelement
                if self.config.wait_for_no_overlap_found_by_js
                else element()
            )
            actions.move_to_element(webelement).perform()

        self.wait.command('hover', fn)

        return self

    def press_sequentially(self, text: str) -> Element:
        """Presses each key (letter) in text sequentially to the element.

        See more at [command.press_sequentially][selene.core.command.press_sequentially].
        """

        from selene.core import command

        self.wait.for_(command.press_sequentially(text))

        return self

    # TODO: won't it be better to name it press_select_all_shortcut?
    def select_all(self) -> Element:
        """Sends «select all» keys shortcut as ctrl+a for Win/Linux
        or cmd+a for mac.

        See more at [command.select_all][selene.core.command.select_all],
        that can be also applied on a "browser" level, without specifying
        the exact element to send shortcut to.

        Has no "by_js" version so far (see [#572](https://github.com/yashaka/selene/issues/572))
        """

        from selene.core import command

        self.wait.for_(command.select_all)

        return self

    def copy(self) -> Element:
        """Sends «copy» OS-based keys shortcut.

        See more at [command.copy][selene.core.command.copy],
        that can be also applied on a "browser" level, without specifying
        the exact element to send shortcut to.

        See also ["all scenarios to work with clipboard"][clipboard-copy-and-paste-howto]
        """

        from selene.core import command

        self.wait.for_(command.copy)

        return self

    def paste(self, text: Optional[str] = None) -> Element:
        """Sends «paste» OS-based keys shortcut.

        If text argument is provided, will copy it to clipboard before sending the keys shortuct.

        See more at [command.paste][selene.core.command.paste],
        that can be also applied on a "browser" level, without specifying
        the exact element to send shortcut to.

        See also ["all scenarios to work with clipboard"][clipboard-copy-and-paste-howto]
        """

        from selene.core import command

        if text is None:
            self.wait.for_(command.paste)
        else:
            self.wait.for_(command.paste(text))

        return self

    def drag_and_drop_to(
        self, target: Element, /, *, _assert_location_changed: bool = False
    ) -> Element:
        """Drags the element to the target element.

        Can be customized via
        [config.drag_and_drop_by_js][selene.core.configuration.Config.drag_and_drop_by_js].
        Though turning the config flag on will disable the _assert_location_changed feature
        (wait for [#567](https://github.com/yashaka/selene/issues/567)).

        See more at [command.drag_and_drop_to][selene.core.command.drag_and_drop_to].
        See also [command.js.drag_and_drop_to][selene.core.command.js.drag_and_drop_to].
        """

        from selene.core import command

        if self.config.drag_and_drop_by_js:
            self.wait.for_(command.js.drag_and_drop_to(target))
        else:
            self.wait.for_(
                command.drag_and_drop_to(
                    target, _assert_location_changed=_assert_location_changed
                )
            )

        return self

    def drag_and_drop_by_offset(self, x: int, y: int) -> Element:
        """Drags the element by the offset.

        Currently, cannot be customized via
        [config.drag_and_drop_by_js][selene.core.configuration.Config.drag_and_drop_by_js]
        (wait for [#568](https://github.com/yashaka/selene/issues/568)).

        See more at [command.drag_and_drop_by_offset][selene.core.command.drag_and_drop_by_offset].
        """

        from selene.core import command

        self.wait.for_(command.drag_and_drop_by_offset(x, y))

        return self

    def drop_file(self, path: str) -> Element:
        """Simulates via JS: drops file by absolute path to the element (self).
        Usually is needed as a workaround for cases where there is no
        `input[type=file]` available to send_keys with path to the file.
        Prefer the [send_keys][selene.web._elements.Element.send_keys] method
        if possible. See also [#569](https://github.com/yashaka/selene/issues/569)

        See more at [command.js.drop_file][selene.core.command.js.drop_file].
        """

        from selene.core import command

        self.wait.for_(command.js.drop_file(path))

        return self

    def scroll_to_top(self) -> Element:
        """Simulates via JS: scrolls to an element so the top of the element
        will be aligned to the top of the visible area of the scrollable ancestor.

        See also [command.scroll_into_view][selene.core.command.js.scroll_into_view].
        """

        from selene.core import command

        self.wait.for_(
            Command(
                'scroll to top',
                command.js.scroll_into_view(block='start', inline='nearest'),
            )
        )

        return self

    def scroll_to_bottom(self) -> Element:
        """Simulates via JS: scrolls to an element so the bottom of the element will
        be aligned to the bottom of the visible area of the scrollable ancestor.

        See also [command.scroll_into_view][selene.core.command.js.scroll_into_view].
        """

        from selene.core import command

        self.wait.for_(
            Command(
                'scroll to bottom',
                command.js.scroll_into_view(block='end', inline='nearest'),
            )
        )

        return self

    def scroll_to_center(self) -> Element:
        """Simulates via JS: scrolls to an element so the center of the element will
        be aligned to the center of the scrollable ancestor.

        See also [command.scroll_into_view][selene.core.command.js.scroll_into_view].
        """

        from selene.core import command

        self.wait.for_(
            Command(
                'scroll to center',
                command.js.scroll_into_view(block='center', inline='center'),
            )
        )

        return self


# TODO: should we rename it to FrameContextManager
class _FrameContext:
    """A context manager to work with frames (iframes).
    Has an additional decorator to adapt context manager to step-methods
    when implementing a PageObject pattern.

    Partially serves as entity similar to Element
    allowing to find element or collection inside frame
    and work with them with implicit automatic "switch into context"
    before any action and "switch out" after it.
    But this ability may reduce performance in case of "too much of actions"
    inside a frame. In such cases, it's better to use explicit context manager.

    !!! note
        There is a `query.frame_context` alias to this class, because it can
        be used as "pseudo-query": `element.get(query.frame_context)`.

        This context manager is already built into `selene.web.Element` entity,
        That's why in the majority of examples below
        you will see `element.frame_context` instead of `_FrameContext(element)`
        or `element.get(_FrameContext)`.

    ## Laziness on query application

    On `element.get(query.frame_context)` (or `element.frame_context`)
    it actually just wraps an element into context manager and so is lazy,
    i.e. you can store result of such query into a variable
    even before opening a browser and use it later.
    Thus, unlike for other queries, there is no difference
    between using the query directly as `query.frame_context(element)`
    or via `get` method as `element.get(query.frame_context)`.

    The "lazy result" of the query is also a "lazy search context"
    similar to Element entity
    – it allows to find elements or collections inside the frame
    by using `self.element(selector)` or `self.all(selector)` methods.
    This allows the easiest and most implicit way to work with frames in Selene
    without bothering about switching to the frame and back:

    ### Example: Using as "search context" with fully implicit frame management

    ```python
    from selene import browser, command, have, query
    ...
    # iframe = _FrameContext(browser.element('#editor-iframe'))
    # OR:
    # iframe = query.frame_context(browser.element('#editor-iframe'))
    # OR:
    # iframe = browser.element('#editor-iframe').get(_FrameContext)
    # OR:
    # iframe = browser.element('#editor-iframe').get(query.frame_context)
    # OR:
    iframe = browser.element('#editor-iframe').frame_context
    iframe.all('strong').should(have.size(0))
    iframe.element('.textarea').type('Hello, World!').perform(command.select_all)
    browser.element('#toolbar').element('#bold').click()
    iframe.all('strong').should(have.size(1))
    ```

    !!! warning

        But be aware that such syntax will force to switch to the frame and back
        for each command executed on element or collection of elements
        inside the frame. This might result in slower tests
        if you have a lot of commands to be executed all together inside the frame.

    !!! tip

        We recommend to stay
        [YAGNI](https://enterprisecraftsmanship.com/posts/yagni-revisited/)
        and use this "frame like an element context" syntax by default,
        but when you notice performance drawbacks,
        consider choosing an explicit way to work with frame context
        as a context manager passed to `with` statement
        or as a decorator `within` applied to step-methods of PageObject
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

    ## Example: Straightforward usage of the frame context (in with statement):

    ```python
    from selene import browser, query, command, have

    toolbar = browser.element('.tox-toolbar__primary')
    text_area_frame = browser.element('.tox-edit-area__iframe')
    # the following var will only work if used after the switch to the frame ↙️
    text_area = browser.element('#tinymce')  # ❗️ inside the frame

    browser.open('https://the-internet.herokuapp.com/iframe')

    with text_area_frame.frame_context:
        text_area.perform(command.select_all)

    toolbar.element('[title=Bold]').click()

    with text_area_frame.frame_context:
        text_area.element('p').should(
            have.js_property('innerHTML').value(
                '<strong>Your content goes here.</strong>'
            )
        )
    ```

    ## Example: Usage utilizing the lazy nature of the frame context (in with statement)

    ```python
    from selene import browser, query, command, have

    toolbar = browser.element('.tox-toolbar__primary')
    text_area_frame = browser.element('.tox-edit-area__iframe')
    text_area_frame_context = text_area_frame.frame_context  # 💡↙️
    # the following var will only work if used after the switch to the frame
    text_area = browser.element('#tinymce')  # ❗️ inside the frame

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
    # text_area_frame_context = _FrameContext(text_area_frame)
    # OR:
    text_area_frame_context = query.frame_context(text_area_frame)  # 💡↙️
    # the following var will only work if used after the switch to the frame
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

    # GIVEN opened browser
    browser.open('https://the-internet.herokuapp.com/nested_frames')

    # WHEN
    with browser.element('[name=frame-top]').frame_context:
        with browser.element('[name=frame-middle]').frame_context:
            browser.element(
                '#content',
                # THEN
            ).should(have.exact_text('MIDDLE'))
        # AND
        browser.element('[name=frame-right]').should(be.visible)
    ```

    ## Example: Usage utilizing the [within][selene.web._elements._FrameContext.within] decorator for PageObjects:

    See example at [within][selene.web._elements._FrameContext.within] section.
    """

    def __init__(self, element: Element):
        self._container = element
        self.__entered = False

    def decorator(self, func):
        """A decorator to mark a function as a step within context manager

        See example of usage at [within][selene.web._elements._FrameContext.within] section.
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
    within = decorator
    """An alias to [`decorator`][selene.web._elements._FrameContext.decorator]

    Example of usage:

    ```python
    from selene import browser, command, have, query


    def teardown_function():
        browser.quit()


    class WYSIWYG:
        toolbar = browser.element('.tox-toolbar__primary')
        text_area_frame = browser.element('.tox-edit-area__iframe').frame_context  # 💡⬇️
        text_area = browser.element('#tinymce')

        def open(self):
            browser.open('https://the-internet.herokuapp.com/iframe')
            return self

        def set_bold(self):
            self.toolbar.element('[title=Bold]').click()
            return self

        @text_area_frame.within  # ⬅️
        def should_have_text_html(self, text_html):
            self.text_area.should(have.js_property('innerHTML').value(text_html))
            return self

        @text_area_frame.within  # ⬅️
        def select_all_text(self):
            self.text_area.perform(command.select_all)
            return self

        @text_area_frame.within  # ⬅️
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
        if not self.__entered:
            self._container.wait.with_(
                # resetting wait decorator to default
                # in order to avoid automatic exit applied to each command
                # including switching to the frame
                # that (automatic exit) was added after self.element
                # (this fixes breaking exiting from the frame in nested frame context)
                decorator=None,
            ).for_(
                Command(
                    'switch to frame',
                    lambda entity: entity.config.driver.switch_to.frame(
                        entity.locate()
                    ),
                )
            )
        self.__entered = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__entered:
            driver = self._container.config.driver

            # we intentionally use parent_frame() over default_content()
            # to make it work for nested frames
            # (in case of "root frames" parent_frame() should work as default_content())
            driver.switch_to.parent_frame()
            self.__entered = False

    @property
    def __as_wait_decorator(self):
        if self._container.config._wait_decorator is None:
            return support._wait.with_(context=self)

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

    def element(self, selector: str | typing.Tuple[str, str]) -> Element:
        """Allows to search for a first element by selector inside the frame context
        with implicit switching to the frame and back for each method execution.

        Is lazy, i.e. does not switch to the frame immediately on calling this method,
        and so can be stored in a variable and used later.

        Args:
            selector: css or xpath as string or classic selenium tuple-like locator,
                      e.g. `('css selector', '.some-class')`
                      or `(By.CSS_SELECTOR, '.some-class')`

        !!! warning
            By adding implicit switching to the frame and back
            for each command executed on entity, it makes the usage of such entity
            slower in case of a lot of commands to be executed
            all together inside the frame.

            It becomes especially important in case of nested frames.
            In such cases, if you use
            `entity.get(query.frame_context)` over `query.frame_context(entity)`
            or `entity.frame_context` then try to keep turned on the option:
            [config._disable_wait_decorator_on_get_query][selene.core.configuration.Config._disable_wait_decorator_on_get_query]
            That will help to avoid re-switching at least on `get` calls.

            If you notice performance drawbacks, consider choosing an explicit way
            to work with frame context as a context manager passed to `with` statement.
        """
        by = self._container.config._selector_or_by_to_by(selector)

        return Element(
            Locator(
                f'{self._container}: element({by})',
                # f'{self._container} {{ element({by}) }}',  # TODO: maybe this?
                lambda: self._container.config.driver.find_element(*by),
            ),
            self._container.config.with_(_wait_decorator=self.__as_wait_decorator),
        )

    def all(self, selector: str | typing.Tuple[str, str]) -> All[Element]:
        """Allows to search for all elements by selector inside the frame context
        with implicit switching to the frame and back for each method execution.

        Is lazy, i.e. does not switch to the frame immediately on calling this method,
        and so can be stored in a variable and used later.

        Args:
            selector: css or xpath as string or classic selenium tuple-like locator,
                      e.g. `('css selector', '.some-class')`
                      or `(By.CSS_SELECTOR, '.some-class')`

        !!! warning
            Same "potential performance drawbacks" warning is applied here
            as for [element][selene.web._elements._FrameContext.element] method.
        """
        by = self._container.config._selector_or_by_to_by(selector)

        return All(
            Locator(
                f'{self._container}: all({by})',
                lambda: self._container.config.driver.find_elements(*by),
            ),
            self._container.config.with_(_wait_decorator=self.__as_wait_decorator),
        )
