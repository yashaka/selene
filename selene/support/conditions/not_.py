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
import warnings
from typing import Any

from selene.core import match as _match

# --- be.* conditions --- #
from selene.core.condition import Condition
from selene.core.entity import Element, Collection, Browser

# TODO: consider refactoring to class for better extendability
#       when creating custom conditions

visible: Condition[Element] = _match.element_is_visible.not_
hidden: Condition[Element] = _match.element_is_hidden.not_

present: Condition[Element] = _match.element_is_present.not_
in_dom: Condition[Element] = _match.element_is_present.not_
# TODO: do we need both present and in_dom?
# TODO: consider deprecating existing
existing: Condition[Element] = _match.element_is_present.not_

absent: Condition[Element] = _match.element_is_absent.not_

enabled: Condition[Element] = _match.element_is_enabled.not_
disabled: Condition[Element] = _match.element_is_disabled.not_

blank: Condition[Element] = _match.element_is_blank.not_


# --- have.* conditions --- #


def exact_text(value) -> Condition[Element]:
    return _match.element_has_exact_text(value).not_


# TODO: consider accepting int
def text(partial_value) -> Condition[Element]:
    return _match.element_has_text(partial_value).not_


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

    def value(self, expected: str, ignore_case=False) -> Condition[Element]:
        return original.value(expected, ignore_case).not_

    def value_containing(self, expected: str, ignore_case=False) -> Condition[Element]:
        return original.value_containing(expected, ignore_case).not_

    def values(self, *expected: str) -> Condition[Collection]:
        return original.values(*expected).not_

    def values_containing(self, *expected: str) -> Condition[Collection]:
        return original.values_containing(*expected).not_

    negated.value = value
    negated.value_containing = value_containing
    negated.values = values
    negated.values_containing = values_containing

    return negated


def js_property(name: str, *args, **kwargs):
    if args or 'value' in kwargs:
        warnings.warn(
            'passing second argument is deprecated; '
            'use have.js_property(foo).value(bar) instead',
            DeprecationWarning,
        )
        return (
            _match.element_has_js_property(name)
            .value(args[0] if args else kwargs['value'])
            .not_
        )

    original = _match.element_has_js_property(name)
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


def value(text) -> Condition[Element]:
    return _match.element_has_value(text).not_


def value_containing(partial_text) -> Condition[Element]:
    return _match.element_has_value_containing(partial_text).not_


def css_class(name) -> Condition[Element]:
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


# TODO: consider accepting ints
def texts(*partial_values: str) -> Condition[Collection]:
    return _match.collection_has_texts(*partial_values).not_


def exact_texts(*values: str) -> Condition[Collection]:
    return _match.collection_has_exact_texts(*values).not_


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
