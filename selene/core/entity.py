# MIT License
#
# Copyright (c) 2015-2020 Iakiv Kramarenko
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
from typing import TypeVar, Union, List, Dict, Any, Callable

from selenium.webdriver import ActionChains
from selenium.webdriver.android.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.remote.webelement import WebElement

from selene.core.configuration import Config
from selene.core.wait import Wait, Command, Query
from selene.core.condition import Condition
from selene.core.locator import Locator

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

    @property
    def wait(self) -> Wait[E]:
        return self.config.wait(self)

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

    # todo: what about `entity[query.something]` syntax over or in addition to `entity.get(query.something)` ?
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

    def with_(self, config: Config = None, **config_as_kwargs) -> Element:
        return Element(self._locator, self.config.with_(config, **config_as_kwargs))

    # --- Located --- #

    def __str__(self):
        return str(self._locator)

    def __call__(self) -> WebElement:
        return self._locator()

    @property
    def cached(self) -> Element:
        webelement = self()
        return Element(Locator(f'{self}.cached', lambda: webelement), self.config)

    # --- Relative location --- #

    def element(self, css_or_xpath_or_by: Union[str, tuple]) -> Element:
        by = to_by(css_or_xpath_or_by)

        return Element(
            Locator(f'{self}.element({by})',
                    lambda: self().find_element(*by)),
            self.config)

    def all(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        by = to_by(css_or_xpath_or_by)

        return Collection(
            Locator(f'{self}.all({by})',
                    lambda: self().find_elements(*by)),
            self.config)

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

        from selene.core import command
        self.wait.for_(command.js.set_value(value) if self.config.set_value_by_js
                       else Command(f'set value: {value}', fn))

        # todo: consider returning self.cached, since after first successful call,
        #       all next ones should normally pass
        #       no waiting will be needed normally
        #       if yes - then we should pass fn commands to wait.for_ so the latter will return webelement to cache
        #       also it will make sense to make this behaviour configurable...
        return self

    def type(self, text: Union[str, int]) -> Element:
        # todo: do we need a separate send_keys method?
        def fn(element: Element):
            webelement = element()
            webelement.send_keys(str(text))

        from selene.core import command
        self.wait.for_(command.js.type(text) if self.config.type_by_js
                       else Command(f'type: {text}', fn))

        return self

    def press(self, *keys) -> Element:
        self.wait.command(f'press keys: {keys}', lambda element: element().send_keys(*keys))
        return self

    def press_enter(self) -> Element:
        return self.press(Keys.ENTER)

    def press_escape(self) -> Element:
        return self.press(Keys.ESCAPE)

    def press_tab(self) -> Element:
        return self.press(Keys.TAB)

    def clear(self) -> Element:
        self.wait.command('clear', lambda element: element().clear())
        return self

    def submit(self) -> Element:
        self.wait.command('submit', lambda element: element().submit())
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

    # --- Assertable --- #

    # we need this method here in order to make autocompletion work...
    # unfortunately the "base class" version is not enough
    def should(self, condition: ElementCondition, timeout: int = None) -> Element:
        if timeout:
            warnings.warn(
                "using timeout argument is deprecated; "
                "use `browser.element('#foo').with_(Config(timeout=6)).should(be.enabled)`"
                "or just `...with_(timeout=6).should(...` style instead",
                DeprecationWarning)
            return self.with_(Config(timeout=timeout)).should(condition)

        super().should(condition)
        return self

    # --- Deprecated --- #

    def get_actual_webelement(self) -> WebElement:
        warnings.warn(
            "considering to be deprecated; use element as callable instead, like: browser.element('#foo')()",
            PendingDeprecationWarning)
        return self()

    def caching(self) -> Element:
        warnings.warn("deprecated; use `cached` property instead: browser.element('#foo').cached", DeprecationWarning)
        return self.cached

    def s(self, css_or_xpath_or_by: Union[str, tuple]) -> Element:
        # warnings.warn(
        #     "consider using more explicit `element` instead: browser.element('#foo').element('.bar')",
        #     SyntaxWarning)
        return self.element(css_or_xpath_or_by)

    def find(self, css_or_xpath_or_by: Union[str, tuple]) -> Element:
        warnings.warn(
            "deprecated; consider using `element` instead: browser.element('#foo').element('.bar')",
            DeprecationWarning)
        return self.element(css_or_xpath_or_by)

    def ss(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        # warnings.warn(
        #     "consider using `all` instead: browser.element('#foo').all('.bar')",
        #     SyntaxWarning)
        return self.all(css_or_xpath_or_by)

    def find_all(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn(
            "deprecated; consider using `all` instead: browser.element('#foo').all('.bar')",
            DeprecationWarning)
        return self.all(css_or_xpath_or_by)

    def elements(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn(
            "deprecated; consider using `all` instead: browser.element('#foo').all('.bar')",
            DeprecationWarning)
        return self.all(css_or_xpath_or_by)

    @property
    def parent_element(self):
        warnings.warn(
            "considering to deprecate because such impl makes less sens for mobile automation; "
            "consider using corresponding xpath instead if you really need it for web:"
            "browser.element('#foo').element('..')",
            PendingDeprecationWarning)
        return self.element('..')

    @property
    def following_sibling(self):
        warnings.warn(
            "considering to deprecate because such impl makes less sens for mobile automation; "
            "consider using corresponding xpath instead if you really need it for web:"
            "browser.element('#foo').element('./following-sibling::*')",
            PendingDeprecationWarning)
        return self.element('./following-sibling::*')

    @property
    def first_child(self):
        warnings.warn(
            "considering to deprecate because such impl makes less sens for mobile automation; "
            "consider using corresponding xpath instead if you really need it for web: "
            "browser.element('#foo').element('./*[1]')",
            PendingDeprecationWarning)
        return self.element('./*[1]')

    def assure(self, condition: ElementCondition, timeout=None) -> Element:
        warnings.warn(
            "deprecated; use `should` method instead: browser.element('#foo').should(be.enabled)",
            DeprecationWarning)
        return self.should(condition, timeout)

    def should_be(self, condition: ElementCondition, timeout=None) -> Element:
        warnings.warn(
            "deprecated; use `should` method with `be.*` style conditions instead: "
            "browser.element('#foo').should(be.enabled)",
            DeprecationWarning)
        return self.should(condition, timeout)

    def should_have(self, condition: ElementCondition, timeout=None) -> Element:
        warnings.warn(
            "deprecated; use `should` method with `have.*` style conditions instead: "
            "browser.element('#foo').should(have.text('bar')",
            DeprecationWarning)
        return self.should(condition, timeout)

    def should_not(self, condition: ElementCondition, timeout=None) -> Element:
        warnings.warn(
            "deprecated; use `should` method with `be.not.*` or `have.no.*` style conditions instead: "
            "`browser.element('#foo').should(be.not.enabled).should(have.no.css_class('bar')`, "
            "you also can build your own inverted conditions by: `not_ok = Condition.as_not(have.text('Ok'))`",
            DeprecationWarning)
        return self.should(condition, timeout)

    def assure_not(self, condition: ElementCondition, timeout=None) -> Element:
        warnings.warn(
            "deprecated; use `should` method with `be.not.*` or `have.no.*` style conditions instead: "
            "`browser.element('#foo').should(be.not.enabled).should(have.no.css_class('bar')`, "
            "you also can build your own inverted conditions by: `not_ok = Condition.as_not(have.text('Ok'))`",
            DeprecationWarning)
        return self.should(condition, timeout)

    def should_not_be(self, condition: ElementCondition, timeout=None) -> Element:
        warnings.warn(
            "deprecated; use `should` method with `be.not.*` or `have.no.*` style conditions instead: "
            "`browser.element('#foo').should(be.not.enabled).should(have.no.css_class('bar')`, "
            "you also can build your own inverted conditions by: `not_ok = Condition.as_not(have.text('Ok'))`",
            DeprecationWarning)
        return self.should(condition, timeout)

    def should_not_have(self, condition: ElementCondition, timeout=None) -> Element:
        warnings.warn(
            "deprecated; use `should` method with `be.not.*` or `have.no.*` style conditions instead: "
            "`browser.element('#foo').should(be.not.enabled).should(have.no.css_class('bar')`, "
            "you also can build your own inverted conditions by: `not_ok = Condition.as_not(have.text('Ok'))`",
            DeprecationWarning)
        return self.should(condition, timeout)

    def set(self, value: Union[str, int]) -> Element:
        warnings.warn(
            "deprecated; use `set_value` method instead",
            DeprecationWarning)
        return self.set_value(value)

    def scroll_to(self):
        warnings.warn(
            "deprecated; use `browser.element('#foo').perform(command.js.scroll_into_view)` style instead",
            DeprecationWarning)
        from selene.core import command
        self.perform(command.js.scroll_into_view)
        return self

    def press_down(self):
        warnings.warn(
            "deprecated; use `browser.element('#foo').type(Keys.ARROW_DOWN)` style instead",
            DeprecationWarning)
        return self.type(Keys.ARROW_DOWN)

    def find_element(self, by=By.ID, value=None):
        self.wait.command('find element', lambda element: element().find_element(by, value))
        return self

    def find_elements(self, by=By.ID, value=None):
        self.wait.command('find elements', lambda element: element().find_elements(by, value))
        return self

    def send_keys(self, *value) -> Element:
        warnings.warn(
            "send_keys is deprecated because the name is not user-oriented in context of web ui e2e tests; "
            "use `type` for 'typing text', press(*key) or press_* for 'pressing keys' methods instead",
            DeprecationWarning)
        self.wait.command('send keys', lambda element: element().send_keys(*value))
        return self

    @property
    def tag_name(self) -> str:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.tag_name)` style instead",
            DeprecationWarning)
        from selene.core import query
        return self.get(query.tag)

    @property
    def text(self) -> str:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.text)` style instead",
            DeprecationWarning)
        from selene.core import query
        return self.get(query.text)

    def attribute(self, name: str) -> str:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.attribute('name'))` style instead",
            DeprecationWarning)
        from selene.core import query
        return self.get(query.attribute(name))

    def js_property(self, name: str) -> str:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.js_property('name'))` style instead",
            DeprecationWarning)
        from selene.core import query
        return self.get(query.js_property(name))

    def value_of_css_property(self, name: str) -> str:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.css_property('name'))` style instead",
            DeprecationWarning)
        from selene.core import query
        return self.get(query.css_property(name))

    def get_attribute(self, name: str) -> str:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.attribute('name'))` style instead",
            DeprecationWarning)
        from selene.core import query
        return self.get(query.attribute(name))

    def get_property(self, name: str) -> str:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.js_property('name'))` style instead",
            DeprecationWarning)
        from selene.core import query
        return self.get(query.js_property(name))

    def is_selected(self) -> bool:
        warnings.warn(
            "deprecated; use `browser.element('#foo').matching(be.selected)` style instead",
            DeprecationWarning)
        from selene.support.conditions import be
        return self.matching(be.selected)

    def is_enabled(self):
        warnings.warn(
            "deprecated; use `browser.element('#foo').matching(be.enabled)` style instead",
            DeprecationWarning)
        from selene.support.conditions import be
        return self.matching(be.enabled)

    def is_displayed(self):
        warnings.warn(
            "deprecated; use `browser.element('#foo').matching(be.visible)` style instead",
            DeprecationWarning)
        from selene.support.conditions import be
        return self.matching(be.visible)

    @property
    def location(self) -> Dict[str, int]:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.location)` style instead",
            DeprecationWarning)
        from selene.core import query
        return self.get(query.location)

    @property
    def location_once_scrolled_into_view(self) -> Dict[str, int]:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.location_once_scrolled_into_view)` style instead",
            DeprecationWarning)
        from selene.core import query
        return self.get(query.location_once_scrolled_into_view)

    @property
    def size(self) -> Dict[str, Any]:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.size)` style instead",
            DeprecationWarning)
        from selene.core import query
        return self.get(query.size)

    @property
    def rect(self) -> Dict[str, Any]:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.rect)` style instead",
            DeprecationWarning)
        from selene.core import query
        return self.get(query.rect)

    @property
    def screenshot_as_base64(self) -> Any:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.screenshot_as_base64)` style instead",
            DeprecationWarning)
        from selene.core import query
        return self.get(query.screenshot_as_base64)

    @property
    def screenshot_as_png(self) -> Any:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.screenshot_as_base64)` style instead",
            DeprecationWarning)
        from selene.core import query
        return self.get(query.screenshot_as_png)

    def screenshot(self, filename: str) -> bool:
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.screenshot('filename'))` style instead",
            DeprecationWarning)
        from selene.core import query
        return self.get(query.screenshot(filename))

    @property
    def parent(self):
        warnings.warn(
            "deprecated; use `browser.element('#foo').config.driver` style for the majority of cases",
            DeprecationWarning)
        return self.get(Query('parent search context', lambda element: element().parent))

    @property
    def id(self):
        warnings.warn(
            "deprecated; use `browser.element('#foo').get(query.internal_id)` style instead",
            DeprecationWarning)
        from selene.core import query
        return self.get(query.internal_id)


