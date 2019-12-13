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
import warnings
from typing import Any

from selene import match
from selene.entity import Browser, SeleneCollection, SeleneElement
from selene.condition import Condition
from selene.support.past import conditions  # todo: remove


# todo: provide something like the following from selenidejs:
#     export const no = new Proxy(have, {
#         get: (have, conditionName) => (...args) => Condition.not(have[conditionName](...args))
#     });


def exact_text(value) -> Condition[SeleneElement]:
    return match.element_has_exact_text(value)


# todo: consider accepting int
def text(partial_value) -> Condition[SeleneElement]:
    return match.element_has_text(partial_value)


def attribute(name: str, value: str = None) -> Condition[SeleneElement]:
    if value:
        warnings.warn(
            'passing second argument is deprecated; use have.attribute(foo).value(bar) instead',
            DeprecationWarning)
        return match.element_has_attribute(name).value(value)

    return match.element_has_attribute(name)


def value(text) -> Condition[SeleneElement]:
    return match.element_has_value(text)


def value_containing(partial_text) -> Condition[SeleneElement]:
    return match.element_has_value_containing(partial_text)


def css_class(name) -> Condition[SeleneElement]:
    return match.element_has_css_class(name)


# *** SeleneCollection conditions ***


def size(number: int) -> Condition[SeleneCollection]:
    return match.collection_has_size(number)


def size_less_than(number: int) -> Condition[SeleneCollection]:
    return match.collection_has_size_less_than(number)


def size_less_than_or_equal(number: int) -> Condition[SeleneCollection]:
    return match.collection_has_size_less_than_or_equal(number)


def size_greater_than(number: int) -> Condition[SeleneCollection]:
    return match.collection_has_size_greater_than(number)


def size_at_least(number: int) -> Condition[SeleneCollection]:
    warnings.warn('might be deprecated; use have.size_greater_than_or_equal instead', PendingDeprecationWarning)
    return match.collection_has_size_greater_than_or_equal(number)


def size_greater_than_or_equal(number: int) -> Condition[SeleneCollection]:
    return match.collection_has_size_greater_than_or_equal(number)


# todo: consider accepting ints
def texts(*partial_values: str) -> Condition[SeleneCollection]:
    return match.collection_has_texts(*partial_values)


def exact_texts(*values: str) -> Condition[SeleneCollection]:
    return match.collection_has_exact_texts(*values)


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
    warnings.warn('might be deprecated; use have.js_returned(True, ...) instead', PendingDeprecationWarning)
    return match.browser_has_js_returned(True, script_to_return_bool)


def js_returned(expected: Any, script: str, *args) -> Condition[Browser]:
    return match.browser_has_js_returned(expected, script, *args)


# --- Deprecated --- #


def not_(condition_to_be_inverted):
    warnings.warn('might be deprecated; use Condition.as_not instead', PendingDeprecationWarning)
    return Condition.as_not(condition_to_be_inverted)
