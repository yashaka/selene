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
from typing import Any, Iterable

from selene.core import match as _match

# TODO:  consider breaking into be_not.* and have_no.*
#        then, it can be implemented inside be.* and have.* (if utilizing classes)

# --- be.not_.* conditions --- #
from selene.core.condition import Condition
from selene.core.entity import Element, Collection
from selene.core._browser import Browser

# TODO: consider refactoring to class for better extendability
#       when creating custom conditions

visible: Condition[Element] = _match.visible.not_
hidden: Condition[Element] = _match.hidden.not_
hidden_in_dom: Condition[Element] = _match.hidden_in_dom.not_

present_in_dom: Condition[Element] = _match.present_in_dom.not_
absent_in_dom: Condition[Element] = _match.absent_in_dom.not_
in_dom: Condition[Element] = _match.present_in_dom.not_


enabled: Condition[Element] = _match.enabled.not_
disabled: Condition[Element] = _match.disabled.not_

selected: Condition[Element] = _match.selected.not_

# focused: Condition[Element] = _match.focused.not_

blank: Condition[Element] = _match.element_is_blank.not_

# --- be.not_.* DEPRECATED conditions --- #

present: Condition[Element] = _match.present_in_dom.not_
"""Deprecated 'is not present' condition. Use not_.present_in_dom instead."""

existing: Condition[Element] = _match.present_in_dom.not_
"""Deprecated 'is not existing' condition. Use not_.present_in_dom instead."""

absent: Condition[Element] = _match.absent_in_dom.not_
"""Deprecated 'is not absent' condition. Use not_.absent_in_dom instead."""


# --- have.* conditions --- #


def exact_text(value: str | int | float):
    return _match.exact_text(value, _inverted=True)


def text(partial_value: str | int | float):
    return _match.text(partial_value, _inverted=True)


def text_matching(regex_pattern: str):
    return _match.text_pattern(regex_pattern, _inverted=True)


def attribute(name: str, *args, **kwargs):
    if args or 'value' in kwargs:
        warnings.warn(
            'passing second argument is deprecated; '
            'use have.attribute(foo).value(bar) instead',
            DeprecationWarning,
        )
        return (
            _match.element_has_attribute(name)
            .value(args[0] if args else kwargs['value'])
            .not_
        )

    original = _match.element_has_attribute(name)
    negated = original.not_

    def value(
        self, expected: str | int | float, ignore_case=False
    ) -> Condition[Element]:
        return original.value(expected, ignore_case).not_

    def value_containing(
        self, expected: str | int | float, ignore_case=False
    ) -> Condition[Element]:
        return original.value_containing(expected, ignore_case).not_

    def values(self, *expected: str | int | float) -> Condition[Collection]:
        return original.values(*expected).not_

    def values_containing(self, *expected: str | int | float) -> Condition[Collection]:
        return original.values_containing(*expected).not_

    negated.value = value
    negated.value_containing = value_containing
    negated.values = values
    negated.values_containing = values_containing

    return negated


def js_property(name: str, *args, **kwargs):
    warnings.warn('deprecated; use have.no.property instead', DeprecationWarning)
    return property_(name, *args, **kwargs)


def property_(name: str, *args, **kwargs):
    if args or 'value' in kwargs:
        warnings.warn(
            'passing second argument is deprecated; '
            'use have.property(foo).value(bar) instead',
            DeprecationWarning,
        )
        return (
            _match.native_property(name)
            .value(args[0] if args else kwargs['value'])
            .not_
        )

    original = _match.native_property(name)
    negated = original.not_

    def value(self, expected: str | int | float) -> Condition[Element]:
        return original.value(expected).not_

    def value_containing(self, expected: str | int | float) -> Condition[Element]:
        return original.value_containing(expected).not_

    def values(
        self, *expected: str | int | float | Iterable[str]
    ) -> Condition[Collection]:
        return original.values(*expected).not_

    def values_containing(
        self, *expected: str | int | float | Iterable[str]
    ) -> Condition[Collection]:
        return original.values_containing(*expected).not_

    negated.value = value
    negated.value_containing = value_containing
    negated.values = values
    negated.values_containing = values_containing

    return negated


