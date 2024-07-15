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

import re
import warnings
from functools import reduce

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from typing_extensions import (
    List,
    Any,
    Union,
    Iterable,
    Tuple,
    Literal,
    Dict,
    override,
    Callable,
    Self,
    Type,
    cast,
    Optional,
    TypeVar,
)

from selene.common import predicate, helpers, appium_tools
from selene.common._typing_functions import Query
from selene.core import query
from selene.core.condition import Condition, Match
from selene.core.conditions import (
    ElementCondition,
    CollectionCondition,
    BrowserCondition,
)
from selene.core.entity import Collection, Element, Configured
from selene.core._browser import Browser


# GENERAL CONDITION BUILDERS ------------------------------------------------- #
E = TypeVar('E', bound=Configured)


class _EntityHasSomethingSupportingIgnoreCase(Match[E]):
    def __init__(
        self,
        name,
        /,
        expected,
        actual,
        by,
        _ignore_case=False,
        _inverted=False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ):
        self.__name = name
        self.__actual = actual
        self.__expected = expected
        self.__by = by
        self.__ignore_case = _ignore_case
        self.__inverted = _inverted
        self.__falsy_exceptions = _falsy_exceptions

        super().__init__(
            lambda maybe_entity: (
                name
                + (
                    ' ignoring case:'
                    if (maybe_entity is not None and maybe_entity.config._ignore_case)
                    or _ignore_case
                    else ''
                )
                + f' \'{expected}\''
                # todo: refactor to and change tests correspondingly:
                # f'{" ignoring case:" if _ignore_case else ":"} «{expected}»'
            ),
            actual=lambda entity: (entity, actual(entity)),
            by=lambda entity_and_actual: (
                by(str(expected).lower())(str(actual).lower())
                if (
                    entity_and_actual[0],
                    actual := entity_and_actual[1],
                )[0].config._ignore_case
                or _ignore_case
                else by(str(expected))(str(actual))
            ),
            _describe_actual_result=lambda entity_and_actual: (
                Query._full_description_or(
                    'actual', for_=actual, _with_prefix='actual '
                )
                + f': {entity_and_actual[1]}'
            ),
            _inverted=_inverted,
            _falsy_exceptions=_falsy_exceptions,
        )

    # TODO: should we add property pattern or with_regex (compare with *_like conditions)
    #       similar to ignore_case, that adds regex support to condition?

    @property
    def ignore_case(self) -> Condition[E]:
        return self.__class__(
            self.__name,
            self.__expected,
            self.__actual,
            self.__by,
            _ignore_case=True,
            _inverted=self.__inverted,
            _falsy_exceptions=self.__falsy_exceptions,
        )


class _CollectionHasSomeThingsSupportingIgnoreCase(Match[Collection]):
    def __init__(
        self,
        name,
        /,
        *expected: str | int | float | Iterable[str],
        actual,
        by,
        _ignore_case=False,
        _inverted=False,
        _falsy_exceptions: Iterable[Type[Exception]] = (AssertionError,),
    ):
        self.__name = name
        self.__actual = actual
        self.__expected = expected
        self.__by = by
        self.__ignore_case = _ignore_case
        self.__inverted = _inverted
        self.__falsy_exceptions = _falsy_exceptions

        # todo: should we store flattened version in self?
        #       how should we render nested expected in error?
        #       should we transform actual to same un-flattened structure as expected?
        #       (when rendering, of course)

        def compare(entity_and_actual: Tuple[Collection, Iterable]) -> bool:
            entity, actual = entity_and_actual
            expected_flattened = helpers.flatten(expected)
            str_lower = lambda some: str(some).lower()
            return (
                by(map(str_lower, expected_flattened))(map(str_lower, actual))
                if entity.config._ignore_case or _ignore_case
                else by(map(str, expected_flattened))(map(str, actual))
            )

        super().__init__(
            lambda maybe_entity: (
                name
                + (
                    ' ignoring case:'
                    if (maybe_entity is not None and maybe_entity.config._ignore_case)
                    or _ignore_case
                    else ''
                )
                + f' {list(expected)}'
            ),
            actual=lambda entity: (entity, actual(entity)),
            by=compare,
            _describe_actual_result=lambda entity_and_actual: (
                Query._full_description_or(
                    'actual', for_=actual, _with_prefix='actual '
                )
                + f': {entity_and_actual[1]}'
            ),
            _inverted=_inverted,
            _falsy_exceptions=_falsy_exceptions,
        )

    @property
    def ignore_case(self) -> Condition[Collection]:
        return self.__class__(
            self.__name,
            *self.__expected,
            actual=self.__actual,
            by=self.__by,
            _ignore_case=True,
            _inverted=self.__inverted,
            _falsy_exceptions=self.__falsy_exceptions,
        )


# CONDITIONS ----------------------------------------------------------------- #

present_in_dom: Condition[Element] = Match(
    'is present in DOM',
    actual=lambda element: element.locate(),
    by=lambda webelement: webelement is not None,
    _describe_actual_result=lambda webelement: (
        f'actual html element: {webelement.get_attribute("outerHTML")}'
        if not appium_tools._is_mobile_element(webelement)
        else str(webelement)  # todo: find out what best to log for mobile
    ),
    _falsy_exceptions=(NoSuchElementException,),
)

# todo: consider refactoring so it would be similar to present_in_dom
#       in context of details in error message, by utilizing _describe_actual_result
absent_in_dom: Condition[Element] = Condition.as_not(present_in_dom, 'is absent in DOM')


def __deprecated_is_present(element: Element) -> bool:
    warnings.warn(
        'be.present is deprecated, use be.present_in_dom instead',
        DeprecationWarning,
    )
    return element.locate() is not None


present: Condition[Element] = Match(
    'is present in DOM',
    by=__deprecated_is_present,  # noqa
    _falsy_exceptions=(NoSuchElementException,),
)
"""Deprecated 'is present' condition. Use present_in_dom instead. """


absent: Condition[Element] = Condition.as_not(present, 'is absent in DOM')
"""Deprecated 'is absent' condition. Use absent_in_dom instead."""


def __deprecated_is_existing(element: Element) -> bool:
    warnings.warn(
        'be.existing is deprecated, use be.present_in_dom instead',
        DeprecationWarning,
    )
    return element.locate() is not None


existing: Condition[Element] = Match(
    'is present in DOM',
    by=__deprecated_is_existing,  # noqa
    _falsy_exceptions=(NoSuchElementException,),
)
"""Deprecated 'is existing' condition. Use present_in_dom instead."""

