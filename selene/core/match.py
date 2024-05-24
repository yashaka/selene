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
from selene.core.condition import Condition
from selene.core.conditions import (
    ElementCondition,
    CollectionCondition,
    BrowserCondition,
)
from selene.core.entity import Collection, Element
from selene.core._browser import Browser
from selene.core.wait import Query

# TODO: consider moving to selene.match.element.is_visible, etc...
element_is_visible: Condition[Element] = ElementCondition.raise_if_not(
    'is visible', lambda element: element().is_displayed()
)


element_is_hidden: Condition[Element] = ElementCondition.as_not(
    element_is_visible, 'is hidden'
)

element_is_enabled: Condition[Element] = ElementCondition.raise_if_not(
    'is enabled', lambda element: element().is_enabled()
)

element_is_disabled: Condition[Element] = ElementCondition.as_not(element_is_enabled)

element_is_clickable: Condition[Element] = element_is_visible.and_(element_is_enabled)

element_is_present: Condition[Element] = ElementCondition.raise_if_not(
    'is present in DOM', lambda element: element() is not None
)

element_is_absent: Condition[Element] = ElementCondition.as_not(element_is_present)

# TODO: how will it work for mobile?
element_is_focused: Condition[Element] = ElementCondition.raise_if_not(
    'is focused',
    lambda element: element()
    == element.config.driver.execute_script('return document.activeElement'),
)


def element_has_text(
    expected: str,
    describing_matched_to='has text',
    compared_by_predicate_to=predicate.includes,
) -> Condition[Element]:
    return ElementCondition.raise_if_not_actual(
        describing_matched_to + ' ' + expected,
        query.text,
        compared_by_predicate_to(expected),
    )


def element_has_exact_text(expected: str) -> Condition[Element]:
    return element_has_text(expected, 'has exact text', predicate.equals)


def text_pattern(expected: str) -> Condition[Element]:
    return ElementCondition.raise_if_not_actual(
        f'has text matching {expected}',
        query.text,
        predicate.matches(expected),
    )


def element_has_js_property(name: str):
    # TODO: should we keep simpler but less obvious name - *_has_property ?
    def property_value(element: Element):
        return element.locate().get_property(name)

    def property_values(collection: Collection):
        return [element.get_property(name) for element in collection()]

    raw_property_condition = ElementCondition.raise_if_not_actual(
        'has js property ' + name, property_value, predicate.is_truthy
    )

    class ConditionWithValues(ElementCondition):
        def value(self, expected: str) -> Condition[Element]:
            return ElementCondition.raise_if_not_actual(
                f"has js property '{name}' with value '{expected}'",
                property_value,
                predicate.equals(expected),
            )

        def value_containing(self, expected: str) -> Condition[Element]:
            return ElementCondition.raise_if_not_actual(
                f"has js property '{name}' with value containing '{expected}'",
                property_value,
                predicate.includes(expected),
            )

        def values(self, *expected: Union[str, Iterable[str]]) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has js property '{name}' with values '{expected_}'",
                property_values,
                predicate.equals_to_list(expected_),
            )

        def values_containing(
            self, *expected: Union[str, Iterable[str]]
        ) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has js property '{name}' with values containing '{expected_}'",
                property_values,
                predicate.equals_by_contains_to_list(expected_),
            )

    return ConditionWithValues(str(raw_property_condition), raw_property_condition.call)


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

    return ConditionWithValues(str(raw_property_condition), raw_property_condition.call)


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
        def value(self, expected: str, ignore_case=False) -> Condition[Element]:
            if ignore_case:
                warnings.warn(
                    'ignore_case syntax is experimental and might change in future',
                    FutureWarning,
                )
            return ElementCondition.raise_if_not_actual(
                f"has attribute '{name}' with value '{expected}'",
                attribute_value,
                predicate.equals(expected, ignore_case),
            )

        def value_containing(
            self, expected: str, ignore_case=False
        ) -> Condition[Element]:
            if ignore_case:
                warnings.warn(
                    'ignore_case syntax is experimental and might change in future',
                    FutureWarning,
                )
            return ElementCondition.raise_if_not_actual(
                f"has attribute '{name}' with value containing '{expected}'",
                attribute_value,
                predicate.includes(expected, ignore_case),
            )

        def values(self, *expected: Union[str, Iterable[str]]) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has attribute '{name}' with values '{expected_}'",
                attribute_values,
                predicate.equals_to_list(expected_),
            )

        def values_containing(
            self, *expected: Union[str, Iterable[str]]
        ) -> Condition[Collection]:
            expected_ = helpers.flatten(expected)

            return CollectionCondition.raise_if_not_actual(
                f"has attribute '{name}' with values containing '{expected_}'",
                attribute_values,
                predicate.equals_by_contains_to_list(expected_),
            )

    return ConditionWithValues(
        str(raw_attribute_condition), raw_attribute_condition.call
    )


