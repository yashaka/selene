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

from selene.support.past import config
from selene.support.past.common.none_object import NoneObject
from selene.support.past.driver import SeleneDriver
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
    config.timeout = original_timeout


def test_search_is_lazy_and_does_not_start_on_creation_for_both_parent_and_inner():
    GIVEN_PAGE.opened_empty()
    non_existent_element = driver.element('#not-existing-element').element('.not-existing-inner')
    assert str(non_existent_element)


def test_search_is_postponed_until_actual_action_like_questioning_displayed():
    GIVEN_PAGE.opened_empty()

    element = driver.element('#will-be-existing-element').element('.will-exist-inner')
    WHEN.load_body('''
        <h1 id="will-be-existing-element">
            <span class="will-exist-inner">Hello</span> kitty:*
        </h1>''')
    assert element.is_displayed() is True


def test_search_is_updated_on_next_actual_action_like_questioning_displayed():
    GIVEN_PAGE.opened_empty()

    element = driver.element('#will-be-existing-element').element('.will-exist-inner')
    WHEN.load_body('''
        <h1 id="will-be-existing-element">
            <span class="will-exist-inner">Hello</span> kitty:*
        </h1>''')
    assert element.is_displayed() is True

    element = driver.element('#will-be-existing-element').element('.will-exist-inner')
    WHEN.load_body('''
        <h1 id="will-be-existing-element">
            <span class="will-exist-inner" style="display:none">Hello</span> kitty:*
        </h1>''')
    assert element.is_displayed() is False


def test_search_finds_exactly_inside_parent():
    GIVEN_PAGE.opened_with_body('''
        <a href="#first">go to Heading 2</a>
        <p>
            <a href="#second">go to Heading 2</a>
            <h1 id="first">Heading 1</h1>
            <h2 id="second">Heading 2</h2>
        /p>''')

    driver.element('p').element('a').click()
    assert ("second" in driver.current_url) is True
