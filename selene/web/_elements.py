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

from typing_extensions import Union, Callable, Tuple, Iterable, Optional, Self, override
import typing_extensions as typing
import warnings

from selene import support
from selene.common.fp import pipe
from selene.common.helpers import flatten
from selene.common._typing_functions import Command
from selene.core.condition import Condition
from selene.core.configuration import Config
from selene.core._elements_context import E
from selene.core._entity import _LocatableEntity, _WaitingConfiguredEntity
from selene.core.locator import Locator
from selene.core.wait import Wait

from selene.core.exceptions import TimeoutException, _SeleneError

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


@typing.runtime_checkable
class _SearchContext(typing.Protocol):
    def find_element(self, by: str, value: str | None = None) -> WebElement: ...

    def find_elements(
        self, by: str, value: str | None = None
    ) -> typing.List[WebElement]: ...


# TODO: won't it work also for Browser?
class _ElementsContext(_LocatableEntity[_SearchContext], _WaitingConfiguredEntity):
    """An Element-like class that serves as pure context for search elements inside
    via `element(selector_or_by)` or `all(selector_or_by)` methods"""

    def __init__(self, locator: Locator[_SearchContext], config: Config, **kwargs):
        super().__init__(locator=locator, config=config, **kwargs)

    def __str__(self):
        return str(self._locator)

    # --- Located-like aliases --- #

    @property
    def __raw__(self) -> _SearchContext:
        return self.locate()

    def __call__(self) -> _SearchContext:
        return self.locate()

    # --- Configured --- #

    def with_(
        self, config: Optional[Config] = None, **config_as_kwargs
    ) -> _ElementsContext:
        return _ElementsContext(
            self._locator,
            config if config else self.config.with_(**config_as_kwargs),
        )

    # --- Relative location --- #

    @property
    def cached(self) -> _ElementsContext:
        cache = None
        error = None
        try:
            cache = self.locate()
        except Exception as e:
            error = e

        def get_cache():
            if cache:
                return cache
            raise error

        return _ElementsContext(Locator(f'{self}.cached', get_cache), self.config)

    def element(self, selector_or_by: Union[str, Tuple[str, str]], /) -> Element:
        by = self.config._selector_or_by_to_by(selector_or_by)

        return Element(
            Locator(f'{self}.element({by})', lambda: self().find_element(*by)),
            self.config,
        )

    def all(self, selector_or_by: Union[str, Tuple[str, str]], /) -> Collection:
        by = self.config._selector_or_by_to_by(selector_or_by)

        return Collection(
            Locator(f'{self}.all({by})', lambda: self().find_elements(*by)),
            self.config,
        )


