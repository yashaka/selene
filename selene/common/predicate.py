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

import re


def is_truthy(something):
    return bool(something) if not something == '' else True


def equals_ignoring_case(expected):
    return lambda actual: str(expected).lower() == str(actual).lower()


def equals(expected, ignore_case=False):
    return (
        lambda actual: expected == actual
        if not ignore_case
        else equals_ignoring_case(expected)
    )


def is_greater_than(expected):
    return lambda actual: actual > expected


def is_greater_than_or_equal(expected):
    return lambda actual: actual >= expected


def is_less_than(expected):
    return lambda actual: actual < expected


def is_less_than_or_equal(expected):
    return lambda actual: actual <= expected


def includes_ignoring_case(expected):
    return lambda actual: str(expected).lower() in str(actual).lower()


def includes(expected, ignore_case=False):
    def fn(actual):
        try:
            return (
                expected in actual
                if not ignore_case
                else includes_ignoring_case(expected)
            )
        except TypeError:
            return False

    return fn


def includes_word_ignoring_case(expected):
    return lambda actual: str(expected).lower() in re.split(r'\s+', str(actual).lower())


def includes_word(expected, ignore_case=False):
    return (
        lambda actual: expected in re.split(r'\s+', actual)
        if not ignore_case
        else includes_ignoring_case(expected)
    )


# will not work with empty seqs :( TODO: fix
# currently we use it only for non-empty seqs taking this into account
seq_compare_by = (
    lambda f: lambda x=None, *xs: lambda y=None, *ys: True
    if x is None and y is None
    else bool(f(x)(y)) and seq_compare_by(f)(*xs)(*ys)  # type: ignore
)


# def seq_compare_by_2(f):
#     def fn(x, *xs):
#         def fn(y, *ys):
#             return True if x is None and y is None else \
#                 bool(f(x)(y)) and seq_compare_by(f)(*xs or (None, ))(*ys or (None, ))
#         return fn
#     return fn


list_compare_by = lambda f: lambda expected: lambda actual: (
    seq_compare_by(f)(*expected)(*actual)
)


# list_compare_by = lambda f: lambda expected: lambda actual: \
#     seq_compare_by(f)(* expected if expected else (None,))(* actual if actual else (None, ))


equals_to_list = list_compare_by(equals)
equals_by_contains_to_list = list_compare_by(includes)
