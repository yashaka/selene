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
import warnings
from typing import Any

from selene.core import match
from selene.support.conditions import not_ as _not_

no = _not_

def exact_text(value) -> match.ElementCondition:
    return match.element_has_exact_text(value)


# todo: consider accepting int
def text(partial_value) -> match.ElementCondition:
    return match.element_has_text(partial_value)


# todo: should we use here js.property style (and below for js.returned(...))
def js_property(name: str, value: str = None):
    if value:
        warnings.warn(
            'passing second argument is deprecated; use have.js_property(foo).value(bar) instead',
            DeprecationWarning)
        return match.element_has_js_property(name).value(value)

    return match.element_has_js_property(name)


def css_property(name: str, value: str = None):
    if value:
        warnings.warn(
            'passing second argument is deprecated; use have.css_property(foo).value(bar) instead',
            DeprecationWarning)
        return match.element_has_css_property(name).value(value)

    return match.element_has_css_property(name)


def attribute(name: str, value: str = None):
    if value:
        warnings.warn(
            'passing second argument is deprecated; use have.attribute(foo).value(bar) instead',
            DeprecationWarning)
        return match.element_has_attribute(name).value(value)

    return match.element_has_attribute(name)


def value(text) -> match.ElementCondition:
    return match.element_has_value(text)


def value_containing(partial_text) -> match.ElementCondition:
    return match.element_has_value_containing(partial_text)


def css_class(name) -> match.ElementCondition:
    return match.element_has_css_class(name)


def tag(name: str) -> match.ElementCondition:
    return match.element_has_tag(name)


def tag_containing(name: str) -> match.ElementCondition:
    return match.element_has_tag_containing(name)


# *** SeleneCollection conditions ***


def size(number: int) -> match.CollectionCondition:
    return match.collection_has_size(number)


def size_less_than(number: int) -> match.CollectionCondition:
    return match.collection_has_size_less_than(number)


def size_less_than_or_equal(number: int) -> match.CollectionCondition:
    return match.collection_has_size_less_than_or_equal(number)


def size_greater_than(number: int) -> match.CollectionCondition:
    return match.collection_has_size_greater_than(number)


def size_at_least(number: int) -> match.CollectionCondition:
    warnings.warn('might be deprecated; use have.size_greater_than_or_equal instead', PendingDeprecationWarning)
    return match.collection_has_size_greater_than_or_equal(number)


def size_greater_than_or_equal(number: int) -> match.CollectionCondition:
    return match.collection_has_size_greater_than_or_equal(number)


# todo: consider accepting ints
def texts(*partial_values: str) -> match.CollectionCondition:
    return match.collection_has_texts(*partial_values)


def exact_texts(*values: str) -> match.CollectionCondition:
    return match.collection_has_exact_texts(*values)


def url(exact_value: str) -> match.BrowserCondition:
    return match.browser_has_url(exact_value)


def url_containing(partial_value: str) -> match.BrowserCondition:
    return match.browser_has_url_containing(partial_value)


def title(exact_value: str) -> match.BrowserCondition:
    return match.browser_has_title(exact_value)


def title_containing(partial_value: str) -> match.BrowserCondition:
    return match.browser_has_title_containing(partial_value)


def tabs_number(value: int) -> match.BrowserCondition:
    return match.browser_has_tabs_number(value)


def tabs_number_less_than(value: int) -> match.BrowserCondition:
    return match.browser_has_tabs_number_less_than(value)


def tabs_number_less_than_or_equal(value: int) -> match.BrowserCondition:
    return match.browser_has_tabs_number_less_than_or_equal(value)


def tabs_number_greater_than(value: int) -> match.BrowserCondition:
    return match.browser_has_tabs_number_greater_than(value)


def tabs_number_greater_than_or_equal(value: int) -> match.BrowserCondition:
    return match.browser_has_tabs_number_greater_than_or_equal(value)


def js_returned_true(script_to_return_bool: str) -> match.BrowserCondition:
    warnings.warn('might be deprecated; use have.js_returned(True, ...) instead', PendingDeprecationWarning)
    return match.browser_has_js_returned(True, script_to_return_bool)


def js_returned(expected: Any, script: str, *args) -> match.BrowserCondition:
    return match.browser_has_js_returned(expected, script, *args)