visible: Condition[Element] = Match(
    'is visible',
    actual=lambda element: element.locate(),
    by=lambda actual: actual.is_displayed(),
    _describe_actual_result=lambda actual: (
        f'actual html element: {actual.get_attribute("outerHTML")}'
        if not appium_tools._is_mobile_element(actual)
        else str(actual)  # todo: find out what best to log for mobile
    ),
    _falsy_exceptions=(NoSuchElementException,),
)

# todo: remove once decide on the best implementation
#       and at least documented in docs this version
__visible_with_actual_as_tuple: Condition[Element] = Match(
    'is visible',
    actual=lambda element: (
        webelement := element.locate(),
        webelement.get_attribute('outerHTML'),
    ),
    by=lambda actual_element_and_outer_html: (
        actual_element_and_outer_html[0].is_displayed()
    ),
)
"""Alternative and disabled via protection prefix version of visible condition,
that will result in good error like:
    actual: (<selenium.webdriver.remote.webelement.WebElement
    (session="...", element="...")>,
    '<button id="hidden" style="display: none">Press me</button>')

– but is slower, because of two calls to webdriver on actual
"""

hidden: Condition[Element] = Condition.as_not(visible, 'is hidden')

hidden_in_dom: Condition[Element] = present_in_dom.and_(visible.not_)


enabled: Condition[Element] = Match(
    'is enabled',
    by=lambda element: element.locate().is_enabled(),
)

# disabled: Condition[Element] = Condition.as_not(enabled, 'disabled')
disabled: Condition[Element] = enabled.not_

clickable: Condition[Element] = visible.and_(enabled)


selected: Condition[Element] = Match(
    'is selected',
    by=lambda element: element.locate().is_selected(),
)


class js:
    # todo: how will it work for mobile? – it will not work:)
    #       do we even need it? – inside js class? or maybe be multiplatform?
    _active_element: Condition[Element] = Match(
        'has focus',
        by=lambda element: (
            element.locate()
            == element.config.driver.execute_script('return document.activeElement')
        ),
    )


# todo: consider removing once moved to docs
class __x_ElementHasText(Condition[Element]):
    """Just an example of a custom condition builder
    based on inheritance from Condition[Element]
    """

    def __init__(
        self,
        expected: str | int | float,
        _describing_matched_to='has text',
        _compared_by_predicate_to=predicate.includes,
        _ignore_case=False,
        _inverted=False,
    ):
        self.__expected = expected
        self.__describe_matched_to = _describing_matched_to
        self.__compared_by_predicate_to = _compared_by_predicate_to
        self.__ignore_case = _ignore_case
        self.__inverted = _inverted

        super().__init__(
            (
                f'{_describing_matched_to}'
                f'{" ignoring case:" if _ignore_case else ""} {expected}'
                # todo: refactor to and change tests correspondingly:
                # f'{" ignoring case:" if _ignore_case else ":"} {expected}'
            ),
            actual=query.text,
            by=lambda actual: (
                _compared_by_predicate_to(str(expected).lower())(str(actual).lower())
                if _ignore_case
                else _compared_by_predicate_to(str(expected))(str(actual))
            ),
            _inverted=_inverted,
        )

    # returning Conditioin[Element] to not allow .ignore_case.ignore_case usage:)
    @property
    def ignore_case(self) -> Condition[Element]:
        return self.__class__(
            self.__expected,
            self.__describe_matched_to,
            self.__compared_by_predicate_to,
            _ignore_case=True,
            _inverted=self.__inverted,
        )


def __x_text(expected: str | int | float, _ignore_case=False, _inverted=False):
    return __x_ElementHasText(
        expected, 'has text', predicate.includes, _ignore_case, _inverted=_inverted
    )


def __x_exact_text(expected: str | int | float, _ignore_case=False, _inverted=False):
    return __x_ElementHasText(
        expected, 'has exact text', predicate.equals, _ignore_case, _inverted=_inverted
    )


# todo: is text + exact_text naming still relevant for match.* case over have.*?
#       let's compare examples:
#       > element.should(have.exact_text('full of partial!'))   # 👍🏻
#       > element.should(have.text('partial'))                  # 👍🏻
#       > element.should(match.exact_text('full of partial!'))  # 👍🏻
#       > element.should(match.text('part'))                    # 🤨
#       > element.should(match.text_containing('part'))         # 🤔
#       > element.should(match.partial_text('part'))            # 👍🏻
#       > match.text('part')(element)                           # 🤨
#       > match.text_containing('part')(element)                # ??
#       > match.partial_text('part')(element)                   # 👍🏻
#       let's see other conditions
#       > element.should(have.value('full of partial!'))        # 👍🏻
#       > element.should(have.value_containing('part'))         # 👍🏻
#       > element.should(match.value('full of partial!'))       # 👍🏻
#       > element.should(match.value_containing('part'))        # 👍🏻
#       > element.should(match.partial_value('part'))           # 👍🏻?
#       > browser.should(match.url_containing('part'))          # 👍🏻
#       > browser.should(match.partial_url('part'))             # 👍🏻?
#       > match.url_containing('part')(browser)                 # 👍🏻
#       > match.partial_url('part')(browser)                    # 👍🏻?
#       Hm... There is something weird in "match.partial_*('part')" ...
#       it's conciser but less consistent with have.*_containing
#       and maybe it's subjective, but partial_ phrasing sounds
#       less natural for me... from human-language perspective
#       Hence, let's keep things simple and consistent.
#       match.text is really a problem. Not others.
#       So let's rename only it and rename only to the most consistent
#       with other versions... i.e. to text_containing
#       Let's not do anything else. For example,
#       we could rename match.exact_text to match.text, but again,
#       let's keep consistency with have.* as much as possible
def text_containing(expected: str | int | float, _ignore_case=False, _inverted=False):
    return _EntityHasSomethingSupportingIgnoreCase(
        'has text',  # TODO: is it here name or description? probably it's even a "name prefix"
        expected,
        actual=query.text,
        by=predicate.includes,
        _ignore_case=_ignore_case,
        _inverted=_inverted,
    )


def exact_text(expected: str | int | float, _ignore_case=False, _inverted=False):
    return _EntityHasSomethingSupportingIgnoreCase(
        'has exact text',
        expected,
        actual=query.text,
        by=predicate.equals,
        _ignore_case=_ignore_case,
        _inverted=_inverted,
    )