element_is_selected: Condition[Element] = ElementCondition.raise_if_not(
    'is selected', lambda element: element().is_selected()
)


def element_has_value(expected: str) -> Condition[Element]:
    return element_has_attribute('value').value(expected)


def element_has_value_containing(expected: str) -> Condition[Element]:
    return element_has_attribute('value').value_containing(expected)


def collection_has_values(
    *expected: Union[str, Iterable[str]]
) -> Condition[Collection]:
    return element_has_attribute('value').values(*expected)


def collection_has_values_containing(
    *expected: Union[str, Iterable[str]]
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


element_is_blank: Condition[Element] = element_has_exact_text('').and_(
    element_has_value('')
)


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


# TODO: make it configurable whether assert only visible texts or ot
def collection_has_texts(*expected: Union[str, Iterable[str]]) -> Condition[Collection]:
    expected_ = helpers.flatten(expected)

    def actual_visible_texts(collection: Collection) -> List[str]:
        return [
            webelement.text for webelement in collection() if webelement.is_displayed()
        ]

    return CollectionCondition.raise_if_not_actual(
        f'has texts {expected_}',
        Query('visible texts', actual_visible_texts),
        predicate.equals_by_contains_to_list(expected_),
    )


def collection_has_exact_texts(
    *expected: str | int | float | Iterable[str],
):
    if ... in expected:  # TODO count other cases
        raise ValueError(
            '... is not allowed in exact_texts for "globbing"'
            'use _exact_texts_like condition instead'
        )

    actual_visible_texts: Query[Collection, List[str]] = Query(
        'visible texts',
        lambda collection: [
            webelement.text for webelement in collection() if webelement.is_displayed()
        ],
    )

    # flatten expected values and convert numbers to strings
    expected_flattened_stringified = [str(item) for item in helpers.flatten(expected)]
    return CollectionCondition.raise_if_not_actual(
        # TODO: should we use just expected here ↙ ?
        f'has exact texts {expected_flattened_stringified}',
        actual_visible_texts,
        predicate.equals_to_list(expected_flattened_stringified),
    )


# TODO: consider implementing a mixture of exact_texts and exact_texts_like
#       with syntax: exact_texts(1, 2, 3, 4) + exact_texts.like(1, ..., 4)
# def __exact_texts(
#     *expected: str | int | float | Iterable[str],
# ):
#     if ... in expected:  # TODO count other cases
#         raise ValueError(
#             '... is not allowed in exact_texts for "globbing"'
#             'use exact_texts._like condition instead'
#         )
#
#     actual_visible_texts: Query[Collection, List[str]] = Query(
#         'visible texts',
#         lambda collection: [
#             webelement.text for webelement in collection() if webelement.is_displayed()
#         ],
#     )
#
#     def build_raw_exact_texts(expected):
#         # flatten expected values and convert numbers to strings
#         expected_flattened_stringified = [
#             str(item) for item in helpers.flatten(expected)
#         ]
#         return CollectionCondition.raise_if_not_actual(
#             # TODO: should we use just expected here ↙ ?
#             f'has exact texts {expected_flattened_stringified}',
#             actual_visible_texts,
#             predicate.equals_to_list(expected_flattened_stringified),
#         )
#
#     class CollectionHasExactTextsWithGlobbing(CollectionCondition):
#
#         def _like(
#             self, *expected: str | int | float | Iterable
#         ) -> Condition[Collection]:
#             if ... not in expected:  # TODO: adapt to different types of blobs
#                 return build_raw_exact_texts(expected)
#
#             expected_pattern = re.sub(
#                 r'Ellipsis(,|\\])',
#                 r'.+?\1',
#                 (
#                     r'^'
#                     + re.escape(
#                         str(
#                             [
#                                 (str(item) if item is not ... else item)
#                                 for item in expected
#                             ]
#                         )
#                     )
#                     + r'$'
#                 ),
#             )
#
#             actual_visible_text: Query[Collection, str] = Query(
#                 'visible texts',
#                 lambda collection: str(actual_visible_texts(collection)),
#             )
#
#             return CollectionCondition.raise_if_not_actual(
#                 re.sub(
#                     r"'\.\.\.'([,\]])",
#                     r"...\1",
#                     f'has exact texts like {[value if value is not ... else r"..." for value in expected]}',
#                 ),
#                 actual_visible_text,
#                 predicate.matches(expected_pattern),
#             )
#
#     return CollectionHasExactTextsWithGlobbing(
#         str(build_raw_exact_texts(expected)),
#         build_raw_exact_texts(expected).call,
#     )


class _exact_texts_like(CollectionCondition):
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
        _negated=False,
        _globs: Tuple[Tuple[Any, str], ...] = (),
        _name_prefix: str = 'have',
        _name: str = 'exact texts like',
    ):  # noqa
        if self._MATCHING_SEPARATOR.__len__() != 1:
            raise ValueError('MATCHING_SEPARATOR should be a one character string')
        super().__init__(self.__str__, self.__call__)
        self._expected = expected
        self._negated = _negated
        self._globs = _globs if _globs else _exact_texts_like._DEFAULT_GLOBS
        self._name_prefix = _name_prefix
        self._name = _name
        # actually disabling any patterns, processing as a normal string
        self._process_patterns: Callable[[AnyStr], AnyStr] = (
            re.escape
        )  # HARDCODED by intent

    # @overload
    # def where(self, *globs: Tuple[Any, str]) -> _exact_texts_like: ...
    # """
    # Original idea was to give a possibility to customize globs in the most free way
    # by specifying both markers and patterns,
    # but it happened that implementation of matching logic is over-complicated
    # and tightly coupled with chosen patterns...
    # Thus, we removed this possibility for now, and the only way to customize globs
    # is to define markers per corresponding predefined pattern.
    # """
    # @overload
    # def where(
    #     self,
    #     *,
    #     exactly_one: Any = None,
    #     zero_or_one: Any = None,
    #     one_or_more: Any = None,
    #     zero_or_more: Any = None,
    # ) -> _exact_texts_like: ...
    # def where(self, *globs: Tuple[Any, str], **kwargs) -> _exact_texts_like:
    #     kwargs = cast(
    #         Dict[_exact_texts_like._PredefinedPatternType, Any],
    #         kwargs,
    #     )
    #     ... # here was actual original implementation

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
            _negated=self._negated,
            _globs=tuple(
                (glob_marker, self._PredefinedGlobPatterns[glob_pattern_type])
                for glob_pattern_type, glob_marker in kwargs.items()
            ),
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
            # see more exaplanation below...
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
            str(item)
            if item is not ''
            else _exact_texts_like._MATCHING_EMPTY_STRING_MARKER
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

        if not self._match(expected_pattern, actual_to_match):
            # TODO: implement pattern_explained
            #       probably after refactoring from tuple to dict as globs storage
            # pattern_explained = [
            #     next(...) if item in self._glob_markers else item
            #     for item in self._expected
            # ]
            raise AssertionError(
                f'actual visible texts:\n    {actual_to_render}\n'
                '\n'
                # f'Pattern explained:\n    {pattern_explained}\n'
                f'Pattern used for matching:\n    {expected_pattern}\n'
                f'Actual text used to match:\n    {actual_to_match}'
            )

    def __str__(self):
        return (
            f'{self._name_prefix} {"no " if self._negated else ""}{self._name}:\n    '
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

    # on subclassing this class, in case of new params to init
    # you have to ensure that such new params are counted in overriden not_
    @override
    @property
    def not_(self) -> Self:
        return self.__class__(
            *self._expected, _negated=not self._negated, _globs=self._globs
        )

    def _match(self, pattern, actual):
        answer = re.match(pattern, actual)
        return not answer if self._negated else answer

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
        _process_patterns: Callable[[AnyStr], AnyStr] = lambda item: item,
        _negated=False,
        _name_prefix='have',
        _name='text patterns like',
        # even though we don't customize globs in this class
        # the child classes can, so at least we have to pass through globs
        _globs=(),
    ):  # noqa
        super().__init__(
            *expected,
            _negated=_negated,
            _globs=_globs,
            _name_prefix=_name_prefix,
            _name=_name,
        )
        self._process_patterns = _process_patterns  # type: ignore


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
        _process_patterns: Callable[[AnyStr], AnyStr] = lambda item: item,
        _negated=False,
        _globs=(),  # just to match interface (will be actually skipped)
        _name_prefix='have',
        _name='text patterns',
    ):  # noqa
        super().__init__(
            *helpers.flatten(expected),  # TODO: document
            _process_patterns=_process_patterns,
            _negated=_negated,
            _name_prefix=_name_prefix,
            _name=_name,
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


class _texts_like(_text_patterns_like):
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
        _negated=False,
        _globs=(),
        _name_prefix='have',
        _name='texts like',
    ):
        def match_text_by_contains(item: str) -> str:
            return r'.*?' + re.escape(item) + r'.*?'

        super().__init__(
            *expected,
            _process_patterns=match_text_by_contains,
            _negated=_negated,
            _globs=_globs,  # just in case – passing through
            _name_prefix=_name_prefix,
            _name=_name,
        )

    @property
    def with_regex(self):
        """An alias to [_text_patterns_like][selene.match._text_patterns_like] condition
        : switches to regex matching mode for all items in the expected list"""
        return _text_patterns_like(
            *self._expected,
            _negated=self._negated,
            _globs=self._globs,
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

            # return re.escape(item).replace(r'\*', r'.*?').replace(r'\?', r'.')
            # return re.sub(
            #     re.escape(zero_or_more_chars),
            #     '.*?',
            #     re.sub(re.escape(exactly_one_char), '.', re.escape(item)),
            # )
            if zero_or_more_chars is None and exactly_one_char is None:
                return self._process_patterns(item)

            # return (
            #     re.escape(item)
            #     .replace(re.escape(zero_or_more_chars), r'.*?')
            #     .replace(re.escape(exactly_one_char), r'.')
            # )

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
            _negated=self._negated,
            _globs=self._globs,
            _name='texts with wildcards like',
        )


# # refactored to class
# def _texts_like(
#     *expected: str | int | float | Iterable,
# ):
#     def match_text_by_contains(item: str) -> str:
#         return r'.*?' + re.escape(item) + r'.*?'
#
#     return _text_patterns_like(*expected, _process_wildcards=match_text_by_contains)


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
) -> Condition[Browser]:
    def script_result(browser: Browser):
        return browser.driver.execute_script(script, *args)

    return BrowserCondition.raise_if_not_actual(
        f'has the ```{script}``` script returned {expected}',
        script_result,
        predicate.equals(expected),
    )
