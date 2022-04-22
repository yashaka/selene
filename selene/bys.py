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


def by(css_selector):
    warnings.warn(
        'deprecated; use by.* from selene.support.by', DeprecationWarning
    )
    return by_css(css_selector)


def by_css(css_selector):
    warnings.warn(
        'deprecated; use by.* from selene.support.by', DeprecationWarning
    )
    return (By.CSS_SELECTOR, css_selector)


def by_id(name):
    warnings.warn(
        'deprecated; use by.* from selene.support.by', DeprecationWarning
    )
    return (By.ID, name)


def by_name(name):
    warnings.warn(
        'deprecated; use by.* from selene.support.by', DeprecationWarning
    )
    return (By.NAME, name)


def by_link_text(text):
    warnings.warn(
        'deprecated; use by.* from selene.support.by', DeprecationWarning
    )
    return (By.LINK_TEXT, text)


def by_partial_link_text(text):
    warnings.warn(
        'deprecated; use by.* from selene.support.by', DeprecationWarning
    )
    return (By.PARTIAL_LINK_TEXT, text)


def by_xpath(xpath):
    warnings.warn(
        'deprecated; use by.* from selene.support.by', DeprecationWarning
    )
    return (By.XPATH, xpath)


def following_sibling():
    warnings.warn(
        'deprecated; use by.* from selene.support.by', DeprecationWarning
    )
    return by_xpath("./following-sibling::*")


def parent():
    warnings.warn(
        'deprecated; use by.* from selene.support.by', DeprecationWarning
    )
    return by_xpath("..")


def first_child():
    warnings.warn(
        'deprecated; use by.* from selene.support.by', DeprecationWarning
    )
    return by_xpath("./*[1]")


def by_text(element_text):
    warnings.warn(
        'deprecated; use by.* from selene.support.by', DeprecationWarning
    )
    return by_xpath(
        './/*[text()[normalize-space(.) = '
        + escape_text_quotes_for_xpath(element_text)
        + ']]'
    )


def by_partial_text(element_text):
    warnings.warn(
        'deprecated; use by.* from selene.support.by', DeprecationWarning
    )
    return by_xpath(
        './/*[text()[contains(normalize-space(.), '
        + escape_text_quotes_for_xpath(element_text)
        + ')]]'
    )


def with_text(element_text):
    warnings.warn(
        'deprecated; use by.* from selene.support.by', DeprecationWarning
    )
    return by_partial_text(element_text)


def escape_text_quotes_for_xpath(text):
    warnings.warn(
        'deprecated; use by.* from selene.support.by', DeprecationWarning
    )
    return 'concat("", "%s")' % (str("\", '\"', \"".join(text.split('"'))))