def css_property(name: str, *args, **kwargs):
    if args or 'value' in kwargs:
        warnings.warn(
            'passing second argument is deprecated; '
            'use have.css_property(foo).value(bar) instead',
            DeprecationWarning,
        )
        return (
            _match.element_has_css_property(name)
            .value(args[0] if args else kwargs['value'])
            .not_
        )

    original = _match.element_has_css_property(name)
    negated = original.not_

    def value(self, expected: str) -> Condition[Element]:
        return original.value(expected).not_

    def value_containing(self, expected: str) -> Condition[Element]:
        return original.value_containing(expected).not_

    def values(self, *expected: str) -> Condition[Collection]:
        return original.values(*expected).not_

    def values_containing(self, *expected: str) -> Condition[Collection]:
        return original.values_containing(*expected).not_

    negated.value = value
    negated.value_containing = value_containing
    negated.values = values
    negated.values_containing = values_containing

    return negated


def value(text: str | int | float) -> Condition[Element]:
    return _match.element_has_value(text).not_


def value_containing(partial_text: str | int | float) -> Condition[Element]:
    return _match.element_has_value_containing(partial_text).not_


def css_class(name: str) -> Condition[Element]:
    return _match.element_has_css_class(name).not_


def tag(name: str) -> Condition[Element]:
    return _match.element_has_tag(name).not_


def tag_containing(name: str) -> Condition[Element]:
    return _match.element_has_tag_containing(name).not_


# *** SeleneCollection conditions ***


def size(number: int) -> Condition[Collection]:
    return _match.collection_has_size(number).not_


def size_less_than(number: int) -> Condition[Collection]:
    return _match.collection_has_size_less_than(number).not_


def size_less_than_or_equal(number: int) -> Condition[Collection]:
    return _match.collection_has_size_less_than_or_equal(number).not_


def size_greater_than(number: int) -> Condition[Collection]:
    return _match.collection_has_size_greater_than(number).not_


def size_at_least(number: int) -> Condition[Collection]:
    warnings.warn(
        'might be deprecated; use have.size_greater_than_or_equal instead',
        PendingDeprecationWarning,
    )
    return _match.collection_has_size_greater_than_or_equal(number).not_


def size_greater_than_or_equal(number: int) -> Condition[Collection]:
    return _match.collection_has_size_greater_than_or_equal(number).not_


def texts(*partial_values: str | int | float | Iterable[str]):
    return _match.texts(*partial_values, _inverted=True)


def exact_texts(*values: str | int | float | Iterable[str]):
    return _match.exact_texts(*values, _inverted=True)


def _exact_texts_like(*texts_or_item_placeholders: str | int | float | Iterable):
    return _match._exact_texts_like(*texts_or_item_placeholders, _inverted=True)


def _text_patterns_like(
    *regex_patterns_or_item_placeholders: str | int | float | Iterable,
):
    return _match._text_patterns_like(
        *regex_patterns_or_item_placeholders, _inverted=True
    )


def _texts_matching(*regex_patterns: str | int | float | Iterable):
    return _match._text_patterns(*regex_patterns, _inverted=True)


def _texts_like(*contained_texts_or_item_placeholders: str | int | float | Iterable):
    return _match._texts_like(*contained_texts_or_item_placeholders, _inverted=True)


def url(exact_value: str) -> Condition[Browser]:
    return _match.browser_has_url(exact_value).not_


def url_containing(partial_value: str) -> Condition[Browser]:
    return _match.browser_has_url_containing(partial_value).not_


def title(exact_value: str) -> Condition[Browser]:
    return _match.browser_has_title(exact_value).not_


def title_containing(partial_value: str) -> Condition[Browser]:
    return _match.browser_has_title_containing(partial_value).not_


def tabs_number(value: int) -> Condition[Browser]:
    return _match.browser_has_tabs_number(value).not_


def tabs_number_less_than(value: int) -> Condition[Browser]:
    return _match.browser_has_tabs_number_less_than(value).not_


def tabs_number_less_than_or_equal(value: int) -> Condition[Browser]:
    return _match.browser_has_tabs_number_less_than_or_equal(value).not_


def tabs_number_greater_than(value: int) -> Condition[Browser]:
    return _match.browser_has_tabs_number_greater_than(value).not_


def tabs_number_greater_than_or_equal(value: int) -> Condition[Browser]:
    return _match.browser_has_tabs_number_greater_than_or_equal(value).not_


def js_returned_true(script_to_return_bool: str) -> Condition[Browser]:
    warnings.warn(
        'might be deprecated; use have.js_returned(True, ...) instead',
        PendingDeprecationWarning,
    )
    return _match.browser_has_js_returned(True, script_to_return_bool).not_


def js_returned(expected: Any, script: str, *args) -> Condition[Browser]:
    return _match.browser_has_js_returned(expected, script, *args).not_


def script_returned(expected: Any, script: str, *args) -> Condition[Browser]:
    return _match.browser_has_script_returned(expected, script, *args).not_
