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
from __future__ import annotations

import os
import typing
import warnings

from abc import abstractmethod, ABC
from typing import TypeVar, Union, Callable, Tuple, Iterable, Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.remote.webelement import WebElement

from selene.common.fp import pipe

from selene.core.configuration import Config
from selene.core.wait import Wait, Command, Query
from selene.core.condition import Condition
from selene.core.locator import Locator

from selene.common.helpers import to_by, flatten, is_absolute_url
from selene.core.exceptions import TimeoutException, _SeleneError
from selene.support.webdriver import WebHelper


E = TypeVar('E', bound='Assertable')
R = TypeVar('R')


class Assertable(ABC, typing.Generic[E]):
    @abstractmethod
    # TODO: shouldn't we type self too?
    #       see #generic-methods-and-generic-self
    #       at https://mypy.readthedocs.io/en/stable/generics.html
    # def should(self: E, condition: Condition[E]) -> E:
    def should(self, condition: Condition[E]) -> E:
        pass


# TODO: try as Matchable(ABC) and check if autocomplete will still work
class Matchable(Assertable[E]):
    @abstractmethod
    def wait_until(self, condition: Condition[E]) -> bool:
        pass

    @abstractmethod
    def matching(self, condition: Condition[E]) -> bool:
        pass


# class Configured(ABC, typing.Generic[E]):
class Configured(ABC):
    @property
    @abstractmethod
    def config(self) -> Config:
        pass

    # @abstractmethod
    # def with_(self, config: Optional[Config] = None, **config_as_kwargs) -> E:
    #     pass


class WaitingEntity(Matchable[E], Configured):
    def __init__(self, config: Config):
        self._config = config

    @property
    def wait(self) -> Wait[E]:
        return self.config.wait(typing.cast(E, self))  # type: ignore

    def perform(self, command: Command[E]) -> E:
        """Useful to call external commands.

        Commands might be predefined in Selene:
            element.perform(command.js.scroll_into_view)
        or some custom defined by selene user:
            element.perform(my_action.triple_click)

        You might think that it will be useful
        to use these methods also in Selene internally
        in order to define built in commands e.g. in Element class, like:

            def click(self):
                return self.perform(Command('click', lambda element: element().click()))

        instead of:

            def click(self):
                self.wait.for_(Command('click', lambda element: element().click()))
                return self

        But so far, we use the latter version - though, less concise, but more explicit,
        making it more obvious that waiting is built in;)

        """
        self.wait.for_(command)
        return typing.cast(E, self)

    # TODO: what about `entity[query.something]` syntax
    #       over or in addition to `entity.get(query.something)` ?
    def get(self, query: Query[E, R]) -> R:
        return self.wait.for_(query)

    # --- Configured --- #

    @property
    def config(self) -> Config:
        return self._config

    # --- Assertable --- #

    def should(self, condition: Condition[E]) -> E:
        self.wait.for_(condition)
        return typing.cast(E, self)

    # --- Matchable --- #

    def wait_until(self, condition: Condition[E]) -> bool:
        return self.wait.until(condition)

    def matching(self, condition: Condition[E]) -> bool:
        return condition.predicate(typing.cast(E, self))


