# MIT License
#
# Copyright (c) 2015-2020 Iakiv Kramarenko
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

import pytest

from selene import be, have
from selene.support import by

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


@pytest.fixture(scope='function', autouse=True)
def open_start_page(session_browser):
    session_browser.open(start_page)
    session_browser.element("#hidden_button").should(be.in_dom).should(be.hidden)


def test_get_actual_hidden_webelement(session_browser):
    session_browser.element("#hidden_button").get_actual_webelement()


def test_find_selenium_element_from_hidden_element(session_browser):
    session_browser.element("#hidden_button").find_element(*by.be_following_sibling())


def test_find_selenium_elements_from_hidden_element(session_browser):
    session_browser.element("#hidden_button").find_elements(*by.be_following_sibling())


def test_find_selene_element_from_hidden_element(session_browser):
    session_browser.element("#hidden_button").following_sibling.should(have.text("Inner Link"))
