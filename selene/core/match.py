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

from typing_extensions import (
    List,
    Any,
    Union,
    Iterable,
    Tuple,
    Unpack,
    TypedDict,
    overload,
    NotRequired,
    cast,
    Literal,
    Dict,
    override,
    Callable,
    AnyStr,
    TypeVar,
    Self,
)

from selene.common import predicate, helpers
from selene.core import query
from selene.core.condition import Condition, Match
from selene.core.conditions import (
    ElementCondition,
    CollectionCondition,
    BrowserCondition,
)
from selene.core.entity import Collection, Element
from selene.core._browser import Browser

present_in_dom: Condition[Element] = Match(
    'is present in DOM',
    actual=lambda element: element.locate(),
    by=lambda webelement: webelement is not None,
)

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
)
"""Deprecated 'is existing' condition. Use present_in_dom instead."""


visible: Condition[Element] = Match(
    'is visible',
    actual=lambda element: element.locate(),
    by=lambda actual: actual.is_displayed(),
)

hidden: Condition[Element] = Condition.as_not(visible, 'is hidden')

hidden_in_dom: Condition[Element] = present_in_dom.and_(visible.not_)


element_is_enabled: Condition[Element] = ElementCondition.raise_if_not(
    'is enabled', lambda element: element().is_enabled()
)

element_is_disabled: Condition[Element] = ElementCondition.as_not(element_is_enabled)

element_is_clickable: Condition[Element] = visible.and_(element_is_enabled)

# TODO: how will it work for mobile?
element_is_focused: Condition[Element] = ElementCondition.raise_if_not(
    'is focused',
    lambda element: element()
    == element.config.driver.execute_script('return document.activeElement'),
)


