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
import warnings
from typing import Any, Union, Iterable, Optional

from selene.core import match
from selene.core.condition import Condition
from selene.core.entity import Element, Collection
from selene.core._browser import Browser
from selene.support.conditions import not_ as _not_

no = _not_


def exact_text(value: str | int | float):
    return match.exact_text(value)


# TODO: consider accepting int
def text(partial_value: str | int | float):
    return match.text(partial_value)


def text_matching(regex_pattern: str):
    return match.text_pattern(regex_pattern)


# TODO: should we use here js.property style (and below for js.returned(...))
def js_property(name: str, value: Optional[str] = None):
    if value:
        warnings.warn(
            'passing second argument is deprecated; use have.js_property(foo).value(bar) instead',
            DeprecationWarning,
        )
        return match.element_has_js_property(name).value(value)

    return match.element_has_js_property(name)


def css_property(name: str, value: Optional[str] = None):
    if value:
        warnings.warn(
            'passing second argument is deprecated; use have.css_property(foo).value(bar) instead',
            DeprecationWarning,
        )
        return match.element_has_css_property(name).value(value)

    return match.element_has_css_property(name)


def attribute(name: str, value: Optional[str] = None):
    if value:
        warnings.warn(
            'passing second argument is deprecated; use have.attribute(foo).value(bar) instead',
            DeprecationWarning,
        )
        return match.element_has_attribute(name).value(value)

    return match.element_has_attribute(name)


def value(text: str | int | float) -> Condition[Element]:
    return match.element_has_value(text)


def values(*texts: str | int | float | Iterable[str]) -> Condition[Collection]:
    return match.collection_has_values(*texts)


def value_containing(partial_text: str | int | float) -> Condition[Element]:
    return match.element_has_value_containing(partial_text)


def values_containing(
    *partial_texts: str | int | float | Iterable[str],
) -> Condition[Collection]:
    return match.collection_has_values_containing(*partial_texts)


def css_class(name) -> Condition[Element]:
    return match.element_has_css_class(name)


def tag(name: str) -> Condition[Element]:
    return match.element_has_tag(name)


def tag_containing(name: str) -> Condition[Element]:
    return match.element_has_tag_containing(name)


# *** SeleneCollection conditions ***


def size(number: int) -> Condition[Collection]:
    return match.collection_has_size(number)


def size_less_than(number: int) -> Condition[Collection]:
    return match.collection_has_size_less_than(number)


def size_less_than_or_equal(number: int) -> Condition[Collection]:
    return match.collection_has_size_less_than_or_equal(number)


def size_greater_than(number: int) -> Condition[Collection]:
    return match.collection_has_size_greater_than(number)


def size_at_least(number: int) -> Condition[Collection]:
    warnings.warn(
        'might be deprecated; use have.size_greater_than_or_equal instead',
        PendingDeprecationWarning,
    )
    return match.collection_has_size_greater_than_or_equal(number)


def size_greater_than_or_equal(number: int) -> Condition[Collection]:
    return match.collection_has_size_greater_than_or_equal(number)


# TODO: consider accepting ints
def texts(*partial_values: str | int | float | Iterable[str]):
    return match.texts(*partial_values)


def exact_texts(*values: str | int | float | Iterable[str]):
    return match.exact_texts(*values)


def _exact_texts_like(*texts_or_item_placeholders: str | int | float | Iterable):
    """List-globbing version of
    [have.exact_texts(*texts)][selene.support.conditions.have.exact_texts]
    allowing to use item placeholders instead of text items.

    Default list globbing placeholders are:

    - `[...]` matches **zero or one** item of any text in the list
    - `...` matches **exactly one** item of any text in the list
    - `(...,)` matches one **or more** items of any text in the list
    - `[(...,)]` matches **zero** or more items of any text in the list

    Placeholders can be overridden in the following manner:
    `have._texts_like(*text_items_or_placeholders).where(**placeholders_to_override)`

    Nested lists with text items for better formatting of expected texts –
    are not supported, unlike in `have.exact_texts(*items)`,
    because list literals are used as placeholders for list globbing."""
    return match._exact_texts_like(*texts_or_item_placeholders)


