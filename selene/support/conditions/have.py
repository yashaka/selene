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

from selene import conditions


# *** Condition builders ***


def not_(condition_to_be_inverted):
    return conditions.not_(condition_to_be_inverted)


# *** SeleneElement conditions ***


def exact_text(value):
    return conditions.exact_text(value)


def text(partial_value):
    return conditions.text(partial_value)


def attribute(name, value):
    return conditions.attribute(name, value)


def value(val):
    return conditions.value(val)


def css_class(name):
    return conditions.css_class(name)


# *** SeleneCollection conditions ***


def size(size_of_collection):
    return conditions.size(size_of_collection)


def size_at_least(minimum_size_of_collection):
    return conditions.size_at_least(minimum_size_of_collection)


def size_greater_than_or_equal(minimum_size_of_collection):
    return conditions.size_at_least(minimum_size_of_collection)


def exact_texts(*values):
    return conditions.exact_texts(*values)


def texts(*partial_values):
    return conditions.texts(*partial_values)


# *** WebDriver conditions ***


def js_returned_true(script_to_return_bool):
    return conditions.JsReturnedTrue(script_to_return_bool)


def title(exact_value):
    return conditions.Title(exact_value)


def title_containing(partial_value):
    return conditions.TitleContaining(partial_value)


def url(exact_value):
    return conditions.Url(exact_value)


def url_containing(partial_value):
    return conditions.UrlContaining(partial_value)
