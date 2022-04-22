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
from typing import Union

from selene.core.entity import Element, Collection
from selene.support.shared import browser


def s(css_or_xpath_or_by: Union[str, tuple]) -> Element:
    warnings.warn(
        'selene.support.jquery_style_selectors.s is deprecated; '
        'use selene.support.shared.jquery_style.s instead',
        DeprecationWarning,
    )
    return browser.element(css_or_xpath_or_by)


def ss(css_or_xpath_or_by: Union[str, tuple]) -> Collection:
    warnings.warn(
        'selene.support.jquery_style_selectors.ss is deprecated; '
        'use selene.support.shared.jquery_style.ss instead',
        DeprecationWarning,
    )
    return browser.all(css_or_xpath_or_by)
