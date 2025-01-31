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

from __future__ import annotations

from typing_extensions import Optional, Union, Tuple, cast, Iterable, Sequence, Callable

from selene.common.helpers import flatten
from selene.common._typing_functions import Command
from selene.core.condition import Condition
from selene.core.configuration import Config
from selene.core.entity import WaitingEntity
from selene.core.locator import Locator
from selene.core.wait import Wait

from selenium.webdriver import ActionChains

try:
    from appium import webdriver
    from appium.webdriver import WebElement as AppiumElement
except ImportError as error:
    raise ImportError(
        'Appium-Python-Client is not installed, '
        'run `pip install Appium-Python-Client`,'
        'or add and install dependency '
        'with your favorite dependency manager like poetry: '
        '`poetry add Appium-Python-Client`'
    ) from error


class Element(WaitingEntity['Element']):
    # TODO: should we move locator based init and with_ to Located base abstract class?

    # TODO: we need a separate Config for Mobile
    #       e.g. we don't need log_outer_html_on_failure for mobile, etc.
    def __init__(self, locator: Locator[AppiumElement], config: Config):
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

    def locate(self) -> AppiumElement:
        return self._locator()

    @property
    def __raw__(self):
        return self.locate()

    def __call__(self) -> AppiumElement:
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
        return super().wait

    # @property
    # def cached(self) -> Element:
    #     # TODO: do we need caching ? with lazy save of webelement to cache
    #
    #     cache = None
    #     error = None
    #     try:
    #         cache = self.locate()
    #     except Exception as e:
    #         error = e
    #
    #     def get_webelement():
    #         if cache:
    #             return cache
    #         raise error
    #
    #     return Element(Locator(f'{self}.cached', get_webelement), self.config)

    # --- Relative location --- #

    # TODO: refactor for platform wise locators
    def element(self, selector_or_by: Union[str, Tuple[str, str]], /) -> Element:
        by = self.config._selector_or_by_to_by(selector_or_by)

        return Element(
            Locator(
                f'{self}.element({by})',
                lambda: cast(AppiumElement, self.locate().find_element(*by)),
            ),
            self.config,
        )

    def all(self, selector_or_by: Union[str, Tuple[str, str]], /) -> AllElements:
        by = self.config._selector_or_by_to_by(selector_or_by)

        return AllElements(
            Locator(
                f'{self}.all({by})',
                lambda: cast(Sequence[AppiumElement], self.locate().find_elements(*by)),
            ),
            self.config,
        )

    # --- Commands --- #

    # TODO: can we implement script on SELF for Mobile?
    # def execute_script(self, script_on_self: str, *arguments):
    #     """
    #     Executes JS script on self as webelement. Will not work for Mobile!
    #
    #     The script can use predefined parameters:
    #     - ``element`` and ``self`` are aliases to this element handle, i.e. ``self.locate()`` or ``self.locate()``.
    #     - ``arguments`` are accessible from the script with same order and indexing as they are provided to the method
    #
    #     Examples::
    #
    #         browser.element('[id^=google_ads]').execute_script('element.remove()')
    #         # OR
    #         browser.element('[id^=google_ads]').execute_script('self.remove()')
    #         '''
    #         # are shortcuts to
    #         browser.execute_script('arguments[0].remove()', browser.element('[id^=google_ads]')())
    #         '''
    #
    #         browser.element('input').execute_script('element.value=arguments[0]', 'new value')
    #         # OR
    #         browser.element('input').execute_script('self.value=arguments[0]', 'new value')
    #         '''
    #         # are shortcuts to
    #         browser.execute_script('arguments[0].value=arguments[1]', browser.element('input').locate(), 'new value')
    #         '''
    #     """
    #     driver = cast(webdriver.Remote, self.config.driver)
    #     webelement = self()
    #     # TODO: should we wrap it in wait or not?
    #     # TODO: should we add additional it and/or its aliases for element?
    #     return driver.execute_driver(
    #         script_on_self,
    #         # webelement,
    #         # arguments,
    #     )

    def set_value(self, value: Union[str, int]) -> Element:
        # TODO: should we move all commands like following or queries like in conditions - to separate py modules?
        # todo: should we make them webelement based (Callable[[MobileElement], None]) instead of element based?
        def fn(element: Element):
            mobelement = element.locate()
            mobelement.clear()
            mobelement.send_keys(str(value))

        self.wait.for_(Command(f'set value: {value}', fn))

        # todo: consider returning self.cached, since after first successful call,
        #       all next ones should normally pass
        #       no waiting will be needed normally
        #       if yes - then we should pass fn commands to wait.for_
        #       so the latter will return webelement to cache
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

    def type(self, text: Union[str, int]) -> Element:
        def fn(element: Element):
            mobelement = element.locate()
            mobelement.send_keys(str(text))

        self.wait.for_(Command(f'type: {text}', fn))

        return self

    def send_keys(self, *value) -> Element:
        """
        Similar to type(text), but with a more low-level naming & args,
        that might be useful in some cases.
        """
        # todo: here it's a bit weird... we actually needed command not query,
        #       but because of send_keys in Appium returns not None, we have to use query
        #       to ensure correct typing
        self.wait.query('send keys', lambda element: element.locate().send_keys(*value))
        return self

    def press(self, *keys) -> Element:
        """
        Similar to send_keys but with a more high level naming
        """

        def fn(element: Element):
            mobelement = element.locate()
            mobelement.send_keys(*keys)

        self.wait.command(f'press keys: {keys}', fn)

        return self

    def clear(self) -> Element:
        def fn(element: Element):
            mobelement = element.locate()
            mobelement.clear()

        self.wait.command('clear', fn)

        return self

    # TODO: consider support of percentage in offsets (in command.js.click too)
    # TODO: will this implementation of offsets work for Mobile?
    # TODO: should TAPPING be implemented in different than simple clicking way?
    # TODO: do we need a click alias? should render the name of it differently per platform?
    def tap(self, *, xoffset=0, yoffset=0) -> Element:
        """Just a normal tap action with optional offset:)"""

        def raw_click(element: Element):
            element.locate().click()

        def click_with_offset_actions(element: Element):
            actions: ActionChains = ActionChains(self.config.driver)
            mobelement = element.locate()
            actions.move_to_element_with_offset(
                mobelement, xoffset, yoffset
            ).click().perform()

        self.wait.for_(
            (
                Command('tap', raw_click)
                if (not xoffset and not yoffset)
                else Command(
                    f'tap(xoffset={xoffset},yoffset={yoffset})',
                    click_with_offset_actions,
                )
            )
        )

        return self

    def long_press(self, duration=1.0) -> Element:
        """Long press on element (also known as “touch and hold”) with duration in milliseconds.

        Args:
            duration (float): duration of the hold between press and release in seconds
        """
        from selene.core import command

        self.perform(command.long_press(duration))
        return self