class text_pattern(Condition[Element]):

    def __init__(self, expected: str, _flags=0, _inverted=False):
        self.__expected = expected
        self.__flags = _flags
        self.__inverted = _inverted

        super().__init__(
            lambda maybe_entity: (
                f'has text matching'
                + (
                    f' (with flags {flags}):'
                    if (
                        flags := (
                            _flags | re.IGNORECASE
                            if maybe_entity is not None
                            and maybe_entity.config._ignore_case
                            else _flags
                        )
                    )
                    else ''
                )
                + f' {expected}'
            ),
            actual=lambda entity: (entity, query.text(entity)),
            by=lambda entity_and_actual: predicate.matches(
                expected,
                (
                    _flags | re.IGNORECASE
                    if entity_and_actual[0] is not None
                    and entity_and_actual[0].config._ignore_case
                    else _flags
                ),
            )(entity_and_actual[1]),
            _describe_actual_result=lambda entity_and_actual: (
                f'actual text: {entity_and_actual[1]}'
            ),
            _inverted=_inverted,
        )

    @property
    def ignore_case(self):
        return self.where_flags(re.IGNORECASE)

    # todo: should we shorten name just to flags? (or add alias) i.e.
    #       `.should(have.text_matching(r'.*one.*').flags(re.IGNORECASE))`
    #       over
    #       `.should(have.text_matching(r'.*one.*').where_flags(re.IGNORECASE))`
    #       currently it's named with where_ prefix for consistency with
    #       texts_like & co conditions
    def where_flags(self, flags: re.RegexFlag, /) -> Condition[Element]:
        return self.__class__(
            self.__expected,
            self.__flags | flags,
            self.__inverted,
        )


def native_property(name: str):
    def property_value(element: Element):
        return element.locate().get_property(name)

    def property_values(collection: Collection):
        return [element.get_property(name) for element in collection()]

    raw_property_condition = ElementCondition.raise_if_not_actual(
        'has native property ' + name, property_value, predicate.is_truthy
    )

    class PropertyWithValues(ElementCondition):
        def value(self, expected: str | int | float) -> Condition[Element]:
            return ElementCondition.raise_if_not_actual(
                f"has native property '{name}' with value '{expected}'",
                property_value,
                predicate.str_equals(expected),
            )

        def value_containing(self, expected: str | int | float) -> Condition[Element]:
            return ElementCondition.raise_if_not_actual(
                f"has native property '{name}' with value containing '{expected}'",
                property_value,
                predicate.str_includes(expected),
            )

        def values(
            self, *expected: str | int | float | Iterable[str]
        ) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has native property '{name}' with values '{expected_}'",
                property_values,
                predicate.str_equals_to_list(expected_),
            )

        def values_containing(
            self, *expected: str | int | float | Iterable[str]
        ) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has native property '{name}' with values containing '{expected_}'",
                property_values,
                predicate.str_equals_by_contains_to_list(expected_),
            )

    return PropertyWithValues(
        str(raw_property_condition), test=raw_property_condition.__call__
    )


def element_has_css_property(name: str):
    def property_value(element: Element) -> str:
        return element().value_of_css_property(name)

    def property_values(collection: Collection) -> List[str]:
        return [element.value_of_css_property(name) for element in collection()]

    raw_property_condition = ElementCondition.raise_if_not_actual(
        'has css property ' + name, property_value, predicate.is_truthy
    )

    class ConditionWithValues(ElementCondition):
        def value(self, expected: str) -> Condition[Element]:
            return ElementCondition.raise_if_not_actual(
                f"has css property '{name}' with value '{expected}'",
                property_value,
                predicate.equals(expected),
            )

        def value_containing(self, expected: str) -> Condition[Element]:
            return ElementCondition.raise_if_not_actual(
                f"has css property '{name}' with value containing '{expected}'",
                property_value,
                predicate.includes(expected),
            )

        def values(self, *expected: Union[str, Iterable[str]]) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has css property '{name}' with values '{expected_}'",
                property_values,
                predicate.equals_to_list(expected_),
            )

        def values_containing(
            self, *expected: Union[str, Iterable[str]]
        ) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has css property '{name}' with values containing '{expected_}'",
                property_values,
                predicate.equals_by_contains_to_list(expected_),
            )

    return ConditionWithValues(
        str(raw_property_condition), test=raw_property_condition.__call__
    )


class attribute(Condition[Element]):

    # todo: the raw attribute condition does not support ignore_case, should it?
    def __init__(self, name: str, _inverted=False):
        self.__expected = name
        # self.__ignore_case = _ignore_case
        self.__inverted = _inverted

        super().__init__(
            f"has attribute '{name}'",
            actual=query.attribute(name),
            by=predicate.is_truthy,  # todo: should it be more like .is_not_none?
            _inverted=_inverted,
        )

    def value(self, expected):
        return _EntityHasSomethingSupportingIgnoreCase(
            f"has attribute '{self.__expected}' with value",
            expected=expected,
            actual=query.attribute(self.__expected),
            by=predicate.equals,
            _inverted=self.__inverted,
        )

    def value_containing(self, expected):
        return _EntityHasSomethingSupportingIgnoreCase(
            f"has attribute '{self.__expected}' with value containing",
            expected=expected,
            actual=query.attribute(self.__expected),
            by=predicate.includes,
            _inverted=self.__inverted,
        )

    def values(self, *expected: str | int | float | Iterable[str]):
        return _CollectionHasSomeThingsSupportingIgnoreCase(
            f"has attribute '{self.__expected}' with values",
            *expected,
            actual=query.attributes(self.__expected),
            by=predicate.str_equals_to_list,
            _inverted=self.__inverted,
        )

    def values_containing(self, *expected: str | int | float | Iterable[str]):
        return _CollectionHasSomeThingsSupportingIgnoreCase(
            f"has attribute '{self.__expected}' with values containing",
            *expected,
            actual=query.attributes(self.__expected),
            by=predicate.str_equals_by_contains_to_list,
            _inverted=self.__inverted,
        )


def value(expected: str | int | float, _inverted=False):
    return attribute('value', _inverted).value(expected)


def value_containing(expected: str | int | float, _inverted=False):
    return attribute('value', _inverted).value_containing(expected)


def values(*expected: str | int | float | Iterable[str], _inverted=False):
    return attribute('value', _inverted).values(*expected)


