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

from typing import List, Union

from selenium.webdriver.remote.webelement import WebElement

from selene.common.helpers import as_dict, to_by, flatten
from selene import query
from selene.condition import Condition
from selene.config import Config
from selene.element import Element
from selene.entity import WaitingEntity
from selene.locator import Locator


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
            return self.sliced(slice.start, slice.stop, slice.step)

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
                    lambda: [element.element(*by) for element in self.cached]),
            self.config)


class SeleneCollection(Collection):  # todo: consider deprecating this name
    pass
