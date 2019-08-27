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

import os

from selene import config, browser
from selene.conditions import in_dom, hidden, text, size
from selene.support import by
from selene.support.jquery_style_selectors import s

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def setup_module(m):
    config.browser_name = "chrome"
    browser.open_url(start_page)
    s("#hidden_button").should_be(in_dom).should_be(hidden)


def test_get_actual_hidden_webelement():
    s("#hidden_button").get_actual_webelement()


def test_find_selenium_element_from_hidden_element():
    s("#hidden_button").find_element(*by.be_following_sibling())


def test_find_selenium_elements_from_hidden_element():
    s("#hidden_button").find_elements(*by.be_following_sibling())


def test_find_selene_element_from_hidden_element():
    s("#hidden_button").following_sibling.should_have(text("Inner Link"))


def test_find_selene_collection_from_hidden_context():
    s("#hidden_button").ss(by.be_following_sibling()).should_have(size(6))