def values_containing(*expected: str | int | float | Iterable[str], _inverted=False):
    return attribute('value', _inverted).values_containing(*expected)


def css_class(name: str, _inverted=False):
    def class_attribute_value(element: Element):
        return element.locate().get_attribute('class')

    return _EntityHasSomethingSupportingIgnoreCase(
        'has css class',
        expected=name,
        actual=class_attribute_value,
        by=predicate.includes_word,
        _inverted=_inverted,
    )


# it can't be implemented as exact_text('').and_(value(''))
# because value of <li ...>...</li> is '0'! o_O
blank: Condition[Element] = Match(
    'is blank',
    actual=lambda element: (
        ('value', webelement.get_attribute('value'))
        if (webelement := element.locate()) and webelement.tag_name == 'input'
        else ('text', webelement.text)
    ),
    by=lambda actual_desc_and_result: not actual_desc_and_result[1],
    # todo: document in docs the following: specifically in this case,
    #       providing _describe_actual_result is not like that important
    #       because if skipped the actual rendering would be just
    #       'actual: (text|value, ...)' instead of 'actual text|value: ...'
    #       that is not much less informative...
    #       once documented, I would consider removing this customization...
    _describe_actual_result=lambda actual_desc_and_result: (
        f'actual {actual_desc_and_result[0]}: {actual_desc_and_result[1]}'
    ),
)
"""Asserts that element is blank,
i.e. has empty value if is an <input> element or empty text otherwise.

Is similar to the experimental 4-in-1 [_empty][selene.core.match._empty] condition,
works only for singular elements: if they are a value-based elements
(like inputs and textarea) then it checks for empty value,
if they are text-based elements then it checks for empty text content.

The `_empty` condition works same but if applied to collection
then will assert that it has size 0. And when applied to "form" element,
then will check for all form "value-like" inputs to be empty.
Hence, the `blank` condition is more precise, while `empty` is more general.
Because of its generality, the `empty` condition can be easier to remember,
but can lead to some kind of confusion when applied to both element
and collection in same test.
"""


# probably we don't need such over-complication of creating 2 conditions in 1
# but let's leave it so far, just as an example of potentially possible impl.
def tag(
    expected: str,
    _name='has tag',
    _by=predicate.equals,
) -> Condition[Element]:
    return Match(f'{_name} {expected}', actual=query.tag, by=_by(expected))


def tag_containing(expected: str) -> Condition[Element]:
    return tag(expected, _name='has tag containing', _by=predicate.includes)


# todo: find the best way to type it... as Condition[Locatable] or smth like that...
#       maybe even like as Condition[Callable]
def __size_or_value_or_text(entity: Callable):
    snapshot = entity()

    if hasattr(snapshot, '__len__'):
        return 'size', len(snapshot)

    if isinstance(snapshot, WebElement):
        return (
            # TODO: what about input of type=color? it's empty value is '#000000'
            ('value', snapshot.get_attribute('value'))
            if (tag_name := snapshot.tag_name) == 'input'
            else (
                (
                    'values of all form inputs, textareas and selects',
                    ''.join(
                        (element_with_value.get_attribute('value') or '')
                        for element_with_value in snapshot.find_elements(
                            By.CSS_SELECTOR,
                            'textarea,'
                            'input'
                            ':not([type=button])'
                            ':not([type=submit])'
                            ':not([type=reset])'
                            ':not([type=hidden])'
                            ':not([type=range])'  # todo: should we count range as empty on 0 value?
                            # ':not([type=image])'  # todo: value will be allwasy '', but should we count src?
                            ':not([type=color])'  # todo: should we count color as empty on #000000 value?
                            ':not([type=checkbox]:not(:checked))'
                            ':not([type=radio]:not(:checked))'
                            ','
                            'input[type=checkbox]:checked,'
                            'input[type=radio]:checked,'
                            'select',
                            # todo: what if some file input will not have input field but path set?
                        )
                    ),
                )
                if tag_name == 'form'
                # todo: should we count values as texts too?
                #       cause textarea value will be counted by default, but other inputs - not
                #       though it will be counted only if predefined between tags...
                # todo: another weird: textarea with text in html, even after reset to "" in UI
                #       will still return text hardcoded in html... should we count this somehow?
                else ('text', snapshot.text)
            )
        )

    if hasattr(snapshot, 'value'):
        return 'value', snapshot.value

    if hasattr(snapshot, 'text'):
        return 'text', snapshot.text

    return 'str', str(snapshot)


_empty: Condition[Callable] = Match(
    'is empty',
    __size_or_value_or_text,  # noqa
    by=lambda actual_desc_and_result: not actual_desc_and_result[1],
    _describe_actual_result=lambda actual_desc_and_result: (
        f'actual {actual_desc_and_result[0]}: {actual_desc_and_result[1]}'
    ),
)
"""Experimental 4-in-1 "is form or input or element or collection empty" condition,
that is an alternative to old and deprecated the [empty][selene.core.match.empty]
collection condition.
"""  # todo: document all details of implementation


def __is_empty(collection: Collection):
    warnings.warn(
        'match.collection_is_empty or be.empty is deprecated; '
        'use more explicit and obvious have.size(0) instead',
        DeprecationWarning,
    )
    return len(collection()) == 0


empty: Condition[Collection] = Match(
    'is empty',
    __is_empty,  # noqa
    by=predicate.is_truthy,
)
"""Deprecated 'is empty' collection condition.
Use [size(0)][selene.core.match.size] instead.
"""


