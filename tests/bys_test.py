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
from selene import by


def test_by_id():
    assert by.id('c') == ('id', 'c')


def test_by_css():
    assert by.css("a") == ('css selector', 'a')


def test_by_name():
    assert by.name("test") == ('name', 'test')


def test_by_link_text():
    assert by.link_text("text") == ('link text', 'text')


def test_by_partial_link_text():
    assert by.partial_link_text("text") == ("partial link text", "text")


def test_by_xpath():
    assert by.xpath("//a") == ('xpath', "//a")


def test_by_text():
    assert by.text("test") == (
        "xpath",
        './/*[text()[normalize-space(.) = concat("", "test")]]',
    )


def test_by_partial_text():
    assert by.partial_text("text") == (
        "xpath",
        './/*[text()[contains(normalize-space(.), concat("", "text"))]]',
    )


def test_by_escape_text_quotes_for_xpath():
    assert by._escape_text_quotes_for_xpath('test') == 'concat("", "test")'