class Element(WaitingEntity['Element']):
    @staticmethod
    def _log_webelement_outer_html_for(
        element: Element,
    ) -> Callable[[TimeoutException], Exception]:
        def log_webelement_outer_html(error: TimeoutException) -> Exception:
            from selene.core import query
            from selene.core.match import element_is_present

            cached = element.cached

            if cached.matching(element_is_present):
                return TimeoutException(
                    f'{error.msg}\n'
                    f'Actual webelement: {query.outer_html(element)}'  # type: ignore
                )
            else:
                return error

        return log_webelement_outer_html

    # TODO: should we move locator based init and with_ to Located base abstract class?

    def __init__(self, locator: Locator[WebElement], config: Config):
        self._locator = locator
        super().__init__(config)

    # --- Configured --- #

    def with_(self, config: Optional[Config] = None, **config_as_kwargs) -> Element:
        return Element(
            self._locator,
            config if config else self.config.with_(**config_as_kwargs),
        )

    # --- Located --- #

    def __str__(self):
        return str(self._locator)

    def locate(self) -> WebElement:
        return self._locator()

    @property
    def __raw__(self):
        return self.locate()

    def __call__(self) -> WebElement:
        return self.locate()

    # --- WaitingEntity --- #

    @property
    def wait(self) -> Wait[Element]:
        # TODO:  will not it break code like browser.with_(timeout=...)?
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

    @property
    def cached(self) -> Element:
        # TODO: do we need caching ? with lazy save of webelement to cache

        cache = None
        error = None
        try:
            cache = self()
        except Exception as e:
            error = e

        def get_webelement():
            if cache:
                return cache
            raise error

        return Element(Locator(f'{self}.cached', get_webelement), self.config)

    # --- Relative location --- #

    def element(self, css_or_xpath_or_by: Union[str, Tuple[str, str]]) -> Element:
        by = to_by(css_or_xpath_or_by)

        return Element(
            Locator(f'{self}.element({by})', lambda: self().find_element(*by)),
            self.config,
        )

    def all(self, css_or_xpath_or_by: Union[str, Tuple[str, str]]) -> Collection:
        by = to_by(css_or_xpath_or_by)

        return Collection(
            Locator(f'{self}.all({by})', lambda: self().find_elements(*by)),
            self.config,
        )

    # --- Commands --- #

    def execute_script(self, script_on_self: str, *arguments):
        """
        Executes JS script on self as webelement. Will not work for Mobile!

        The script can use predefined parameters:
        - ``element`` and ``self`` are aliases to this element handle, i.e. ``self.locate()`` or ``self()``.
        - ``arguments`` are accessible from the script with same order and indexing as they are provided to the method

        Examples::

            browser.element('[id^=google_ads]').execute_script('element.remove()')
            # OR
            browser.element('[id^=google_ads]').execute_script('self.remove()')
            '''
            # are shortcuts to
            browser.execute_script('arguments[0].remove()', browser.element('[id^=google_ads]')())
            '''

            browser.element('input').execute_script('element.value=arguments[0]', 'new value')
            # OR
            browser.element('input').execute_script('self.value=arguments[0]', 'new value')
            '''
            # are shortcuts to
            browser.execute_script('arguments[0].value=arguments[1]', browser.element('input').locate(), 'new value')
            '''
        """
        driver: WebDriver = self.config.driver
        webelement = self()
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

    # TODO: do we need this method?
    #       do we really need to wrap script into function(element,args) here?
    #       if yes... wouldn't it be better to use standard arguments name
    #       instead of args?
    #       for better integration with js support in jetbrains products?
    def _execute_script(
        self,
        script_on_self_element_and_args: str,
        *extra_args,
    ):
        warnings.warn(
            '._execute_script is now deprecated '
            'in favor of .execute_script(script_on_self, *arguments) '
            'that uses access to arguments (NOT args!) in the script',
            DeprecationWarning,
        )
        driver: WebDriver = self.config.driver
        webelement = self()
        # TODO: should we wrap it in wait or not?
        return driver.execute_script(
            f'''
                return (function(element, args) {{
                    {script_on_self_element_and_args}
                }})(arguments[0], arguments[1])
            ''',
            webelement,
            extra_args,
        )

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
        """
        To be used for more low level operations like «uploading files», etc.
        To simulate normal input of keys by user when typing
        - use Element.type(self, text).
        """
        self.wait.command('send keys', lambda element: element().send_keys(*value))
        return self

    def press(self, *keys) -> Element:
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
        def fn(element: Element):
            webelement = (
                element._actual_not_overlapped_webelement
                if self.config.wait_for_no_overlap_found_by_js
                else element()
            )
            webelement.submit()

        self.wait.command('submit', fn)

        return self

    # TODO: add offset args with defaults, or add additional method, think on what is better
    def click(self) -> Element:
        """Just a normal click:)"""

        def raw_click(element: Element):
            element.locate().click()

        from selene.core import command

        self.wait.for_(
            typing.cast(Command[Element], command.js.click)
            if self.config.click_by_js
            else Command('click', raw_click)
        )

        return self

    def double_click(self) -> Element:
        actions: ActionChains = ActionChains(self.config.driver)

        def fn(element: Element):
            webelement = (
                element._actual_not_overlapped_webelement
                if self.config.wait_for_no_overlap_found_by_js
                else element()
            )
            actions.double_click(webelement).perform()

        self.wait.command('double click', fn)

        return self

    def context_click(self) -> Element:
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

    def hover(self) -> Element:
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

    # TODO: should we reflect queries as self methods? or not...
    # pros: faster to query element attributes
    # cons: queries are not test oriented. test is steps + asserts
    #       so queries will be used only occasionally, then why to make a heap from Element?
    #       hence, occasionally it's enough to have them called as
    #           query.outer_html(element)  # non-waiting version
    #       or
    #           element.get(query.outer_html)  # waiting version
    # def outer_html(self) -> str:
    #     return self.wait.for_(query.outer_html)

    # --- Deprecate or not? --- #

    def s(self, css_or_xpath_or_by: Union[str, Tuple[str, str]]) -> Element:
        # warnings.warn(
        #     "consider using more explicit `element` instead: browser.element('#foo').element('.bar')",
        #     SyntaxWarning)
        return self.element(css_or_xpath_or_by)

    def ss(self, css_or_xpath_or_by: Union[str, Tuple[str, str]]) -> Collection:
        # warnings.warn(
        #     "consider using `all` instead: browser.element('#foo').all('.bar')",
        #     SyntaxWarning)
        return self.all(css_or_xpath_or_by)