class size(Match[Union[Collection, Browser, Element]]):

    def __init__(
        self,
        expected: int | dict,
        _name=lambda maybe_entity: (
            'have size' if isinstance(maybe_entity, Collection) else 'has size'
        ),
        # todo: should we also tune actual rendering based on
        #       config._match_only_visible_elements_size?
        #       ... maybe utilizing _describe_actual_result?
        _by=predicate.equals,
        _inverted=False,
    ):
        self.__expected = expected
        self.__name = lambda maybe_entity: f'{_name(maybe_entity)} {expected}'
        self.__by = _by
        self.__inverted = _inverted

        super().__init__(
            self.__name,
            actual=lambda entity: (
                len([element for element in entity.locate() if element.is_displayed()])
                if isinstance(entity, Collection)
                and entity.config._match_only_visible_elements_size
                else query.size(entity)
            ),
            by=_by(expected),
            _inverted=_inverted,
        )

    # # there is no much sense to apply or_less & co to Browser or Element sizes
    # @property
    # def or_less(self) -> Condition[Collection | Browser | Element]:
    #     return self.__class__(
    #         self.__expected,
    #         f'{self.__name} or less',
    #         predicate.is_less_than_or_equal,
    #         _inverted=self.__inverted,
    #     )
    @property
    def or_less(self) -> Condition[Collection]:
        name = cast(Callable[[Optional[Collection]], str], self.__name)
        return Match(
            lambda entity: f'{name(entity)} or less',
            query.size,
            by=predicate.is_less_than_or_equal(self.__expected),
            _inverted=self.__inverted,
        )

    @property
    def or_more(self) -> Condition[Collection]:
        name = cast(Callable[[Optional[Collection]], str], self.__name)
        return Match(
            lambda entity: f'{name(entity)} or more',
            query.size,
            by=predicate.is_greater_than_or_equal(self.__expected),
            _inverted=self.__inverted,
        )

    @property
    def _more_than(self) -> Condition[Collection]:
        return Match(
            lambda entity: (
                ('have' if isinstance(entity, Collection) else 'has')
                + f' size more than {self.__expected}'
            ),
            query.size,
            by=predicate.is_greater_than(self.__expected),
            _inverted=self.__inverted,
        )

    @property
    def _less_than(self) -> Condition[Collection]:
        return Match(
            lambda entity: (
                ('have' if isinstance(entity, Collection) else 'has')
                + f' size less than {self.__expected}'
            ),
            query.size,
            by=predicate.is_less_than(self.__expected),
            _inverted=self.__inverted,
        )


def size_greater_than(expected: int, _inverted=False):
    return size(expected, _inverted=_inverted)._more_than


def size_greater_than_or_equal(expected: int, _inverted=False):
    return size(expected, _inverted=_inverted).or_more


def size_less_than(expected: int, _inverted=False):
    return size(expected, _inverted=_inverted)._less_than


def size_less_than_or_equal(expected: int, _inverted=False):
    return size(expected, _inverted=_inverted).or_less


def texts(
    *expected: str | int | float | Iterable[str], _ignore_case=False, _inverted=False
):
    # todo: consider counting _match_only_visible_elements_texts in name
    return _CollectionHasSomeThingsSupportingIgnoreCase(
        'have texts',
        *expected,
        actual=lambda collection: (
            query.visible_texts(collection)
            if collection.config._match_only_visible_elements_texts
            else query.texts(collection)
        ),
        by=predicate.equals_by_contains_to_list,
        _ignore_case=_ignore_case,
        _inverted=_inverted,
    )


def exact_texts(
    *expected: str | int | float | Iterable[str], _ignore_case=False, _inverted=False
):
    # todo: consider counting _match_only_visible_elements_texts in name
    return _CollectionHasSomeThingsSupportingIgnoreCase(
        'have exact texts',
        *expected,
        actual=lambda collection: (
            query.visible_texts(collection)
            if collection.config._match_only_visible_elements_texts
            else query.texts(collection)
        ),
        by=predicate.equals_to_list,
        _ignore_case=_ignore_case,
        _inverted=_inverted,
    )


