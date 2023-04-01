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

from selenium.webdriver.common.by import By


def css(selector):
    return By.CSS_SELECTOR, selector


def xpath(selector):
    return By.XPATH, selector


def id(attribute_value):
    return By.ID, attribute_value


def class_name(value):
    return By.CLASS_NAME, value


def name(attribute_value):
    return By.NAME, attribute_value


def link_text(value):
    return By.LINK_TEXT, value


def partial_link_text(value):
    return By.PARTIAL_LINK_TEXT, value


def _escape_text_quotes_for_xpath(text):
    return 'concat("", "%s")' % (str("\", '\"', \"".join(text.split('"'))))


def text(value):
    return xpath(
        './/*[text()[normalize-space(.) = '
        + _escape_text_quotes_for_xpath(value)
        + ']]'
    )


def partial_text(value):
    return xpath(
        './/*[text()[contains(normalize-space(.), '
        + _escape_text_quotes_for_xpath(value)
        + ')]]'
    )


# TODO: deprecate be_* ? since they hide "xpath" logic, which may not be working in all cases
#       for example in case of mobile...
#       maybe the only good thing to keep is by.text and by.partial_text


def be_following_sibling(with_tag: str = '*'):
    warnings.warn(
        'deprecated; use xpath explicitly to not hide complexity in workaround',
        DeprecationWarning,
    )
    return xpath(f'./following-sibling::{with_tag}')


def be_parent():
    warnings.warn(
        'deprecated; use xpath explicitly to not hide complexity in workaround',
        DeprecationWarning,
    )
    return xpath('..')


def be_first_child(with_tag: str = '*'):
    warnings.warn(
        'deprecated; use xpath explicitly to not hide complexity in workaround',
        DeprecationWarning,
    )
    return xpath(f'./{with_tag}[1]')
