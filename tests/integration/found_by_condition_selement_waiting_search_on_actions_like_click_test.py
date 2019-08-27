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

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from selene import config
from selene.conditions import exact_text
from selene.common.none_object import NoneObject
from selene.driver import SeleneDriver
from tests.acceptance.helpers.helper import get_test_driver
from tests.integration.helpers.givenpage import GivenPage

__author__ = 'yashaka'

driver = NoneObject('driver')  # type: SeleneDriver
GIVEN_PAGE = NoneObject('GivenPage')  # type: GivenPage
WHEN = GIVEN_PAGE  # type: GivenPage
original_timeout = config.timeout


def setup_module(m):
    global driver
    driver = SeleneDriver.wrap(get_test_driver())
    global GIVEN_PAGE
    GIVEN_PAGE = GivenPage(driver)
    global WHEN
    WHEN = GIVEN_PAGE


def teardown_module(m):
    driver.quit()


def setup_function(fn):
    global original_timeout


def test_waits_for_visibility():
    GIVEN_PAGE\
        .opened_with_body(
            '''
            <a href="#second" style="display:none">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>''')\
        .execute_script_with_timeout(
            'document.getElementsByTagName("a")[0].style = "display:block";',
            500)

    driver.all('a').element_by(exact_text('go to Heading 2')).click()
    assert ("second" in driver.current_url) is True


def test_waits_for_present_in_dom_and_visibility():
    GIVEN_PAGE.opened_with_body(
            '''
            <h2 id="second">Heading 2</h2>''')
    WHEN.load_body_with_timeout(
            '''
            <a href="#second">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>''',
            500)

    driver.all('a').element_by(exact_text('go to Heading 2')).click()
    assert ("second" in driver.current_url) is True


def test_waits_first_for_present_in_dom_then_visibility():
    GIVEN_PAGE.opened_with_body(
            '''
            <h2 id="second">Heading 2</h2>''')
    WHEN.load_body_with_timeout(
            '''
            <a href="#second" style="display:none">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>''',
            250)\
        .execute_script_with_timeout(
            'document.getElementsByTagName("a")[0].style = "display:block";',
            500)

    driver.all('a').element_by(exact_text('go to Heading 2')).click()
    assert ("second" in driver.current_url) is True


# todo: there should be each such test method for each "passing" test from above...
def test_fails_on_timeout_during_waiting_for_visibility():
    config.timeout = 0.25
    GIVEN_PAGE\
        .opened_with_body(
            '''
            <a href='#second' style='display:none'>go to Heading 2</a>
            <h2 id='second'>Heading 2</h2>''')\
        .execute_script_with_timeout(
            'document.getElementsByTagName("a")[0].style = "display:block";',
            500)

    with pytest.raises(TimeoutException):
        driver.all('a').element_by(exact_text('go to Heading 2')).click()
    assert ("second" in driver.current_url) is False