# todo: refactor to be more like element_has_text,
#       i.e. reusing core logic of Condition,
#       not overriding it
class _exact_texts_like(Condition[Collection]):
    """Condition to match visible texts of all elements in a collection
    with supported list globs for items (item placeholders
    to include/exclude items from match).
    """

    _MATCHING_SEPARATOR = '‚'  # it's not a regular ',', it's a unicode version;)
    """A separator to be used while matching
    to separate texts of different elements in a collection.

    Should be quite unique to not interfere with actual texts characters.
    Otherwise, will brake the match.

    Should be a one character string,
    because is used in predefined pattern for "exactly one" globbing
    that might not work correctly if there will be more than one character.
    """
    _MATCHING_EMPTY_STRING_MARKER = '‹EMTPY_STRING›'
    _RENDERING_SEPARATOR = ', '
    _RENDERING_TRANSLATIONS = (
        (..., '...'),
        ([...], '[...]'),
        ((...,), '(...,)'),
        ([(...,)], '[(...,)])'),
    )

    _PredefinedPatternType = Literal[
        'exactly_one', 'zero_or_one', 'one_or_more', 'zero_or_more'
    ]

    # TODO: consider to redefine on self (or other options),
    #  to get fresh version of _MATCHING_SEPARATOR if it was patched
    _PredefinedGlobPatterns: Dict[_PredefinedPatternType, str] = dict(
        # TODO: ensure correctness of patterns
        exactly_one=r'[^' + _MATCHING_SEPARATOR + r']+',
        zero_or_one=r'[^' + _MATCHING_SEPARATOR + r']*',
        one_or_more=r'.+?',
        zero_or_more=r'.*?',
    )

    _DEFAULT_GLOBS: Tuple[Tuple[Any, str], ...] = (
        (..., _PredefinedGlobPatterns['exactly_one']),
        ([...], _PredefinedGlobPatterns['zero_or_one']),
        ((...,), _PredefinedGlobPatterns['one_or_more']),
        ([(...,)], _PredefinedGlobPatterns['zero_or_more']),
    )

    # TODO: consider this set of list globs as a default
    __X_DEFAULT_GLOBS: Tuple[Tuple[Any, str], ...] = (
        ({...}, _PredefinedGlobPatterns['exactly_one']),
        ([{...}], _PredefinedGlobPatterns['zero_or_one']),
        (..., _PredefinedGlobPatterns['one_or_more']),
        ([...], _PredefinedGlobPatterns['zero_or_more']),
    )

    def __init__(
        self,
        *expected: str | int | float | Iterable,
        _inverted=False,
        _globs: Tuple[Tuple[Any, str], ...] = (),
        _name_prefix: str = 'have',
        _name: str = 'exact texts like',
        _flags=0,
    ):  # noqa
        if self._MATCHING_SEPARATOR.__len__() != 1:
            raise ValueError('MATCHING_SEPARATOR should be a one character string')
        super().__init__(lambda _: self.__str__(), test=self.__call__)
        self._expected = expected
        self._inverted = _inverted
        self._globs = _globs if _globs else _exact_texts_like._DEFAULT_GLOBS
        self._name_prefix = _name_prefix
        self._name = _name
        self._flags = _flags
        # actually disabling any patterns, processing as a normal string
        self._process_patterns: Callable[[str], str] = re.escape  # HARDCODED by intent
        # should we use above Callable[[AnyStr], AnyStr]

    # on subclassing this class, in case of new params to init
    # you have to ensure that such new params are counted in overriden not_
    # – actually this is not True anymore, you can skip overriding not_
    #   if you did not change the core test logic...
    #   But we did change it here... Seems like :D
    @override
    @property
    def not_(self):
        return self.__class__(
            *self._expected,
            _inverted=not self._inverted,
            _globs=self._globs,
            _name_prefix=self._name_prefix,
            _name=self._name,
            _flags=self._flags,
        )

    # we should not allow any other flags except re.IGNORECASE
    # and even the latter should be set kind of "implicitly"...
    # because playing with flags here might brake the globs matching
    # TODO: or not?
    @property
    def ignore_case(self) -> Condition[Collection]:
        return self.__class__(
            *self._expected,
            _inverted=self._inverted,
            _globs=self._globs,
            _name_prefix=self._name_prefix,
            _name=self._name,
            _flags=self._flags | re.IGNORECASE,
        )

    def where(
        self,
        *,
        exactly_one: Any = None,
        zero_or_one: Any = None,
        one_or_more: Any = None,
        zero_or_more: Any = None,
    ) -> Self:

        kwargs: Dict[_exact_texts_like._PredefinedPatternType, Any] = {
            'exactly_one': exactly_one,
            'zero_or_one': zero_or_one,
            'one_or_more': one_or_more,
            'zero_or_more': zero_or_more,
        }

        # TODO: since we removed customization via tuple of tuples,
        #       consider refactoring to using dict for globs management
        return self.__class__(
            *self._expected,
            _inverted=self._inverted,
            _globs=tuple(
                (glob_marker, self._PredefinedGlobPatterns[glob_pattern_type])
                for glob_pattern_type, glob_marker in kwargs.items()
            ),
            _name_prefix=self._name_prefix,
            _name=self._name,
            _flags=self._flags,
        )

    @property
    def _glob_markers(self):
        return [glob_marker for glob_marker, _ in self._globs]

    def __call__(self, entity: Collection):

        actual_texts = (
            [
                webelement.text
                for webelement in entity.locate()
                if webelement.is_displayed()
            ]
            if entity.config._match_only_visible_elements_texts
            else [webelement.text for webelement in entity.locate()]
        )
        # TODO: should we just check for * in pattern here and further for zero_like?
        # TODO: consider moving to self
        zero_like = lambda item_marker: item_marker in [
            marker
            for marker, pattern in self._globs
            if pattern
            in (
                _exact_texts_like._PredefinedGlobPatterns['zero_or_one'],
                _exact_texts_like._PredefinedGlobPatterns['zero_or_more'],
            )
        ]
        actual_to_match = (
            # seems like not needed anymore, once we refactored from join to reduce
            # in order to be able to add '?' for zero_like in the end...
            # see more explanation below...
            #
            # (
            #     # zero_like globs in the START needs an extra separator
            #     # to match correctly
            #     _exact_texts_like._MATCHING_SEPARATOR
            #     if zero_like_at_start
            #     else ''
            # )
            # +
            _exact_texts_like._MATCHING_SEPARATOR.join(
                text if text != '' else _exact_texts_like._MATCHING_EMPTY_STRING_MARKER
                for text in actual_texts
            )
            # zero_like globs in the END needed an extra separator ...
            # + (
            #     # zero_like globs in the END needs an extra separator at the end
            #     # to match correctly
            #     _exact_texts_like._MATCHING_SEPARATOR
            #     if zero_like_at_end
            #     else ''
            # )
            # but to make zero_like work on actual zero items in the middle
            # we had to add this extra separator for all types of globs...
            # actually we needed a different thing but the latter happened
            # as a side effect... so in order to not "clean side effects"
            # we just add here the same separator for all cases in the end:
            + _exact_texts_like._MATCHING_SEPARATOR
        )
        actual_to_render = _exact_texts_like._RENDERING_SEPARATOR.join(actual_texts)

        glob_pattern_by = lambda marker: next(  # noqa
            glob_pattern
            for glob_marker, glob_pattern in self._globs
            if glob_marker == marker
        )
        with_added_empty_string_marker = lambda item: (
            str(item) if item != '' else _exact_texts_like._MATCHING_EMPTY_STRING_MARKER
        )
        MATCHING_SEPARATOR = re.escape(_exact_texts_like._MATCHING_SEPARATOR)
        expected_pattern = (
            r'^'
            # + re.escape(_exact_texts_like._MATCHING_SEPARATOR).join(
            #     (
            #         re.escape(with_added_empty_string_marker(item))
            #         if item not in self._glob_markers
            #         else glob_pattern_by(item)
            #     )
            #     for item in self._expected
            # )
            # – refactored join to reduce, being able to modify separator for cases
            # where next marker is zero_like (e.g. from , to ,?)
            + str(
                reduce(
                    lambda acc, item: (
                        acc
                        + (
                            self._process_patterns(with_added_empty_string_marker(item))
                            + MATCHING_SEPARATOR
                            if item not in self._glob_markers
                            else (
                                glob_pattern_by(item)
                                + MATCHING_SEPARATOR
                                + ('?' if zero_like(item) else '')
                            )
                        )
                    ),
                    self._expected,
                    '',  # start from '' as acc to add separator after item not before
                )
            )
            + r'$'
        )

        answer = None
        regex_invalid_error: re.error | None = None

        try:
            answer = re.match(
                expected_pattern,
                actual_to_match,
                (
                    self._flags | re.IGNORECASE
                    if entity.config._ignore_case
                    else self._flags
                ),
            )
        except re.error as error:
            # going to re-raise it below as AssertionError on `not answer`
            regex_invalid_error = error

        def describe_not_match():
            # TODO: implement pattern_explained
            #       probably after refactoring from tuple to dict as globs storage
            # pattern_explained = [
            #     next(...) if item in self._glob_markers else item
            #     for item in self._expected
            # ]
            return (
                f'actual '
                + (
                    'visible '
                    if entity.config._match_only_visible_elements_texts
                    else ''
                )
                + f'texts:\n    {actual_to_render}\n'
                + '\n'
                # f'Pattern explained:\n    {pattern_explained}\n'
                + f'Pattern used for matching:\n    {expected_pattern}\n'
                # TODO: consider renaming to Actual merged text for match
                + f'Actual text used to match:\n    {actual_to_match}'
            )

        if regex_invalid_error:
            raise AssertionError(
                (f' RegexError: {regex_invalid_error}\n' if regex_invalid_error else '')
                + describe_not_match()
            )

        if answer if self._inverted else not answer:
            raise AssertionError(
                (f' RegexError: {regex_invalid_error}\n' if regex_invalid_error else '')
                + describe_not_match()
            )

    def __str__(self):
        # TODO: consider adding self._name_suffix to contain "like"
        #       so we can format message like
        #       .have texts (flags: re.IGNORECASE) like:
        #       over
        #       .have texts like (flags: re.IGNORECASE):
        # TODO: after previous, we can implement shortcut "ignoring case"
        #       for " (flags: re.IGNORECASE)"
        return (
            # todo: consider wrapping negated part into () like in other conditions
            # todo: consider square brackets arround list of texts like in other conditions
            f'{self._name_prefix} {"no " if self._inverted else ""}{self._name}'
            + (f' (flags: {self._flags})' if self._flags else '')
            + ':'
            + '\n    '
            + _exact_texts_like._RENDERING_SEPARATOR.join(
                (
                    str(item)
                    if item
                    not in [
                        marker
                        for marker, _ in _exact_texts_like._RENDERING_TRANSLATIONS
                    ]
                    else next(
                        translation
                        for marker, translation in _exact_texts_like._RENDERING_TRANSLATIONS
                        if marker == item
                    )
                )
                for item in self._expected
            )
        )

    def _name_for(self, entity: Collection | None = None) -> str:
        return (
            self.ignore_case.__str__()
            if entity is not None and entity.config._ignore_case
            else self.__str__()
        )

    # TODO: will other methods like or_, and_ – do work? o_O


