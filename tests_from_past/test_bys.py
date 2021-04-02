# MIT License
#
# Copyright (c) 2015-2021 Iakiv Kramarenko
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

from selene.bys import (
    by,
    by_css,
    by_name,
    by_link_text,
    by_partial_link_text,
    by_xpath,
    following_sibling,
    parent,
    first_child,
    by_text,
    by_partial_text,
    escape_text_quotes_for_xpath,
)


def test_by_css():
    assert by("a") == ('css selector', 'a')
    assert by_css("span") == ('css selector', 'span')


def test_by_name():
    assert by_name("test") == ('name', 'test')


def test_by_link_text():
    assert by_link_text("text") == ('link text', 'text')


def test_by_partial_link_text():
    assert by_partial_link_text("text") == ("partial link text", "text")


def test_by_xpath():
    assert by_xpath("//a") == ('xpath', "//a")


def test_by_following_sibling():
    assert following_sibling() == ("xpath", './following-sibling::*')


def test_by_parent():
    assert parent() == ("xpath", "..")


def test_first_child():
    assert first_child() == ("xpath", "./*[1]")


def test_by_text():
    assert by_text("test") == (
        "xpath",
        './/*[text()[normalize-space(.) = concat("", "test")]]',
    )


def test_by_partial_text():
    assert by_partial_text("text") == (
        "xpath",
        './/*[text()[contains(normalize-space(.), concat("", "text"))]]',
    )


def test_by_escape_text_quotes_for_xpath():
    assert escape_text_quotes_for_xpath('test') == 'concat("", "test")'