class SeleneElement(Element):  # todo: consider deprecating this name
    pass


class Collection(WaitingEntity):
    def __init__(self, locator: Locator[List[WebElement]], config: Config):
        self._locator = locator
        super().__init__(config)

    def with_(self, config: Config = None, **config_as_kwargs) -> Collection:
        return Collection(self._locator, self.config.with_(config, **config_as_kwargs))

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

    def __len__(self):
        from selene.core import query
        return self.get(query.size)

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
        """
        in the past you used .first() was a method, now it's a property: .first
        probably when migrating to 2.* your code was broken here with an attribute error.
        just change .first() to .first everywhere in you code base;)
        """
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

    def filtered_by(self,
                   condition: Union[
                       Condition[Element],
                       Callable[[E], None]]) -> Collection:
        condition = condition if isinstance(condition, Condition) \
            else Condition(str(condition), condition)

        return Collection(
            Locator(f'{self}.filtered_by({condition})',
                    lambda: [element() for element in self.cached if element.matching(condition)]),
            self.config)

    def filtered_by_their(
            self,
            selector_or_callable: Union[str,
                                        tuple,
                                        Callable[[Element], Element]],
            condition: Condition[Element]) -> Collection:
        """
        :param selector_or_callable:
            - selector may be a str with css/xpath selector or tuple with by.* locator
            - callable should be a function on element that returns element
        :param condition: a condition to
        :return: collection subset with inner/relative element matching condition

        GIVEN html elements somewhere in DOM::
            .result
                .result-title
                .result-url
                .result-snippet

        THEN::

            browser.all('.result')\
                .filtered_by_their('.result-title', have.text('Selene'))\
                .should(have.size(3))

        ... is a shortcut for::

            browser.all('.result')\
                .filtered_by_their(lambda it: have.text(text)(it.element('.result-title')))\
                .should(have.size(3))

        OR with PageObject:

        THEN::

            results.element_by_its(lambda it: Result(it).title, have.text(text))\
                .should(have.size(3))

        Shortcut for::

            results.element_by(lambda it: have.text(text)(Result(it).title))\
                .should(have.size(3))

        WHERE::

            results = browser.all('.result')
            class Result:
                def __init__(self, element):
                    self.element = element
                    self.title = self.element.element('.result-title')
                    self.url = self.element.element('.result-url')
            # ...
        """
        warnings.warn(
            'filtered_by_their is experimental; might be renamed or removed in future',
            FutureWarning)

        def find_in(parent: Element):
            if callable(selector_or_callable):
                return selector_or_callable(parent)
            else:
                return parent.element(selector_or_callable)

        return self.filtered_by(lambda it: condition(find_in(it)))

    def element_by(self,
                   condition: Union[
                       Condition[Element],
                       Callable[[E], None]]) -> Element:
        # todo: In the implementation below...
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
        condition = condition if isinstance(condition, Condition) \
            else Condition(str(condition), condition)

        def find() -> WebElement:
            cached = self.cached

            for element in cached:
                if element.matching(condition):
                    return element()

            from selene.core import query
            outer_htmls = [query.outer_html(element) for element in cached]

            raise AssertionError(
                f'Cannot find element by condition «{condition}» ' +
                f'from webelements collection:\n[{outer_htmls}]')

        return Element(Locator(f'{self}.element_by({condition})', find), self.config)

    def element_by_its(
            self,
            selector_or_callable: Union[str,
                                        tuple,
                                        Callable[[Element], Element]],
            condition: Condition[Element]) -> Element:
        """
        :param selector_or_callable:
            - selector may be a str with css/xpath selector or tuple with by.* locator
            - callable should be a function on element that returns element
        :param condition: a condition to
        :return: element from collection that has inner/relative element matching condition

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
                .element_by(lambda it: have.text(text)(it.element('.result-title')))\
                .element('.result-url').click()

        OR with PageObject:

        THEN::

            Result(results.element_by_its(lambda it: Result(it).title, have.text(text)))\
                .url.click()

        Shortcut for::

            Result(results.element_by(lambda it: have.text(text)(Result(it).title)))\
                .url.click()

        WHERE::

            results = browser.all('.result')
            class Result:
                def __init__(self, element):
                    self.element = element
                    self.title = self.element.element('.result-title')
                    self.url = self.element.element('.result-url')
            # ...
        """
        # todo: main questions to answer before removing warning:
        #       - isn't it enough to allow Callable[[Element], bool] as condition?
        #           browser.all('.result').element_by(
        #               lambda it: it.element('.result-title').matching(have.text('browser tests in Python')))
        #               .element('.result-url').click()
        #       - how to improve error messages in case we pass lambda (not a fun with good name/str repr)?
        warnings.warn(
            'element_by_its is experimental; might be renamed or removed in future',
            FutureWarning)

        def find_in(parent: Element):
            if callable(selector_or_callable):
                return selector_or_callable(parent)
            else:
                return parent.element(selector_or_callable)

        return self.element_by(lambda it: condition(find_in(it)))

    # todo: consider adding ss alias
    def all(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn('might be renamed or deprecated in future; '
                      'all is actually a shortcut for collected(lambda element: element.all(selector)...'
                      'but we also have all_first and...'
                      'it is yet unclear what name would be best for all_first as addition to all... '
                      'all_first might confuse with all(...).first... I mean: '
                      'all_first(selector) is actually '
                      'collected(lambda e: e.element(selector)) '
                      'but it is not the same as '
                      'all(selector).first '
                      'that is collected(lambda e: e.all(selector)).first ... o_O ', FutureWarning)
        by = to_by(css_or_xpath_or_by)

        # todo: consider implement it through calling self.collected
        #       because actually the impl is self.collected(lambda element: element.all(selector))

        return Collection(
            Locator(f'{self}.all({by})',
                    lambda: flatten([webelement.find_elements(*by) for webelement in self()])),
            self.config)

    # todo: consider adding s alias
    def all_first(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn('might be renamed or deprecated in future; '
                      'it is yet unclear what name would be best... '
                      'all_first might confuse with all(...).first... I mean: '
                      'all_first(selector) is actually '
                      'collected(lambda e: e.element(selector)) '
                      'but it is not the same as '
                      'all(selector).first '
                      'that is collected(lambda e: e.all(selector)).first ... o_O ', FutureWarning)
        by = to_by(css_or_xpath_or_by)

        # todo: consider implement it through calling self.collected
        #       because actually the impl is self.collected(lambda element: element.element(selector))

        return Collection(
            Locator(f'{self}.all_first({by})',
                    lambda: [webelement.find_element(*by) for webelement in self()]),
            self.config)

    def collected(self, finder: Callable[[Element], Union[Element, Collection]]) -> Collection:
        # todo: consider adding predefined queries to be able to write
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
            Locator(f'{self}.collected({finder})',  # todo: consider skipping None while flattening
                    lambda: flatten([finder(element)() for element in self.cached])),
            self.config)

    # --- Assertable --- #

    def should(self, condition: Union[CollectionCondition, ElementCondition], timeout: int = None) -> Collection:
        if isinstance(condition, ElementCondition):
            for element in self:
                if timeout:
                    warnings.warn(
                        "using timeout argument is deprecated; "
                        "use `browser.all('.foo').with_(Config(timeout=6)).should(have.size(0))`"
                        "or just `...with_(timeout=6).should(...` style instead",
                        DeprecationWarning)
                    element.with_(Config(timeout=timeout)).should(condition)
                element.should(condition)
        else:
            if timeout:
                warnings.warn(
                    "using timeout argument is deprecated; "
                    "use `browser.all('.foo').with_(Config(timeout=6)).should(have.size(0))` "
                    "or just `...with_(timeout=6).should(...` style instead",
                    DeprecationWarning)
                self.with_(Config(timeout=timeout)).should(condition)
            super().should(condition)
        return self

    # --- Deprecated --- #

    def get_actual_webelements(self) -> List[WebElement]:
        warnings.warn(
            "considering to be deprecated; use collection as callable instead, like: browser.all('.foo')()",
            PendingDeprecationWarning)
        return self()

    def caching(self) -> Collection:
        warnings.warn("deprecated; use `cached` property instead: browser.all('#foo').cached", DeprecationWarning)
        return self.cached

    def all_by(self, condition: Condition[Element]) -> Collection:
        warnings.warn(
            "deprecated; use `filtered_by` instead: browser.all('.foo').filtered_by(be.enabled)",
            DeprecationWarning)
        return self.filtered_by(condition)

    def filter_by(self, condition: Condition[Element]) -> Collection:
        warnings.warn(
            "deprecated; use `filtered_by` instead: browser.all('.foo').filtered_by(be.enabled)",
            DeprecationWarning)
        return self.filtered_by(condition)

    def find_by(self, condition: Condition[Element]) -> Element:
        warnings.warn(
            "deprecated; use `element_by` instead: browser.all('.foo').element_by(be.enabled)",
            DeprecationWarning)
        return self.element_by(condition)

    def size(self):
        warnings.warn(
            "deprecated; use `len` standard function instead: len(browser.all('.foo'))",
            DeprecationWarning)
        return len(self)

    def should_each(self, condition: ElementCondition, timeout=None) -> Collection:
        warnings.warn(
            "deprecated; use `should` method instead: browser.all('.foo').should(have.css_class('bar'))",
            DeprecationWarning)
        return self.should(condition, timeout)

    def assure(self, condition: Union[CollectionCondition, ElementCondition], timeout=None) -> Collection:
        warnings.warn(
            "deprecated; use `should` method instead: browser.all('.foo').should(have.size(0))",
            DeprecationWarning)
        return self.should(condition, timeout)

    def should_be(self, condition: Union[CollectionCondition, ElementCondition], timeout=None) -> Collection:
        warnings.warn(
            "deprecated; use `should` method with `be.*` style conditions instead: "
            "browser.all('.foo').should(be.*)",
            DeprecationWarning)
        return self.should(condition, timeout)

    def should_have(self, condition: Union[CollectionCondition, ElementCondition], timeout=None) -> Collection:
        warnings.warn(
            "deprecated; use `should` method with `have.*` style conditions instead: "
            "browser.all('.foo').should(have.size(0))",
            DeprecationWarning)
        return self.should(condition, timeout)

    def should_not(self, condition: Union[CollectionCondition, ElementCondition], timeout=None) -> Collection:
        warnings.warn(
            "deprecated; use `should` method with `be.not.*` or `have.no.*` style conditions instead: "
            "`browser.all('.foo').should(have.no.size(2))`, "
            "you also can build your own inverted conditions by: `not_zero = Condition.as_not(have.size(0'))`",
            DeprecationWarning)
        return self.should(condition, timeout)

    def assure_not(self, condition: Union[CollectionCondition, ElementCondition], timeout=None) -> Collection:
        warnings.warn(
            "deprecated; use `should` method with `be.not.*` or `have.no.*` style conditions instead: "
            "`browser.all('.foo').should(have.no.size(2))`, "
            "you also can build your own inverted conditions by: `not_zero = Condition.as_not(have.size(0'))`",
            DeprecationWarning)
        return self.should(condition, timeout)

    def should_not_be(self, condition: Union[CollectionCondition, ElementCondition], timeout=None) -> Collection:
        warnings.warn(
            "deprecated; use `should` method with `be.not.*` or `have.no.*` style conditions instead: "
            "`browser.all('.foo').should(have.no.size(2))`, "
            "you also can build your own inverted conditions by: `not_zero = Condition.as_not(have.size(0'))`",
            DeprecationWarning)
        return self.should(condition, timeout)

    def should_not_have(self, condition: Union[CollectionCondition, ElementCondition], timeout=None) -> Collection:
        warnings.warn(
            "deprecated; use `should` method with `be.not.*` or `have.no.*` style conditions instead: "
            "`browser.element('#foo').should(have.no.size(2))`, "
            "you also can build your own inverted conditions by: `not_zero = Condition.as_not(have.size(0'))`",
            DeprecationWarning)
        return self.should(condition, timeout)


class SeleneCollection(Collection):  # todo: consider deprecating this name
    pass


class Browser(WaitingEntity):
    def __init__(self, config: Config):  # todo: what about adding **config_as_kwargs?
        super().__init__(config)

    # todo: consider implement it as context manager too...
    def with_(self, config: Config = None, **config_as_kwargs) -> Browser:
        return Browser(self.config.with_(config, **config_as_kwargs))

    def __str__(self):
        return 'browser'

    # todo: consider making it callable ...

    @property
    def driver(self) -> WebDriver:
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
        from selene.core import query
        self.driver.switch_to.window(query.next_tab(self))

        # todo: should we user waiting version here (and in other similar cases)?
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
            from selene.core import query
            self.driver.switch_to(query.tab(index_or_name)(self))
        else:
            self.driver.switch_to.window(index_or_name)

        return self

    @property
    def switch_to(self) -> SwitchTo:
        return self.driver.switch_to

    # todo: should we add also a shortcut for self.driver.switch_to.alert ?
    #       if we don't need to switch_to.'back' after switch to alert - then for sure we should...
    #       question is - should we implement our own alert as waiting entity?

    def close_current_tab(self) -> Browser:
        self.driver.close()
        return self

    def quit(self) -> None:
        self.driver.quit()

    def clear_local_storage(self) -> Browser:
        self.driver.execute_script('window.localStorage.clear();')  # todo: should we catch and ignore errors?
        return self

    def clear_session_storage(self) -> Browser:
        self.driver.execute_script('window.sessionStorage.clear();')
        return self

    # --- Assertable --- #

    # we need this method here in order to make autocompletion work...
    # unfortunately the "base class" version is not enough
    def should(self, condition: BrowserCondition) -> Browser:
        super().should(condition)
        return self

    # --- Deprecated --- #

    def close(self) -> Browser:
        warnings.warn("deprecated; use a `close_current_tab` method instead", DeprecationWarning)

        return self.close_current_tab()

    def quit_driver(self) -> None:
        warnings.warn("deprecated; use a `quit` method instead", DeprecationWarning)
        self.quit()

    @classmethod
    def wrap(cls, webdriver: WebDriver):
        warnings.warn(
            "deprecated; use a normal constructor style instead: "
            "`Browser(Config(driver=webdriver))`",
            DeprecationWarning)
        return Browser(Config(driver=webdriver))

    def s(self, css_or_xpath_or_by: Union[str, tuple]) -> Element:
        warnings.warn(
            "deprecated; use an `element` method instead: "
            "`browser.element('#foo')`",
            DeprecationWarning)

        return self.element(css_or_xpath_or_by)

    def find(self, css_or_xpath_or_by: Union[str, tuple]) -> Element:
        warnings.warn(
            "deprecated; use an `element` method instead: "
            "`browser.element('#foo')`",
            DeprecationWarning)

        return self.element(css_or_xpath_or_by)

    def ss(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn(
            "deprecated; use an `all` method instead: "
            "`browser.all('.foo')`",
            DeprecationWarning)

        return self.all(css_or_xpath_or_by)

    def find_all(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn(
            "deprecated; use an `all` method instead: "
            "`browser.all('.foo')`",
            DeprecationWarning)

        return self.all(css_or_xpath_or_by)

    def elements(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn(
            "deprecated; use an `all` method instead: "
            "`browser.all('.foo')`",
            DeprecationWarning)

        return self.all(css_or_xpath_or_by)

    def find_elements(self, by=By.ID, value=None):
        warnings.warn(
            "deprecated; use instead: `browser.driver.find_elements(...)`",
            DeprecationWarning)
        return self.driver.find_elements(by, value)

    def find_element(self, by=By.ID, value=None):
        warnings.warn(
            "deprecated; use instead: `browser.driver.find_element(...)`",
            DeprecationWarning)
        return self.driver.find_element(by, value)


from selene.core.conditions import CollectionCondition, ElementCondition, BrowserCondition


# --- Deprecated --- #  todo: remove in future versions


class SeleneDriver(Browser):
    pass