class _ElementHasText(Condition[Element]):

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

        # # actually happened to be not needed, both _ params and even closures of self
        # def describe(_):  # actually we don't need here passing self through describe
        #     return (
        #         f'{_describing_matched_to}'
        #         f'{" ignoring case: "if _ignore_case else ""} {expected}'
        #     )
        #
        # def compare(_):  # here we also don't need it, closure's self is enough
        #     return lambda actual: (
        #         _compared_by_predicate_to(str(expected).lower())(str(actual).lower())
        #         if _ignore_case
        #         else _compared_by_predicate_to(str(expected))(str(actual))
        #     )

        super().__init__(
            (
                f'{_describing_matched_to}'
                f'{" ignoring case:" if _ignore_case else ""} {expected}'
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


def text(expected: str | int | float, _ignore_case=False, _inverted=False):
    return _ElementHasText(
        expected, 'has text', predicate.includes, _ignore_case, _inverted=_inverted
    )


def exact_text(expected: str | int | float, _ignore_case=False, _inverted=False):
    return _ElementHasText(
        expected, 'has exact text', predicate.equals, _ignore_case, _inverted=_inverted
    )


class text_pattern(Condition[Element]):

    def __init__(self, expected: str, _flags=0, _inverted=False):
        self.__expected = expected
        self.__flags = _flags
        self.__inverted = _inverted
        # TODO: on invalid pattern error will be:
        #       'Reason: ConditionMismatch: nothing to repeat at position 0'
        #       how to improve it? leaving more hints that this is "regex invalid error"
        #       probably, we can re-raise re.error inside predicate.matches
        #       with additional explanation

        super().__init__(
            f'has text matching{f" (with flags {_flags}):" if _flags else ""}'
            f' {expected}',
            actual=query.text,
            by=predicate.matches(expected, _flags),
            _inverted=_inverted,
        )

    @property
    def ignore_case(self):
        return self.where_flags(re.IGNORECASE)

    # TODO: should we shorten name just to flags? i.e.
    #       `.should(have.text_matching(r'.*one.*').flags(re.IGNORECASE))`
    #       over
    #       `.should(have.text_matching(r'.*one.*').where_flags(re.IGNORECASE))`
    def where_flags(self, flags: re.RegexFlag, /) -> Condition[Element]:
        return self.__class__(
            self.__expected,
            self.__flags | flags,
            self.__inverted,
        )


def element_has_js_property(name: str):
    # TODO: will this even work for mobile? o_O
    #       if .get_property is valid for mobile
    #       then we should rename it for sure here...
    # TODO: should we keep simpler but less obvious name - *_has_property ?
    def property_value(element: Element):
        return element.locate().get_property(name)

    def property_values(collection: Collection):
        return [element.get_property(name) for element in collection()]

    raw_property_condition = ElementCondition.raise_if_not_actual(
        'has js property ' + name, property_value, predicate.is_truthy
    )

    class ConditionWithValues(ElementCondition):
        def value(self, expected: str | int | float) -> Condition[Element]:
            return ElementCondition.raise_if_not_actual(
                f"has js property '{name}' with value '{expected}'",
                property_value,
                predicate.str_equals(expected),
            )

        def value_containing(self, expected: str | int | float) -> Condition[Element]:
            return ElementCondition.raise_if_not_actual(
                f"has js property '{name}' with value containing '{expected}'",
                property_value,
                predicate.str_includes(expected),
            )

        def values(
            self, *expected: str | int | float | Iterable[str]
        ) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has js property '{name}' with values '{expected_}'",
                property_values,
                predicate.str_equals_to_list(expected_),
            )

        def values_containing(
            self, *expected: str | int | float | Iterable[str]
        ) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has js property '{name}' with values containing '{expected_}'",
                property_values,
                predicate.str_equals_by_contains_to_list(expected_),
            )

    return ConditionWithValues(
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


def element_has_attribute(name: str):
    def attribute_value(element: Element):
        return element.locate().get_attribute(name)

    def attribute_values(collection: Collection):
        return [element.get_attribute(name) for element in collection()]

    raw_attribute_condition = ElementCondition.raise_if_not_actual(
        'has attribute ' + name, attribute_value, predicate.is_truthy
    )

    # TODO: is it OK to have some collection conditions inside a thing named element_has_attribute ? o_O
    class ConditionWithValues(ElementCondition):
        def value(
            self, expected: str | int | float, ignore_case=False
        ) -> Condition[Element]:
            if ignore_case:
                warnings.warn(
                    'ignore_case syntax is experimental and might change in future',
                    FutureWarning,
                )
            return ElementCondition.raise_if_not_actual(
                f"has attribute '{name}' with value '{expected}'",
                attribute_value,
                predicate.str_equals(expected, ignore_case),
            )

        def value_containing(
            self, expected: str | int | float, ignore_case=False
        ) -> Condition[Element]:
            if ignore_case:
                warnings.warn(
                    'ignore_case syntax is experimental and might change in future',
                    FutureWarning,
                )
            return ElementCondition.raise_if_not_actual(
                f"has attribute '{name}' with value containing '{expected}'",
                attribute_value,
                predicate.str_includes(expected, ignore_case),
            )

        def values(
            self, *expected: str | int | float | Iterable[str]
        ) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has attribute '{name}' with values '{expected_}'",
                attribute_values,
                predicate.str_equals_to_list(expected_),
            )

        def values_containing(
            self, *expected: str | int | float | Iterable[str]
        ) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has attribute '{name}' with values containing '{expected_}'",
                attribute_values,
                predicate.str_equals_by_contains_to_list(expected_),
            )

    return ConditionWithValues(
        str(raw_attribute_condition), test=raw_attribute_condition.__call__
    )


element_is_selected: Condition[Element] = ElementCondition.raise_if_not(
    'is selected', lambda element: element().is_selected()
)


def element_has_value(expected: str | int | float) -> Condition[Element]:
    return element_has_attribute('value').value(expected)


def element_has_value_containing(expected: str | int | float) -> Condition[Element]:
    return element_has_attribute('value').value_containing(expected)


def collection_has_values(
    *expected: str | int | float | Iterable[str],
) -> Condition[Collection]:
    return element_has_attribute('value').values(*expected)


def collection_has_values_containing(
    *expected: str | int | float | Iterable[str],
) -> Condition[Collection]:
    return element_has_attribute('value').values_containing(*expected)


