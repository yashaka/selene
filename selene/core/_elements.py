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

from typing_extensions import Iterable, Callable, Self, Optional, overload, Union, Tuple
import typing_extensions as typing

from selenium.webdriver.remote.webelement import WebElement
from typing_extensions import TypeVar


from selene.common.helpers import flatten
from selene.core._elements_context import _ElementsContext
from selene.core._entity import _CachedLocatableEntity, _WaitingConfiguredEntity
from selene.core.condition import Condition
from selene.core.configuration import Config
from selene.core.locator import Locator

# TODO: should we name it as _collection.py?
EC = TypeVar('EC', bound=_ElementsContext)


# TODO: should we extract the base class that does not depend on E bound to Element at all?
#       maybe name it as collection?
# TODO: should we make it subclass of _ElementsContext?
class All(
    _CachedLocatableEntity[typing.Sequence[WebElement]],
    _WaitingConfiguredEntity,
    Iterable[EC],
    typing.Generic[EC],
):
    def __init__(
        self,
        locator: Locator[typing.Sequence[WebElement]],
        # TODO: how good would it be to make the Config to be generic on Element? :)
        #       then we could reuse it's config.build_element_strategy:)
        #       we could use E = TypeVar('E', default=Element)
        #       so the Config without specifying type arg
        #       still work in type hints
        config: Config,
        _Element: Callable[[Locator[WebElement], Config], EC],
        **kwargs,
    ):
        super().__init__(
            locator=locator,
            config=config,
            _Element=_Element,
            **kwargs,
        )
        self._Element = _Element

    # TODO: do we really need it? consider deprecating it
    def __len__(self):
        from selene.core import query

        return self.get(query.size)

    # --- Iterable --- #

    def __iter__(self):
        i = 0
        cached = self.cached
        while i < len(cached.locate()):
            element = cached[i]
            yield element
            i += 1

    # todo: consider config.index_collection_from_1, disabled by default
    # todo: consider additional number param, that counts from 1
    #       if provided instead of index
    def element(self, index: int) -> EC:
        def find() -> WebElement:
            webelements = self.locate()
            length = len(webelements)

            if length <= index:
                raise AssertionError(
                    f'Cannot get element with index {index} '
                    + f'from webelements collection with length {length}'
                )

            return webelements[index]

        return self._Element(
            Locator(f'{self}[{index}]', find),
            self.config,
        )

    @property
    def first(self) -> EC:
        """
        A human-readable alias to .element(0) or [0]
        """
        return self[0]

    @property
    def second(self) -> EC:
        """
        A human-readable alias to .element(1) or [1]
        """
        return self[1]

    @property
    def even(self) -> Self:
        """
        A human-readable alias to [1::2], i.e. filtering collection to have only even elements
        """
        return self[1::2]

    @property
    def odd(self) -> Self:
        """
        A human-readable alias to [::2], i.e. filtering collection to have only odd elements
        """
        return self[::2]

    def sliced(
        self,
        start: Optional[int] = None,
        stop: Optional[int] = None,
        step: int = 1,
    ) -> Self:
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

        return self._build_(
            locator=Locator(
                f'{self}[{start or ""}'
                f':{stop or ""}'
                f'{":" + str(step) if step else ""}]',
                find,
            ),
            config=self.config,
            _Element=self._Element,
        )

    @overload
    def __getitem__(self, index: int) -> EC: ...
    @overload
    def __getitem__(self, slice: slice) -> Self: ...

    def __getitem__(self, index_or_slice: Union[int, slice]) -> Union[EC, Self]:
        if isinstance(index_or_slice, slice):
            return self.sliced(
                index_or_slice.start, index_or_slice.stop, index_or_slice.step
            )

        return self.element(index_or_slice)

    def from_(self, start: int) -> Self:
        return self[start:]

    def to(self, stop: int) -> Self:
        return self[:stop]

    def by(self, condition: Union[Condition[EC], Callable[[EC], None]]) -> Self:
        """Filters collection by condition, thus returning a new collection of
        only elements matching the condition."""
        condition = (
            condition
            if isinstance(condition, Condition)
            else Condition(str(condition), condition)  # TODO: check here for fn name
        )

        return self._build_(
            locator=Locator(
                f'{self}.filtered_by({condition})',
                lambda: [
                    element() for element in self.cached if element.matching(condition)
                ],
            ),
            config=self.config,
            _Element=self._Element,
        )

    def by_their(
        self,
        selector: Union[str, Tuple[str, str], Callable[[EC], EC]],
        condition: Condition[EC],
    ) -> Self:
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

        def find_in(parent: EC) -> EC:
            if callable(selector):
                return selector(parent)
            else:
                return parent.element(selector)

        return self.by(lambda it: condition(find_in(it)))

    def element_by(self, condition: Union[Condition[EC], Callable[[EC], None]]) -> EC:
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
                    return element.locate()

            # if self.config.log_outer_html_on_failure:
            #     """
            #     TODO: move it support.shared.config
            #     """
            #     outer_htmls = [query.outer_html(element) for element in cached]

            #     raise AssertionError(
            #         f'\n\tCannot find element by condition «{condition}» '
            #         f'\n\tAmong {self}'
            #         f'\n\tActual webelements collection:'
            #         f'\n\t{outer_htmls}'
            #     )  # TODO: isn't it better to print it all the time via hook, like for Element?
            # else:
            #     raise AssertionError(
            #         f'\n\tCannot find element by condition «{condition}» '
            #         f'\n\tAmong {self}'
            #     )

            raise AssertionError(
                f'\n\tCannot find element by condition «{condition}» '
                f'\n\tAmong {self}'
            )

        return self._Element(
            Locator(f'{self}.element_by({condition})', find),
            self.config,
        )

    def element_by_its(
        self,
        selector: Union[str, Tuple[str, str], Callable[[EC], EC]],
        condition: Condition[EC],
    ) -> EC:
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

        def find_in(parent: EC):
            if callable(selector):
                return selector(parent)
            else:
                return parent.element(selector)

        return self.element_by(lambda it: condition(find_in(it)))

    def collected(self, finder: Callable[[EC], Union[EC, Self]]) -> Self:
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

        return self._build_(
            locator=Locator(
                f'{self}.collected({finder})',
                # TODO: consider skipping None while flattening
                lambda: typing.cast(
                    typing.Sequence[WebElement],
                    flatten([finder(element).locate() for element in self.cached]),
                ),
            ),
            config=self.config,
            _Element=self._Element,
        )

    def all(self, selector: Union[str, Tuple[str, str]]) -> Self:
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

        return self._build_(
            locator=Locator(
                f'{self}.all({by})',
                lambda: typing.cast(
                    typing.Sequence[WebElement],
                    flatten(
                        [webelement.find_elements(*by) for webelement in self.locate()]
                    ),
                ),
            ),
            config=self.config,
            _Element=self._Element,
        )

    # todo: consider collection.all_first(number, selector) to get e.g. two first td from each tr
    def all_first(self, selector: Union[str, Tuple[str, str]]) -> Self:
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

        return self._build_(
            locator=Locator(
                f'{self}.all_first({by})',
                lambda: [webelement.find_element(*by) for webelement in self.locate()],
            ),
            config=self.config,
            _Element=self._Element,
        )