# texts_pattern can be a good alias for text_patterns_like
# assuming that s_pattern covers both
# – item as globs (_like) and items as regex (patternS)
# but for consistency, let's not break the convention of adding _like everywhere
# where we use item globs
class _text_patterns_like(_exact_texts_like):
    """Condition to match visible texts of all elements in a collection
    with supported item placeholders to include/exclude items from match
    (like [_exact_texts_like][selene.match._exact_texts_like] condition)
    and with additionally supported wildcards (implicit and explicit)
    for the corresponding matching of each item text in a collection"""

    def __init__(
        self,
        *expected: str | int | float | Iterable,
        # by default nothing is processed,
        # i.e. items will be considered as regex patterns
        # with behavior similar to implicit ^ and $ for each item text
        _process_patterns: Callable[[str], str] = lambda item: item,
        _inverted=False,
        _name_prefix='have',
        _name='text patterns like',
        # even though we don't customize globs in this class
        # the child classes can, so at least we have to pass through globs
        _globs=(),
        _flags=0,
    ):  # noqa
        super().__init__(
            *expected,
            _inverted=_inverted,
            _globs=_globs,
            _name_prefix=_name_prefix,
            _name=_name,
            _flags=_flags,
        )
        self._process_patterns = _process_patterns

    # Have to override because of added _process_patterns to pass through
    @override
    @property
    def not_(self):
        return self.__class__(
            *self._expected,
            _process_patterns=self._process_patterns,  # <- override for this
            _inverted=not self._inverted,  # <- while this is main change in this prop
            _globs=self._globs,
            _name_prefix=self._name_prefix,
            _name=self._name,
            _flags=self._flags,
        )

    def where_flags(self, flags: re.RegexFlag, /) -> Condition[Collection]:
        return self.__class__(
            *self._expected,
            _process_patterns=self._process_patterns,
            _inverted=self._inverted,
            _globs=self._globs,  # not mandatory for this class, but just in case
            _name_prefix=self._name_prefix,
            _name=self._name,
            _flags=self._flags | flags,
        )

    # Have to override because parrent does not path through _process_patterns
    @override
    @property
    def ignore_case(self) -> Condition[Collection]:
        return self.where_flags(re.IGNORECASE)


# todo: add an alias from texts(*expected).with_regex to text_patterns_like
#       hm, but then it would be natural
#       if we disable implicit ^ and $ for each item text
#       and so we make it inconsistent with the behavior of *_like versions
#       then probably we should explicitly document that we are not going
#       to add such type of condition at all
class _text_patterns(_text_patterns_like):
    """Condition to match visible texts of all elements in a collection
    with supported item placeholders to include/exclude items from match
    (like [_exact_texts_like][selene.match._exact_texts_like] condition)
    and with additionally supported wildcards (implicit and explicit)
    for the corresponding matching of each item text in a collection"""

    def __init__(
        self,
        *expected: str | int | float | Iterable,
        # by default nothing is processed,
        # i.e. items will be considered as regex patterns
        # with behavior similar to implicit ^ and $ for each item text
        _process_patterns: Callable[[str], str] = lambda item: item,
        _inverted=False,
        _globs=(),  # just to match interface (will be actually skipped)
        _name_prefix='have',
        _name='text patterns',
        _flags=0,
    ):  # noqa
        super().__init__(
            *helpers.flatten(expected),  # TODO: document
            _process_patterns=_process_patterns,
            _inverted=_inverted,
            _name_prefix=_name_prefix,
            _name=_name,
            _flags=_flags,
        )
        # disable globs (doing after __init__ to override defaults)
        self._globs = ()

    # TODO: consider refactoring so this attribute is not even inherited
    @override
    def where(self, **kwargs):
        """Just a placeholder. This attribute is not supported for this condition"""
        raise AttributeError('.where(**) is not supported on text_patterns condition')

    # TODO: can and should we disable here the .where method?
    #       shouldn't we just simply implement it in a straightforward style
    #       similar to match.exact_texts?
    #       then ^ and $ will be explicit instead of implicit as for now