def element_has_css_class(expected: str) -> Condition[Element]:
    def class_attribute_value(element: Element):
        return element.locate().get_attribute('class')

    return ElementCondition.raise_if_not_actual(
        f"has css class '{expected}'",
        class_attribute_value,
        predicate.includes_word(expected),
    )


element_is_blank: Condition[Element] = exact_text('').and_(element_has_value(''))


def element_has_tag(
    expected: str,
    describing_matched_to='has tag',
    compared_by_predicate_to=predicate.equals,
) -> Condition[Element]:
    return ElementCondition.raise_if_not_actual(
        f'{describing_matched_to} + {expected}',
        query.tag,
        compared_by_predicate_to(expected),
    )


def element_has_tag_containing(expected: str) -> Condition[Element]:
    return element_has_tag(expected, 'has tag containing', predicate.includes)


# TODO: should not we make empty to work on both elements and collections?
#   to assert have.size(0) on collections
#   to assert have.value('').and(have.exact_text('')) on element
def _is_collection_empty(collection: Collection) -> bool:
    warnings.warn(
        'match.collection_is_empty or be.empty is deprecated; '
        'use more explicit and obvious have.size(0) instead',
        DeprecationWarning,
    )
    return len(collection()) == 0


collection_is_empty: Condition[Collection] = CollectionCondition.raise_if_not(
    'is empty', _is_collection_empty
)


def collection_has_size(
    expected: int,
    describing_matched_to='has size',
    compared_by_predicate_to=predicate.equals,
) -> Condition[Collection]:
    def size(collection: Collection) -> int:
        return len(collection())

    return CollectionCondition.raise_if_not_actual(
        f'{describing_matched_to} {expected}',
        size,
        compared_by_predicate_to(expected),
    )


def collection_has_size_greater_than(expected: int) -> Condition[Collection]:
    return collection_has_size(
        expected, 'has size greater than', predicate.is_greater_than
    )


def collection_has_size_greater_than_or_equal(
    expected: int,
) -> Condition[Collection]:
    return collection_has_size(
        expected,
        'has size greater than or equal',
        predicate.is_greater_than_or_equal,
    )


def collection_has_size_less_than(expected: int) -> Condition[Collection]:
    return collection_has_size(expected, 'has size less than', predicate.is_less_than)


def collection_has_size_less_than_or_equal(
    expected: int,
) -> Condition[Collection]:
    return collection_has_size(
        expected,
        'has size less than or equal',
        predicate.is_less_than_or_equal,
    )


class _CollectionHasTexts(Condition[Collection]):

    def __init__(
        self,
        *expected: str | int | float | Iterable[str],
        _describing_matched_to='have texts',
        _compared_by_predicate_to=predicate.equals_by_contains_to_list,
        _ignore_case=False,
        _inverted=False,
    ):
        self.__expected = expected
        self.__describe_matched_to = _describing_matched_to
        self.__compared_by_predicate_to = _compared_by_predicate_to
        self.__ignore_case = _ignore_case
        self.__inverted = _inverted

        # TODO: should we store flattened version in self?
        #       how should we render nested expected in error?
        #       should we transform actual to same un-flattened structure as expected?
        #       (when rendering, of course)

        def compare(actual: Iterable) -> bool:
            expected_flattened = helpers.flatten(expected)
            str_lower = lambda some: str(some).lower()
            return (
                _compared_by_predicate_to(map(str_lower, expected_flattened))(
                    map(str_lower, actual)
                )
                if _ignore_case
                else _compared_by_predicate_to(map(str, expected_flattened))(
                    map(str, actual)
                )
            )

        super().__init__(  # type: ignore
            description=(
                f'{_describing_matched_to}'
                f'{" ignoring case:" if _ignore_case else ""} {expected}'
            ),
            actual=query.visible_texts,
            by=compare,
            _inverted=_inverted,
        )

    # returning Condition[Collection] to not allow .ignore_case.ignore_case usage:)
    @property
    def ignore_case(self) -> Condition[Collection]:
        return self.__class__(
            *self.__expected,
            _describing_matched_to=self.__describe_matched_to,
            _compared_by_predicate_to=self.__compared_by_predicate_to,
            _ignore_case=True,
            _inverted=self.__inverted,
        )


