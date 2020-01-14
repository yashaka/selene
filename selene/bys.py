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

from selenium.webdriver.common.by import By

__author__ = 'yashaka'


def by(css_selector):
    return by_css(css_selector)


def by_css(css_selector):
    return (By.CSS_SELECTOR, css_selector)


def by_id(name):
    return (By.ID, name)


def by_name(name):
    return (By.NAME, name)


def by_link_text(text):
    return (By.LINK_TEXT, text)


def by_partial_link_text(text):
    return (By.PARTIAL_LINK_TEXT, text)


def by_xpath(xpath):
    return (By.XPATH, xpath)


def following_sibling():
    return by_xpath("./following-sibling::*")


def parent():
    return by_xpath("..")


def first_child():
    return by_xpath("./*[1]")


def by_text(element_text):
    return by_xpath('.//*[text()[normalize-space(.) = '
                    + escape_text_quotes_for_xpath(element_text)
                    + ']]')


def by_partial_text(element_text):
    return by_xpath('.//*[text()[contains(normalize-space(.), '
                    + escape_text_quotes_for_xpath(element_text)
                    + ')]]')


with_text = by_partial_text


def escape_text_quotes_for_xpath(text):
    return 'concat("", "%s")' % (
        str(
            "\", '\"', \"".join(
                text.split('"'))))