class Collection(WaitingEntity['Collection'], Iterable[Element]):
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
        webelements = self()
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
            webelements = self()

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
            else Condition(str(condition), condition)
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
        by = to_by(selector)

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
        by = to_by(selector)

        # TODO: consider implement it through calling self.collected
        #       because actually the impl is self.collected(lambda element: element.element(selector))

        return Collection(
            Locator(
                f'{self}.all_first({by})',
                lambda: [webelement.find_element(*by) for webelement in self()],
            ),
            self.config,
        )


class Browser(WaitingEntity['Browser']):
    def __init__(self, config: Optional[Config] = None):
        config = Config() if config is None else config
        super().__init__(config)

    def with_(self, config: Optional[Config] = None, **config_as_kwargs) -> Browser:
        return (
            Browser(config)
            if config
            else Browser(self.config.with_(**config_as_kwargs))
        )

    def __str__(self):
        return 'browser'

    @property
    def driver(self) -> WebDriver:
        return self.config.driver

    # TODO: consider making it callable (self.__call__() to be shortcut to self.__raw__ ...)

    @property
    def __raw__(self):
        return self.config.driver

    # @property
    # def actions(self) -> ActionChains:
    #     """
    #     It's kind of just a shortcut for pretty low level actions from selenium webdriver
    #     Yet unsure about this property here:)
    #     comparing to usual high level Selene API...
    #     Maybe later it would be better to make own Actions with selene-style retries, etc.
    #     """
    #     return ActionChains(self.config.driver)

    # --- Element builders --- #

    # TODO: consider None by default,
    #       and *args, **kwargs to be able to pass custom things
    #       to be processed by config.location_strategy
    #       and by default process none as "element to skip all actions on it"
    def element(
        self, css_or_xpath_or_by: Union[str, Tuple[str, str], Locator]
    ) -> Element:
        if isinstance(css_or_xpath_or_by, Locator):
            return Element(css_or_xpath_or_by, self.config)

        by = to_by(css_or_xpath_or_by)

        return Element(
            Locator(f'{self}.element({by})', lambda: self.driver.find_element(*by)),
            self.config,
        )

    def all(
        self, css_or_xpath_or_by: Union[str, Tuple[str, str], Locator]
    ) -> Collection:
        if isinstance(css_or_xpath_or_by, Locator):
            return Collection(css_or_xpath_or_by, self.config)

        by = to_by(css_or_xpath_or_by)

        return Collection(
            Locator(f'{self}.all({by})', lambda: self.driver.find_elements(*by)),
            self.config,
        )

    # --- High Level Commands--- #

    def open(self, relative_or_absolute_url: Optional[str] = None) -> Browser:
        # TODO: should we keep it less pretty but more KISS? like:
        # self.config._driver_get_url_strategy(self.config)(relative_or_absolute_url)
        self.config._executor.get_url(relative_or_absolute_url)

        return self

    def switch_to_next_tab(self) -> Browser:
        from selene.core import query

        self.driver.switch_to.window(query.next_tab(self))

        # TODO: should we use waiting version here (and in other similar cases)?
        # self.perform(Command(
        #     'open next tab',
        #     lambda browser: browser.driver.switch_to.window(query.next_tab(self))))

        return self

    def switch_to_previous_tab(self) -> Browser:
        from selene.core import query

        self.driver.switch_to.window(query.previous_tab(self))
        return self

    def switch_to_tab(self, index_or_name: Union[int, str]) -> Browser:
        if isinstance(index_or_name, int):
            index = index_or_name
            from selene.core import query

            self.driver.switch_to.window(query.tab(index)(self))
        else:
            self.driver.switch_to.window(index_or_name)

        return self

    # TODO: consider deprecating
    @property
    def switch_to(self) -> SwitchTo:
        return self.driver.switch_to

    # TODO: should we add also a shortcut for self.driver.switch_to.alert ?
    #       if we don't need to switch_to.'back' after switch to alert - then for sure we should...
    #       question is - should we implement our own alert as waiting entity?

    def quit(self) -> None:
        """
        Quits the driver.

        If the driver was not even set, will build it just to quit it:D.

        Will fail if the driver was already quit or crashed.
        """
        self.driver.quit()

    # TODO: consider deprecating, it does not close browser, it closes current tab/window
    def close(self) -> Browser:
        self.driver.close()
        return self

    # --- Deprecated --- #

    # TODO: should we keep it?
    def execute_script(self, script, *args):
        warnings.warn(
            'consider using browser.driver.execute_script '
            'instead of browser.execute_script',
            PendingDeprecationWarning,
        )
        return self.driver.execute_script(script, *args)

    # TODO: should we move it to query.* and/or command.*?
    #       like `browser.get(query.screenshot)` ?
    #       like `browser.perform(command.save_screenshot)` ?
    # TODO: deprecate file name, use path
    #       because we can path folder path not file path and it will work
    def save_screenshot(self, file: Optional[str] = None):
        warnings.warn(
            'browser.save_screenshot is deprecated, '
            'use browser.get(query.screenshot_saved())',
            DeprecationWarning,
        )

        from selene.core import query  # type: ignore

        return self.get(query.screenshot_saved())  # type: ignore

    @property
    def last_screenshot(self) -> str:
        warnings.warn(
            'browser.last_screenshot is deprecated, '
            'use browser.config.last_screenshot',
            DeprecationWarning,
        )
        return self.config.last_screenshot  # type: ignore

    # TODO: consider moving this to browser command.save_page_source(filename)
    def save_page_source(self, file: Optional[str] = None) -> Optional[str]:
        warnings.warn(
            'browser.save_page_source is deprecated, '
            'use browser.config.last_screenshot',
            DeprecationWarning,
        )

        if file is None:
            file = self.config._generate_filename(suffix='.html')  # type: ignore

        saved_file = WebHelper(self.driver).save_page_source(file)

        self.config.last_page_source = saved_file  # type: ignore

        return saved_file

    @property
    def last_page_source(self) -> str:
        warnings.warn(
            'browser.last_page_source is deprecated, '
            'use browser.config.last_page_source',
            DeprecationWarning,
        )
        return self.config.last_page_source  # type: ignore

    def close_current_tab(self) -> Browser:
        warnings.warn(
            'deprecated because the «tab» term is not relevant for mobile; '
            'use a `browser.close()` or `browser.driver.close()` instead',
            DeprecationWarning,
        )
        self.driver.close()
        return self

    def clear_local_storage(self) -> Browser:
        warnings.warn(
            'deprecated because of js nature and not-relevance for mobile; '
            'use `browser.perform(command.js.clear_local_storage)` instead',
            DeprecationWarning,
        )
        from selene.core import command

        self.perform(command.js.clear_local_storage)
        return self

    def clear_session_storage(self) -> Browser:
        warnings.warn(
            'deprecated because of js nature and not-relevance for mobile; '
            'use `browser.perform(command.js.clear_session_storage)` instead',
            DeprecationWarning,
        )
        from selene.core import command

        self.perform(command.js.clear_session_storage)
        return self