# TODO: make it configurable whether assert only visible texts or not
def texts(
    *expected: str | int | float | Iterable[str], _ignore_case=False, _inverted=False
):
    return _CollectionHasTexts(
        *expected,
        _describing_matched_to='have texts',
        _compared_by_predicate_to=predicate.equals_by_contains_to_list,
        _ignore_case=_ignore_case,
        _inverted=_inverted,
    )


def exact_texts(
    *expected: str | int | float | Iterable[str], _ignore_case=False, _inverted=False
):
    return _CollectionHasTexts(
        *expected,
        _describing_matched_to='have exact texts',
        _compared_by_predicate_to=predicate.equals_to_list,
        _ignore_case=_ignore_case,
        _inverted=_inverted,
    )


# TODO: refactor to be more like element_has_text,
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
        super().__init__(self.__str__, test=self.__call__)
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

        visible_texts = [
            webelement.text
            for webelement in entity.locate()
            if webelement.is_displayed()
        ]
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
                for text in visible_texts
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
        actual_to_render = _exact_texts_like._RENDERING_SEPARATOR.join(visible_texts)

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
            answer = re.match(expected_pattern, actual_to_match, self._flags)
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
                f'actual visible texts:\n    {actual_to_render}\n'
                '\n'
                # f'Pattern explained:\n    {pattern_explained}\n'
                f'Pattern used for matching:\n    {expected_pattern}\n'
                # TODO: consider renaming to Actual merged text for match
                f'Actual text used to match:\n    {actual_to_match}'
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


# TODO: add an alias from texts(*expected).with_regex to text_patterns_like
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
    def where(self):
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


# TODO: consider refactoring the code like below by moving outside fns like url, title, etc...
# TODO: probably we will do that nevertheless when reusing "commands&queries" inside element class definitions
def browser_has_url(
    expected: str,
    describing_matched_to='has url',
    compared_by_predicate_to=predicate.equals,
) -> Condition[Browser]:
    def url(browser: Browser) -> str:
        return browser.driver.current_url

    return BrowserCondition.raise_if_not_actual(
        f"{describing_matched_to} '{expected}'",
        url,
        compared_by_predicate_to(expected),
    )


def browser_has_url_containing(expected: str) -> Condition[Browser]:
    return browser_has_url(expected, 'has url containing', predicate.includes)


def browser_has_title(
    expected: str,
    describing_matched_to='has title',
    compared_by_predicate_to=predicate.equals,
) -> Condition[Browser]:
    def title(browser: Browser) -> str:
        return browser.driver.title

    return BrowserCondition.raise_if_not_actual(
        f"{describing_matched_to} '{expected}'",
        title,
        compared_by_predicate_to(expected),
    )


def browser_has_title_containing(expected: str) -> Condition[Browser]:
    return browser_has_title(expected, 'has title containing', predicate.includes)


def browser_has_tabs_number(
    expected: int,
    describing_matched_to='has tabs number',
    compared_by_predicate_to=predicate.equals,
) -> Condition[Browser]:
    def tabs_number(browser: Browser) -> int:
        return len(browser.driver.window_handles)

    return BrowserCondition.raise_if_not_actual(
        f'{describing_matched_to} {expected}',
        tabs_number,
        compared_by_predicate_to(expected),
    )


def browser_has_tabs_number_greater_than(expected: int) -> Condition[Browser]:
    return browser_has_tabs_number(
        expected, 'has tabs number greater than', predicate.is_greater_than
    )


def browser_has_tabs_number_greater_than_or_equal(
    expected: int,
) -> Condition[Browser]:
    return browser_has_tabs_number(
        expected,
        'has tabs number greater than or equal',
        predicate.is_greater_than_or_equal,
    )


def browser_has_tabs_number_less_than(expected: int) -> Condition[Browser]:
    return browser_has_tabs_number(
        expected, 'has tabs number less than', predicate.is_less_than
    )


def browser_has_tabs_number_less_than_or_equal(
    expected: int,
) -> Condition[Browser]:
    return browser_has_tabs_number(
        expected,
        'has tabs number less than or equal',
        predicate.is_less_than_or_equal,
    )


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