# could be named as texts_matching_like
# but seems like "matching like" confuses too much...
# yet, we want to keep _like suffix
# as identifier of "globbing" nature of the list match
def _text_patterns_like(
    *regex_patterns_or_item_placeholders: str | int | float | Iterable,
):
    """List-globbing version of
    [have.texts_matching(*regex_patterns)][selene.support.conditions.have.texts_matching]
    allowing to use item placeholders instead of text items.

    Default list globbing placeholders are:

    - `[...]` matches **zero or one** item of any text in the list
    - `...` matches **exactly one** item of any text in the list
    - `(...,)` matches one **or more** items of any text in the list
    - `[(...,)]` matches **zero** or more items of any text in the list

    Placeholders can be overridden in the following manner:
    `have._texts_like(*text_items_or_placeholders).where(**placeholders_to_override)`

    !!! warning

        Nested lists with text items for better formatting of expected texts –
        are not supported,
        unlike in [`have.texts(*texts)`][selene.support.conditions.have.texts],
        because list literals are used as placeholders for list globbing.

    !!! warning

        Unlike in [`have.texts_matching(*regex_patterns)`][selene.support.conditions.have.texts_matching],
        regex patterns for this condition
        can't use `^` (start of text) and `$` (end of text),
        because they are implicit as a result of merging for globbing implementation,
        and if added explicitly will break the match.
    """
    return match._text_patterns_like(*regex_patterns_or_item_placeholders)


def texts_matching(*regex_patterns: str | int | float | Iterable):
    """Regex version of [have.texts(*partial_values)][selene.support.conditions.have.texts]
    allowing to use regex patterns instead of text items matched by contains.
    """
    return match._text_patterns(*regex_patterns)


def _texts_like(*contained_texts_or_item_placeholders: str | int | float | Iterable):
    """List-globbing version of [have.texts(*partial_values)][selene.support.conditions.have.texts]
    allowing to use item placeholders instead of text items.

    Default list globbing placeholders are:

    - `[...]` matches **zero or one** item of any text in the list
    - `...` matches **exactly one** item of any text in the list
    - `(...,)` matches one **or more** items of any text in the list
    - `[(...,)]` matches **zero** or more items of any text in the list

    Placeholders can be overridden in the following manner:
    `have._texts_like(*text_items_or_placeholders).where(**placeholders_to_override)`

    !!! warning

        Nested lists with text items for better formatting of expected texts –
        are not supported, unlike in
        [`have.texts(*texts)`][selene.support.conditions.have.texts],
        because list literals are used as placeholders for list globbing.

    Text items are matched by contains, but can be matched by regex patterns
    if modified via `.with_regex` property making the actual signature be equivalent to
    `have._texts_like(*regex_patterns_or_item_placeholders).with_regex`.
    Actually calling `.with_regex` just forward implementation to
    [have._text_patterns_like(*regex_patterns_or_item_placeholders)][selene.support.conditions.have._text_patterns_like].

    !!! warning

        Unlike in [`have.texts_matching(*regex_patterns)`][selene.support.conditions.have.texts_matching],
        Regex patterns can't use `^` (start of text) and `$` (end of text)
        because they are implicit, and if added explicitly will break the match.

    If modified via `.with_wildcards`
    then switch regex to wildcards-based pattern matching,
    making the actual signature be equivalent to:
    `have._texts_like(*texts_with_wildcards_or_item_placeholders).with_wildcards`
    or
    `have._texts_like(*texts_with_wildcards_or_item_placeholders).where_wildcards(**to_override)`

    Supported wildcards can be overridden and defaults are:

    - `*` matches **zero or more** of any characters in a text item
    - `?` matches **exactly one** of any character in a text item
    """
    return match._texts_like(*contained_texts_or_item_placeholders)


def url(exact_value: str) -> Condition[Browser]:
    return match.browser_has_url(exact_value)


def url_containing(partial_value: str) -> Condition[Browser]:
    return match.browser_has_url_containing(partial_value)


def title(exact_value: str) -> Condition[Browser]:
    return match.browser_has_title(exact_value)


def title_containing(partial_value: str) -> Condition[Browser]:
    return match.browser_has_title_containing(partial_value)


def tabs_number(value: int) -> Condition[Browser]:
    return match.browser_has_tabs_number(value)


def tabs_number_less_than(value: int) -> Condition[Browser]:
    return match.browser_has_tabs_number_less_than(value)


def tabs_number_less_than_or_equal(value: int) -> Condition[Browser]:
    return match.browser_has_tabs_number_less_than_or_equal(value)


def tabs_number_greater_than(value: int) -> Condition[Browser]:
    return match.browser_has_tabs_number_greater_than(value)


def tabs_number_greater_than_or_equal(value: int) -> Condition[Browser]:
    return match.browser_has_tabs_number_greater_than_or_equal(value)


def js_returned_true(script_to_return_bool: str) -> Condition[Browser]:
    warnings.warn(
        'deprecated; use have.script_returned(True, ...) instead',
        DeprecationWarning,
    )
    return match.browser_has_script_returned(True, script_to_return_bool)


def js_returned(expected: Any, script: str, *args) -> Condition[Browser]:
    warnings.warn(
        'deprecated because js does not work for mobile; '
        'use have.script_returned(True, ...) instead',
        DeprecationWarning,
    )
    return match.browser_has_script_returned(expected, script, *args)


def script_returned(expected: Any, script: str, *args) -> Condition[Browser]:
    return match.browser_has_script_returned(expected, script, *args)
