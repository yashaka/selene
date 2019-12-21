# MIT License
#
# Copyright (c) 2015-2019 Iakiv Kramarenko
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

import warnings

from abc import abstractmethod, ABC
from typing import TypeVar, Union, List

from selenium.webdriver import ActionChains
from selenium.webdriver.android.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.remote.webelement import WebElement

from selene.config import Config
from selene.wait import Wait, Command, Query
from selene.condition import Condition
from selene.locator import Locator

from selene.common.helpers import to_by, flatten, is_absolute_url

E = TypeVar('E', bound='Assertable')
R = TypeVar('R')


class Assertable(ABC):
    @abstractmethod
    def should(self, condition: Condition[E]) -> E:
        pass


# todo: try as Matchable(ABC) and check if autocomplete will still work
class Matchable(Assertable):
    @abstractmethod
    def wait_until(self, condition: Condition[E]) -> bool:
        pass

    @abstractmethod
    def matching(self, condition: Condition[E]) -> bool:
        pass


class Configured(ABC):
    @property
    @abstractmethod
    def config(self) -> Config:
        pass


class WaitingEntity(Matchable, Configured):

    def __init__(self, config: Config):
        self._config = config
        self._wait = Wait(self,
                          at_most=config.timeout,
                          or_fail_with=config.hooks.wait.failure)

    @property
    def wait(self) -> Wait[E]:
        return self._wait

    def perform(self, command: Command[E]) -> E:
        """Useful to call external commands.

        Commands might be predefined in Selene:
            element.perform(command.js.scroll_into_view)
        or some custom defined by selene user:
            element.perform(my_action.triple_click)

        You might think that it will be usefull to use these methods also in Selene internally
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
        return self

    def get(self, query: Query[E, R]) -> R:
        return self.wait.for_(query)

    # --- Configured --- #

    @property
    def config(self) -> Config:
        return self._config

    # --- Assertable --- #

    def should(self, condition: Condition[E]) -> E:
        self.wait.for_(condition)
        return self

    # --- Matchable --- #

    def wait_until(self, condition: Condition[E]) -> bool:
        return self.wait.until(condition)

    def matching(self, condition: Condition[E]) -> bool:
        return condition.predicate(self)


class Element(WaitingEntity):

    # todo: should we move locator based init and with_ to Located base abstract class?

    def __init__(self, locator: Locator[WebElement], config: Config):
        self._locator = locator
        super().__init__(config)

    # --- Configured --- #

    def with_(self, config: Config) -> Element:
        return Element(self._locator, self.config.with_(config))

    # --- Located --- #

    def __str__(self):
        return str(self._locator)

    def __call__(self) -> WebElement:
        return self._locator()

    # --- Relative location --- #

    def element(self, css_or_xpath_or_by: Union[str, tuple]) -> Element:
        by = to_by(css_or_xpath_or_by)

        return Element(
            Locator(f'{self}.element({by})',
                    lambda: self().find_element(*by)),
            self.config)

    def s(self, css_or_xpath_or_by: Union[str, tuple]) -> Element:
        warnings.warn('deprecated; use browser.element(...).element(...) instead', DeprecationWarning)
        return self.element(css_or_xpath_or_by)

    def all(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        by = to_by(css_or_xpath_or_by)

        return Collection(
            Locator(f'{self}.all({by})',
                    lambda: self().find_elements(*by)),
            self.config)

    def ss(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn('deprecated; use browser.element(...).all(...) instead', DeprecationWarning)
        return self.all(css_or_xpath_or_by)

    # --- Commands --- #

    def execute_script(self, script_on_self: str, *extra_args):
        driver: WebDriver = self.config.driver
        webelement = self()
        # todo: should we wrap it in wait or not?
        return driver.execute_script(script_on_self, webelement, *extra_args)

    def set_value(self, value: Union[str, int]) -> Element:
        # todo: should we move all commands like following or queries like in conditions - to separate py modules?
        # todo: should we make them webelement based (Callable[[WebElement], None]) instead of element based?
        def fn(element: Element):
            webelement = element()
            webelement.clear()  # todo: change to impl based not on clear, because clear generates post-events...
            webelement.send_keys(str(value))

        from selene import command
        self.wait.for_(command.js.set_value(value) if self.config.set_value_by_js
                       else Command(f'set value: {value}', fn))

        return self

    def type(self, keys: Union[str, int]) -> Element:
        def fn(element: Element):
            webelement = element()
            webelement.send_keys(str(keys))

        from selene import command
        self.wait.for_(command.js.type(keys) if self.config.type_by_js
                          else Command(f'type: {keys}', fn))

        return self

    def press_enter(self) -> Element:
        return self.type(Keys.ENTER)

    def press_escape(self) -> Element:
        return self.type(Keys.ESCAPE)

    def press_tab(self) -> Element:
        return self.type(Keys.TAB)

    def clear(self) -> Element:
        self.wait.command('clear', lambda element: element().clear())
        return self

    # todo: do we need config.click_by_js?
    # todo: add offset args with defaults, or add additional method, think on what is better
    def click(self) -> Element:
        """Just a normal click:)

        You might ask, why don't we have config.click_by_js?
        Because making all clicks js based is not a "normal case".
        You might need to speed up all "set value" in your tests, but command.js.click will not speed up anything.
        Yet, sometimes, it might be useful as workaround.
        In such cases - use

            element.perform(command.js.click)

        to achieve the goal in less concise way,
        thus, identifying by this "awkwardness" that it is really a workaround;)
        """
        self.wait.command('click', lambda element: element().click())
        return self

    def double_click(self) -> Element:
        actions: ActionChains = ActionChains(self.config.driver)
        self.wait.command('double click', lambda element: actions.double_click(element()).perform())
        return self

    def context_click(self) -> Element:
        actions: ActionChains = ActionChains(self.config.driver)
        self.wait.command('context click', lambda element: actions.context_click(element()).perform())
        return self

    def hover(self) -> Element:
        actions: ActionChains = ActionChains(self.config.driver)
        self.wait.command('hover', lambda element: actions.move_to_element(element()).perform())
        return self

    # todo: should we reflect queries as self methods? or not...
    # pros: faster to query element attributes
    # cons: queries are not test oriented. test is steps + asserts
    #       so queries will be used only occasionally, then why to make a heap from Element?
    #       hence, occasionally it's enough to have them called as
    #           query.outer_html(element)  # non-waiting version
    #       or
    #           element.get(query.outer_html)  # waiting version
    # def outer_html(self) -> str:
    #     return self.wait.for_(query.outer_html)


class SeleneElement(Element):  # todo: consider deprecating this name
    pass


class Collection(WaitingEntity):
    def __init__(self, locator: Locator[List[WebElement]], config: Config):
        self._locator = locator
        super().__init__(config)

    def with_(self, config: Config) -> Collection:
        return Collection(self._locator, self.config.with_(config))

    def __str__(self):
        return str(self._locator)

    def __call__(self) -> List[WebElement]:
        return self._locator()

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

    # todo: add config.index_collection_from_1, disabled by default
    def element(self, index: int) -> Element:
        def find() -> WebElement:
            webelements = self()
            length = len(webelements)

            if length <= index:
                raise AssertionError(
                    f'Cannot get element with index {index} ' +
                    f'from webelements collection with length {length}')

            return webelements[index]

        return Element(Locator(f'{self}[{index}]', find), self.config)

    @property
    def first(self):
        return self.element(0)

    def sliced(self, start: int, stop: int, step: int = 1) -> Collection:
        def find() -> List[WebElement]:
            webelements = self()

            # todo: assert length according to provided start, stop...

            return webelements[start:stop:step]

        return Collection(Locator(f'{self}[{start}:{stop}:{step}]', find), self.config)

    def __getitem__(self, index_or_slice: Union[int, slice]) -> Union[Element, Collection]:
        if isinstance(index_or_slice, slice):
            return self.sliced(index_or_slice.start, index_or_slice.stop, index_or_slice.step)

        return self.element(index_or_slice)

    def from_(self, start: int) -> Collection:
        return self[start:]

    def to(self, stop: int) -> Collection:
        return self[:stop]

    def filtered_by(self, condition: Condition[Element]) -> Collection:
        return Collection(
            Locator(f'{self}.filtered_by({condition})',
                    lambda: [element() for element in self.cached if element.matching(condition)]),
            self.config)

    def element_by(self, condition: Condition[Element]) -> Element:
        def find() -> WebElement:
            cached = self.cached

            for element in cached:
                if element.matching(condition):
                    return element()

            from selene import query
            outer_htmls = [query.outer_html(element) for element in cached]

            raise AssertionError(
                f'Cannot find element by condition «{condition}» ' +
                f'from webelements collection:\n[{outer_htmls}]')

        return Element(Locator(f'{self}.element_by({condition})', find), self.config)

    def all(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        by = to_by(css_or_xpath_or_by)

        return Collection(
            Locator(f'{self}.all({by})',
                    lambda: flatten([webelement.find_elements(*by) for webelement in self()])),
            self.config)

    def map(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        by = to_by(css_or_xpath_or_by)

        return Collection(
            Locator(f'{self}.map({by})',
                    lambda: [element.element(*by)() for element in self.cached]),
            self.config)

    # --- Assertable --- #

    def should(self, condition: Union[CollectionCondition, ElementCondition]) -> Collection:
        if isinstance(condition, ElementCondition):
            for element in self:
                element.should(condition)
        else:
            super().should(condition)
        return self


class SeleneCollection(Collection):  # todo: consider deprecating this name
    pass


class Browser(WaitingEntity):
    def __init__(self, config: Config):
        super().__init__(config)

    # todo: consider implement it as context manager too...
    def with_(self, config: Config) -> Browser:
        return Browser(self.config.with_(config))

    def __str__(self):
        return 'browser'

    @property
    def driver(self) -> WebDriver:
        return self.config.driver

    # --- Element builders --- #

    def element(self, css_or_xpath_or_by: Union[str, tuple]) -> Element:
        by = to_by(css_or_xpath_or_by)

        return Element(
            Locator(f'{self}.element({by})',
                    lambda: self.driver.find_element(*by)),
            self.config)

    def all(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        by = to_by(css_or_xpath_or_by)

        return Collection(
            Locator(f'{self}.all({by})',
                    lambda: self.driver.find_elements(*by)),
            self.config)

    # --- High Level Commands--- #

    def open(self, relative_or_absolute_url: str) -> Browser:
        width = self.config.window_width
        height = self.config.window_height

        if width and height:
            self.driver.set_window_size(int(width), int(height))

        is_absolute = is_absolute_url(relative_or_absolute_url)
        base_url = self.config.base_url
        url = relative_or_absolute_url if is_absolute else base_url + relative_or_absolute_url

        self.driver.get(url)
        return self

    def switch_to_next_tab(self) -> Browser:
        from selene import query
        self.driver.switch_to.window(query.next_tab(self))

        # todo: should we user waiting version here (and in other similar cases)?
        # self.perform(Command(
        #     'open next tab',
        #     lambda browser: browser.driver.switch_to.window(query.next_tab(self))))

        return self

    def switch_to_previous_tab(self) -> Browser:
        from selene import query
        self.driver.switch_to.window(query.previous_tab(self))
        return self

    def switch_to_tab(self, index_or_name: Union[int, str]) -> Browser:
        if isinstance(index_or_name, int):
            from selene import query
            self.driver.switch_to(query.tab(index_or_name)(self))
        else:
            self.driver.switch_to.window(index_or_name)

        return self

    @property
    def switch_to(self) -> SwitchTo:
        return self.driver.switch_to.alert

    # todo: should we add also a shortcut for self.driver.switch_to.alert ?
    #       if we don't need to switch_to.'back' after switch to alert - then for sure we should...
    #       question is - should we implement our own alert as waiting entity?

    def close_current_tab(self) -> Browser:
        self.driver.close()
        return self

    def quit(self) -> None:
        self.driver.quit()

    def clear_local_storage(self) -> Browser:
        self.driver.execute_script('window.localStorage.clear();') # todo: should we catch and ignore errors?
        return self

    def clear_session_storage(self) -> Browser:
        self.driver.execute_script('window.sessionStorage.clear();')
        return self


# --- Deprecated --- #  todo: remove in future versions


class SeleneDriver(Browser):
    pass


from selene.conditions import CollectionCondition, ElementCondition