# todo: wouldn't it be enough to name it as All? (currently we have All as alias to AllElements)
class AllElements(WaitingEntity['AllElements'], Iterable[Element]):
    def __init__(self, locator: Locator[Sequence[AppiumElement]], config: Config):
        self._locator = locator
        super().__init__(config)

    def with_(self, config: Optional[Config] = None, **config_as_kwargs) -> AllElements:
        return AllElements(
            self._locator,
            config if config else self.config.with_(**config_as_kwargs),
        )

    def __str__(self):
        return str(self._locator)

    def locate(self) -> Sequence[AppiumElement]:
        return self._locator()

    @property
    def __raw__(self):
        return self.locate()

    def __call__(self) -> Sequence[AppiumElement]:
        return self.locate()

    @property
    def cached(self) -> AllElements:
        mobelements = self.locate()
        return AllElements(Locator(f'{self}.cached', lambda: mobelements), self.config)

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
    def element(self, index: int, /) -> Element:
        def find() -> AppiumElement:
            mobelements = self.locate()
            length = len(mobelements)

            if length <= index:
                raise AssertionError(
                    f'Cannot get element with index {index} '
                    + f'from mobile elements collection with length {length}'
                )

            return mobelements[index]

        return Element(Locator(f'{self}[{index}]', find), self.config)

    @property
    def first(self) -> Element:
        """
        A human-readable alias to .element(0) or [0]
        """
        return cast(Element, self[0])

    @property
    def second(self) -> Element:
        """
        A human-readable alias to .element(1) or [1]
        """
        return cast(Element, self[1])

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
    ) -> AllElements:
        def find() -> Sequence[AppiumElement]:
            mobelements = self.locate()
            length = len(mobelements)
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

            return mobelements[start:stop:step]

        return AllElements(
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
    ) -> Union[Element, AllElements]:
        if isinstance(index_or_slice, slice):
            return self.sliced(
                index_or_slice.start, index_or_slice.stop, index_or_slice.step
            )

        return self.element(index_or_slice)

    def from_(self, start: int) -> AllElements:
        return cast(AllElements, self[start:])

    def to(self, stop: int) -> AllElements:
        return cast(AllElements, self[:stop])

    def by(
        self, condition: Union[Condition[Element], Callable[[Element], None]]
    ) -> AllElements:
        condition = (
            condition
            if isinstance(condition, Condition)
            else Condition(str(condition), condition)  # TODO: check here for fn name
        )

        return AllElements(
            Locator(
                f'{self}.by({condition})',
                lambda: [
                    element.locate()
                    for element in self.cached
                    if element.matching(condition)
                ],
            ),
            self.config,
        )

    def by_their(
        self,
        selector: Union[str, Tuple[str, str], Callable[[Element], Element]],
        condition: Condition[Element],
    ) -> AllElements:
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

        def find() -> AppiumElement:
            cached = self.cached

            for element in cached:
                if element.matching(condition):
                    return element.locate()

            from selene.core import query

            if self.config.log_outer_html_on_failure:
                """
                TODO: move it support.shared.config
                """
                outer_htmls = [query.outer_html(element) for element in cached]

                raise AssertionError(
                    f'\n\tCannot find element by condition «{condition}» '
                    f'\n\tAmong {self}'
                    f'\n\tActual mobelements collection:'
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
        self, finder: Callable[[Element], Union[Element, AllElements]]
    ) -> AllElements:
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

        return AllElements(
            Locator(
                f'{self}.collected({finder})',
                # TODO: consider skipping None while flattening
                lambda: cast(
                    Sequence[AppiumElement],
                    flatten([finder(element)() for element in self.cached]),
                ),
            ),
            self.config,
        )

    def all(self, selector: Union[str, Tuple[str, str]]) -> AllElements:
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

        return AllElements(
            Locator(
                f'{self}.all({by})',
                lambda: cast(
                    Sequence[AppiumElement],
                    flatten(
                        [mobelement.find_elements(*by) for mobelement in self.locate()]
                    ),
                ),
            ),
            self.config,
        )

    # todo: consider collection.all_first(number, selector) to get e.g. two first td from each tr
    def all_first(self, selector: Union[str, Tuple[str, str]]) -> AllElements:
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

        return AllElements(
            Locator(
                f'{self}.all_first({by})',
                lambda: [
                    cast(AppiumElement, mobelement.find_element(*by))
                    for mobelement in self.locate()
                ],
            ),
            self.config,
        )


All = AllElements