class Element(_LocatableEntity[WebElement], _WaitingConfiguredEntity):
    def __init__(self, locator: Locator[WebElement], config: Config, **kwargs):
        super().__init__(locator=locator, config=config, **kwargs)

    def __str__(self):
        return str(self._locator)

    # --- Located-based aliases --- #

    @property
    def __raw__(self):
        return self.locate()

    def __call__(self) -> WebElement:
        return self.locate()

    # --- Configured overrides --- #

    @override
    def with_(self, config: Optional[Config] = None, **config_as_kwargs) -> Self:
        return Element(
            self._locator,
            config if config else self.config.with_(**config_as_kwargs),
        )

    # --- WaitingEntity --- #

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

    @property
    def wait(self) -> Wait[Element]:
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

    # --- Relative location --- #

    @property
    def cached(self) -> Element:
        # TODO: do we need caching ? with lazy save of webelement to cache

        cache = None
        error = None
        try:
            cache = self.locate()
        except Exception as e:
            error = e

        def get_webelement():
            if cache:
                return cache
            raise error

        return Element(Locator(f'{self}.cached', get_webelement), self.config)

    def element(self, css_or_xpath_or_by: Union[str, Tuple[str, str]]) -> Element:
        by = self.config._selector_or_by_to_by(css_or_xpath_or_by)

        return Element(
            Locator(f'{self}.element({by})', lambda: self().find_element(*by)),
            self.config,
        )

    def all(self, css_or_xpath_or_by: Union[str, Tuple[str, str]]) -> Collection:
        by = self.config._selector_or_by_to_by(css_or_xpath_or_by)

        return Collection(
            Locator(f'{self}.all({by})', lambda: self().find_elements(*by)),
            self.config,
        )

    def s(self, css_or_xpath_or_by: Union[str, Tuple[str, str]]) -> Element:
        """A JQuery-like alias (~ $) to
        [Element.element(selector_or_by)][selene.web._elements.Element.element].
        """
        return self.element(css_or_xpath_or_by)

    def ss(self, css_or_xpath_or_by: Union[str, Tuple[str, str]]) -> Collection:
        """A JQuery-like alias (~ $$) to
        [Element.all(selector_or_by)][selene.web._elements.Element.all].
        """
        return self.all(css_or_xpath_or_by)

    @property
    def shadow_root(self) -> _ElementsContext:
        return _ElementsContext(
            Locator(f'{self}.shadow root', lambda: self.locate().shadow_root),
            self.config,
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
     
    def get_text(self) -> str:
        """Gets the text content of the element.

        See more at [query.text][selene.core.query.text].
        """

        from selene.core import query

        return self.get(query.text)
    
    def get_attribute(self, name: str) -> Optional[str]:
        """Gets the value of the specified attribute of the element.

        See more at [query.attribute][selene.core.query.attribute].
        """

        from selene.core import query

        return self.get(query.attribute(name))


# TODO: consider renaming or at list aliased to AllElements
#       for better consistency with browser.all(selector)
#       and maybe even aliased by All for nicer POM support via descriptors
class Collection(_WaitingConfiguredEntity, Iterable[Element]):
    def __init__(self, locator: Locator[typing.Sequence[WebElement]], config: Config):
        self._locator = locator
        super().__init__(config)

    def with_(self, config: Optional[Config] = None, **config_as_kwargs) -> Collection:
        return Collection(
            self._locator,
            config if config else self.config.with_(**config_as_kwargs),
        )

    def __str__(self):
        return str(self._locator)

    def locate(self) -> typing.Sequence[WebElement]:
        return self._locator()

    @property
    def __raw__(self):
        return self.locate()

    def __call__(self) -> typing.Sequence[WebElement]:
        return self.locate()

    @property
    def cached(self) -> Collection:
        webelements = self.locate()
        return Collection(Locator(f'{self}.cached', lambda: webelements), self.config)

    def __iter__(self):
        i = 0
        cached = self.cached
        while i < len(cached()):
            element = cached[i]
            yield element
            i += 1

    def __len__(self):
        from selene.core import query

        return self.get(query.size)

    # TODO: add config.index_collection_from_1, disabled by default
    # TODO: consider additional number param, that counts from 1
    #       if provided instead of index
    def element(self, index: int) -> Element:
        def find() -> WebElement:
            webelements = self.locate()
            length = len(webelements)

            if length <= index:
                raise AssertionError(
                    f'Cannot get element with index {index} '
                    + f'from webelements collection with length {length}'
                )

            return webelements[index]

        return Element(Locator(f'{self}[{index}]', find), self.config)

    @property
    def first(self) -> Element:
        """
        A human-readable alias to .element(0) or [0]
        """
        return typing.cast(Element, self[0])

    @property
    def second(self) -> Element:
        """
        A human-readable alias to .element(1) or [1]
        """
        return typing.cast(Element, self[1])

    @property
    def even(self):
        """
        A human-readable alias to [1::2], i.e. filtering collection to have only even elements
        """
        return self[1::2]

    @property
    def odd(self):
        """
        A human-readable alias to [::2], i.e. filtering collection to have only odd elements
        """
        return self[::2]

    def sliced(
        self,
        start: Optional[int] = None,
        stop: Optional[int] = None,
        step: int = 1,
    ) -> Collection:
        def find() -> typing.Sequence[WebElement]:
            webelements = self.locate()
            length = len(webelements)
            if start is not None and start != 0 and start >= length:
                raise AssertionError(
                    f'not enough elements to slice collection '
                    f'from START on index={start}, '
                    f'actual elements collection length is {length}'
                )
            if stop is not None and stop != -1 and length < stop:
                raise AssertionError(
                    'not enough elements to slice collection '
                    f'from {start or "START"} to STOP at index={stop}, '
                    f'actual elements collection length is {length}'
                )

            # TODO: assert length according to provided start, stop...

            return webelements[start:stop:step]

        return Collection(
            Locator(
                f'{self}[{start or ""}'
                f':{stop or ""}'
                f'{":" + str(step) if step else ""}]',
                find,
            ),
            self.config,
        )

    def __getitem__(
        self, index_or_slice: Union[int, slice]
    ) -> Union[Element, Collection]:
        if isinstance(index_or_slice, slice):
            return self.sliced(
                index_or_slice.start, index_or_slice.stop, index_or_slice.step
            )

        return self.element(index_or_slice)

    def from_(self, start: int) -> Collection:
        return typing.cast(Collection, self[start:])

    def to(self, stop: int) -> Collection:
        return typing.cast(Collection, self[:stop])

    def by(
        self, condition: Union[Condition[Element], Callable[[Element], None]]
    ) -> Collection:
        condition = (
            condition
            if isinstance(condition, Condition)
            else Condition(str(condition), condition)  # TODO: check here for fn name
        )

        return Collection(
            Locator(
                f'{self}.filtered_by({condition})',
                lambda: [
                    element() for element in self.cached if element.matching(condition)
                ],
            ),
            self.config,
        )

    def filtered_by(
        self, condition: Union[Condition[Element], Callable[[Element], None]]
    ) -> Collection:
        warnings.warn(
            'collection.filtered_by(condition) is deprecated in favor of collection.by(condition)',
            DeprecationWarning,
        )
        return self.by(condition)

    def by_their(
        self,
        selector: Union[str, Tuple[str, str], Callable[[Element], Element]],
        condition: Condition[Element],
    ) -> Collection:
        """
        Returns elements from collection that have inner/relative element,
        found by ``selector`` and matching ``condition``.

        Is a shortcut for ``collection.by(lambda element: condition(element.element(selector))``.

        Example (straightforward)
        -------------------------

        GIVEN html elements somewhere in DOM::
            .result
                .result-title
                .result-url
                .result-snippet

        THEN::

            browser.all('.result')\
                .by_their('.result-title', have.text('Selene'))\
                .should(have.size(3))

        is similar to::

            browser.all('.result')\
                .by_their(lambda it: have.text(text)(it.element('.result-title')))\
                .should(have.size(3))

        Example (PageObject)
        --------------------

        GIVEN html elements somewhere in DOM::
            .result
                .result-title
                .result-url
                .result-snippet

        AND::

            results = browser.all('.result')
            class Result:
                def __init__(self, element):
                    self.element = element
                    self.title = self.element.element('.result-title')
                    self.url = self.element.element('.result-url')
            # ...

        THEN::

            results.by_their(lambda it: Result(it).title, have.text(text))\
                .should(have.size(3))

        is similar to::

            results.by_their(lambda it: have.text(text)(Result(it).title))\
                .should(have.size(3))
        """

        def find_in(parent: Element) -> Element:
            if callable(selector):
                return selector(parent)
            else:
                return parent.element(selector)

        return self.by(lambda it: condition(find_in(it)))

    def element_by(
        self, condition: Union[Condition[Element], Callable[[Element], None]]
    ) -> Element:
        # TODO: a first_by(condition) alias would be shorter,
        #  and more consistent with by(condition).first
        #  but the phrase items.element_by(have.text('foo')) leads to a more
        #  natural meaning that such element should be only one...
        #  while items.first_by(have.text('foo')) gives a clue that
        #  it's just one of many...
        #  should we then make element_by fail
        #  if the condition matches more than one element? (maybe we can control it via corresponding config option?)
        #  yet we don't fail if browser.element(selector) or element.element(selector)
        #  finds more than one element... o_O

        # TODO: In the implementation below...
        #       We use condition in context of "matching", i.e. as a predicate...
        #       why then not accept Callable[[E], bool] also?
        #       (as you remember, Condition is Callable[[E], None] throwing Error)
        #       This will allow the following code be possible
        #           results.element_by(lambda it:
        #               Result(it).title.matching(have.text(text)))
        #       instead of:
        #           results.element_by(lambda it: have.text(text)(
        #                              Result(it).title))
        #       in addition to:
        #           results.element_by_its(lambda it:
        #               Result(it).title, have.text(text))
        #       Open Points:
        #       - do we need element_by_its, if we allow Callable[[E], bool] ?
        #       - if we add elements_by_its, do we need then to accept Callable[[E], bool] ?
        #       - probably... Callable[[E], bool] will lead to worse error messages,
        #         in such case we ignore thrown error's message
        #         - hm... ut seems like we nevertheless ignore it...
        #           we use element.matching(condition) below
        condition = (
            condition
            if isinstance(condition, Condition)
            else Condition(str(condition), condition)
        )

        def find() -> WebElement:
            cached = self.cached

            for element in cached:
                if element.matching(condition):
                    return element()

            from selene.core import query

            if self.config.log_outer_html_on_failure:
                """
                TODO: move it support.shared.config
                """
                outer_htmls = [query.outer_html(element) for element in cached]

                raise AssertionError(
                    f'\n\tCannot find element by condition «{condition}» '
                    f'\n\tAmong {self}'
                    f'\n\tActual webelements collection:'
                    f'\n\t{outer_htmls}'
                )  # TODO: isn't it better to print it all the time via hook, like for Element?
            else:
                raise AssertionError(
                    f'\n\tCannot find element by condition «{condition}» '
                    f'\n\tAmong {self}'
                )

        return Element(Locator(f'{self}.element_by({condition})', find), self.config)

    def element_by_its(
        self,
        selector: Union[str, Tuple[str, str], Callable[[Element], Element]],
        condition: Condition[Element],
    ) -> Element:
        """
        Returns element from collection that has inner/relative element
        found by ``selector`` and matching ``condition``.
        Is a shortcut for ``collection.element_by(lambda its: condition(its.element(selector))``.

        Example (straightforward)
        -------------------------

        GIVEN html elements somewhere in DOM::

            .result
                .result-title
                .result-url
                .result-snippet

        THEN::

            browser.all('.result')\
                .element_by_its('.result-title', have.text(text))\
                .element('.result-url').click()

        ... is a shortcut for::

            browser.all('.result')\
                .element_by(lambda its: have.text(text)(its.element('.result-title')))\
                .element('.result-url').click()

        Example (PageObject)
        --------------------

        GIVEN html elements somewhere in DOM::

            .result
                .result-title
                .result-url
                .result-snippet

        AND::

            results = browser.all('.result')
            class Result:
                def __init__(self, element):
                    self.element = element
                    self.title = self.element.element('.result-title')
                    self.url = self.element.element('.result-url')

        THEN::

            Result(results.element_by_its(lambda it: Result(it).title, have.text(text)))\
                .url.click()

        is a shortcut for::

            Result(results.element_by(lambda it: have.text(text)(Result(it).title)))\
                .url.click()
            # ...
        """

        # TODO: tune implementation to ensure error messages are ok

        def find_in(parent: Element):
            if callable(selector):
                return selector(parent)
            else:
                return parent.element(selector)

        return self.element_by(lambda it: condition(find_in(it)))

    def collected(
        self, finder: Callable[[Element], Union[Element, Collection]]
    ) -> Collection:
        # TODO: consider adding predefined queries to be able to write
        #         collected(query.element(selector))
        #       over
        #         collected(lambda element: element.element(selector))
        #       and
        #         collected(query.all(selector))
        #       over
        #         collected(lambda element: element.all(selector))
        #       consider also putting such element builders like to find.* module instead of query.* module
        #       because they are not supposed to be used in entity.get(*) context defined for other query.* fns

        return Collection(
            Locator(
                f'{self}.collected({finder})',
                # TODO: consider skipping None while flattening
                lambda: typing.cast(
                    typing.Sequence[WebElement],
                    flatten([finder(element)() for element in self.cached]),
                ),
            ),
            self.config,
        )

    def all(self, selector: Union[str, Tuple[str, str]]) -> Collection:
        """
        Returns a collection of all elements found be selector inside each element of self

        An alias to ``collection.collected(lambda its: its.all(selector))``.

        Example
        -------

        Given html::

            <table>
              <tr class="row">
                <td class="cell">A1</td><td class="cell">A2</td>
              </tr>
              <tr class="row">
                <td class="cell">B1</td><td class="cell">B2</td>
              </tr>
            </table>

        Then::

            browser.all('.row').all('.cell')).should(have.texts('A1', 'A2', 'B1', 'B2'))
        """
        by = self.config._selector_or_by_to_by(selector)

        # TODO: consider implement it through calling self.collected
        #       because actually the impl is self.collected(lambda element: element.all(selector))

        return Collection(
            Locator(
                f'{self}.all({by})',
                lambda: typing.cast(
                    typing.Sequence[WebElement],
                    flatten([webelement.find_elements(*by) for webelement in self()]),
                ),
            ),
            self.config,
        )

    # todo: consider collection.all_first(number, selector) to get e.g. two first td from each tr
    def all_first(self, selector: Union[str, Tuple[str, str]]) -> Collection:
        """
        Returns a collection of each first element found be selector inside each element of self

        An alias to ``collection.collected(lambda its: its.element(selector))``.
        Not same as ``collection.all(selector).first`` that is same as ``collection.first.element(selector)``

        Example
        -------

        Given html::

            <table>
              <tr class="row">
                <td class="cell">A1</td><td class="cell">A2</td>
              </tr>
              <tr class="row">
                <td class="cell">B1</td><td class="cell">B2</td>
              </tr>
            </table>

        Then::

            browser.all('.row').all_first('.cell')).should(have.texts('A1', 'B1'))
        """
        by = self.config._selector_or_by_to_by(selector)

        # TODO: consider implement it through calling self.collected
        #       because actually the impl is self.collected(lambda element: element.element(selector))

        return Collection(
            Locator(
                f'{self}.all_first({by})',
                lambda: [webelement.find_element(*by) for webelement in self()],
            ),
            self.config,
        )

    # --- Unique for Web --- #

    @property
    def shadow_roots(self) -> Collection:

        # TODO: should not we return Collection of _SearchContexts instead of Collection of WebElements?
        return Collection(
            Locator(
                f'{self}.shadow roots',
                lambda: [webelement.shadow_root for webelement in self.locate()],
            ),
            self.config,
        )


AllElements = Collection

All = Collection


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

    def all(self, selector: str | typing.Tuple[str, str]) -> Collection:
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

        return Collection(
            Locator(
                f'{self._container}: all({by})',
                lambda: self._container.config.driver.find_elements(*by),
            ),
            self._container.config.with_(_wait_decorator=self.__as_wait_decorator),
        )