class _texts_like(_exact_texts_like):
    """Condition to match visible texts of all elements in a collection
    with supported item globs (placeholders to include/exclude items from match,
    like in [_exact_texts_like][selene.match._exact_texts_like] condition)
    and matching each expected item text (that is not an item glob) – "by contains".
    Has additional support for classic wildcards via `.with_wildcards` method
    (* matches any number of any characters including none,
    ? matches any single character).
    """

    def __init__(
        self,
        *expected: str | int | float | Iterable,
        # match text by contains by default:
        _process_patterns: Callable[[str], str] = lambda item: r'.*?'
        + re.escape(item)
        + r'.*?',
        _inverted=False,
        _globs=(),
        _name_prefix='have',
        _name='texts like',
        _flags=0,
    ):
        super().__init__(
            *expected,
            _inverted=_inverted,
            _globs=_globs,  # just in case – passing through
            _name_prefix=_name_prefix,
            _name=_name,
            _flags=_flags,
        )

        self._process_patterns = _process_patterns

    @override
    @property
    def not_(self):
        return self.__class__(
            *self._expected,
            _process_patterns=self._process_patterns,  # <- override for this
            _inverted=not self._inverted,  # <- while this is main feature in this prop
            _globs=self._globs,
            _name_prefix=self._name_prefix,
            _name=self._name,
            _flags=self._flags,
        )

    @override
    @property
    def ignore_case(self) -> Self:
        return self.__class__(
            *self._expected,
            _process_patterns=self._process_patterns,  # <- override for this
            _inverted=self._inverted,
            _globs=self._globs,
            _name_prefix=self._name_prefix,
            _name=self._name,
            _flags=self._flags | re.IGNORECASE,
        )

    @property
    def with_regex(self):
        """An alias to [_text_patterns_like][selene.match._text_patterns_like] condition
        : switches to regex matching mode for all items in the expected list"""
        return _text_patterns_like(
            *self._expected,
            _inverted=self._inverted,
            _globs=self._globs,
            _flags=self._flags,
        )

    @property
    def with_wildcards(self):
        # TODO: do we really need _chars suffix?
        return self.where_wildcards(zero_or_more_chars='*', exactly_one_char='?')

    def where_wildcards(self, zero_or_more_chars=None, exactly_one_char=None):
        def process_wildcards(item: str) -> str:
            """
            TODO: support more wildcards: [abc], [a-z], [!abc], [!a-z]
            """
            if zero_or_more_chars is None and exactly_one_char is None:
                return self._process_patterns(item)

            wildcards_with_pattern = filter(
                lambda pair: pair[0] != '',
                (
                    (re.escape(zero_or_more_chars or ''), r'.*?'),
                    (re.escape(exactly_one_char or ''), r'.'),
                ),
            )

            return reduce(
                lambda acc, wildcard_with_pattern: acc.replace(*wildcard_with_pattern),
                wildcards_with_pattern,
                re.escape(item),
            )

        # return base class to disable doubled `.with_wildcards.with_wildcards`
        return _text_patterns_like(
            *self._expected,
            _process_patterns=process_wildcards,
            _inverted=self._inverted,
            _globs=self._globs,
            _name='texts with wildcards like',
            _flags=self._flags,
        )

    # # TODO: without this override it will fail with "nothing to repeat" when:
    # #       have._texts_like(r'*two*', r'*one*', ...)
    # #         .where_wildcards(zero_or_more_chars='*')
    # #         .ignore_case.not_
    # #       why?
    # @property
    # def ignore_case(self):
    #     return _texts_like(
    #         *self._expected,
    #         _process_patterns=self._process_patterns,
    #         _inverted=self._inverted,
    #         _name_prefix=self._name_prefix,
    #         _name=self._name,
    #         _flags=self._flags | re.IGNORECASE,
    #     )


def url(
    expected: str, _name='has url', _by=predicate.equals, _inverted=False
) -> _EntityHasSomethingSupportingIgnoreCase[Browser]:
    return _EntityHasSomethingSupportingIgnoreCase(
        _name, expected, actual=query.url, by=_by, _inverted=_inverted
    )


def url_containing(expected: str, _inverted=False):
    return url(expected, 'has url containing', predicate.includes, _inverted=_inverted)


def title(
    expected: str, _name='has title', _by=predicate.equals, _inverted=False
) -> _EntityHasSomethingSupportingIgnoreCase[Browser]:
    return _EntityHasSomethingSupportingIgnoreCase(
        _name, expected, actual=query.title, by=_by, _inverted=_inverted
    )


def title_containing(expected: str, _inverted=False):
    return title(
        expected, 'has title containing', predicate.includes, _inverted=_inverted
    )


class tabs_number(Match[Browser]):

    def __init__(
        self,
        expected: int | dict,
        _name='has tabs number',
        _by=predicate.equals,
        _inverted=False,
    ):
        self.__expected = expected
        self.__name = f'{_name} {expected}'
        self.__by = _by
        self.__inverted = _inverted

        super().__init__(
            self.__name,
            actual=query.tabs_number,
            by=_by(expected),
            _inverted=_inverted,
        )

    @property
    def or_less(self) -> Condition[Browser]:
        return Match(
            f'{self.__name} or less',
            query.tabs_number,
            by=predicate.is_less_than_or_equal(self.__expected),
            _inverted=self.__inverted,
        )

    @property
    def or_more(self) -> Condition[Browser]:
        return Match(
            f'{self.__name} or more',
            query.tabs_number,
            by=predicate.is_greater_than_or_equal(self.__expected),
            _inverted=self.__inverted,
        )

    @property
    def _more_than(self) -> Condition[Browser]:
        return Match(
            f'has tabs number more than {self.__expected}',
            query.tabs_number,
            by=predicate.is_greater_than(self.__expected),
            _inverted=self.__inverted,
        )

    @property
    def _less_than(self) -> Condition[Browser]:
        return Match(
            f'has tabs number less than {self.__expected}',
            query.tabs_number,
            by=predicate.is_less_than(self.__expected),
            _inverted=self.__inverted,
        )


def tabs_number_greater_than(expected: int, _inverted=False):
    return tabs_number(expected, _inverted=_inverted)._more_than


def tabs_number_greater_than_or_equal(expected: int, _inverted=False):
    return tabs_number(expected, _inverted=_inverted).or_more


def tabs_number_less_than(expected: int, _inverted=False):
    return tabs_number(expected, _inverted=_inverted)._less_than


def tabs_number_less_than_or_equal(expected: int, _inverted=False):
    return tabs_number(expected, _inverted=_inverted).or_less


def browser_has_js_returned(expected: Any, script: str, *args) -> Condition[Browser]:
    warnings.warn(
        'deprecated because js does not work for mobile; '
        'use have.script_returned(True, ...) instead',
        DeprecationWarning,
    )

    return browser_has_script_returned(expected, script, *args)


def browser_has_script_returned(
    expected: Any, script: str, *args
) -> Condition[Browser]:  # TODO: should it work on element too? on collection?
    def script_result(browser: Browser):
        return browser.driver.execute_script(script, *args)

    return BrowserCondition.raise_if_not_actual(
        f'has the ```{script}``` script returned {expected}',
        script_result,
        predicate.equals(expected),
    )
