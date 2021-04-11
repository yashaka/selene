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
import os

from selene import have
from selene.support.shared import browser
from tests.integration.helpers.givenpage import GivenPage

empty_page = 'file://{}/../resources/empty.html'.format(
    os.path.abspath(os.path.dirname(__file__))
)


def setup_function():
    browser.quit()


def teardown_function():
    browser.config.browser_name = 'chrome'
    browser.quit()


def test_can_init_default_browser_on_visit():
    browser.open(empty_page)
    GivenPage(browser.driver).opened_with_body(
        '''
        <h1 id="header">Selene</h1>'''
    )

    browser.element("#header").should(have.exact_text("Selene"))
    assert browser.driver.name == 'chrome'


def test_can_init_custom_browser_on_visit():
    browser.config.browser_name = 'firefox'

    browser.open(empty_page)
    GivenPage(browser.driver).opened_with_body(
        '''
        <a id="selene_link">Selene site</a>
        '''
    )

    browser.element("#selene_link").should(have.exact_text("Selene site"))
    assert browser.driver.name == 'firefox'


def test_can_init_default_browser_after_custom():
    browser.open(empty_page)
    GivenPage(browser.driver).opened_with_body(
        '''
        <h1 id="header">Selene</h1>
        '''
    )

    browser.element("#header").should(have.exact_text("Selene"))
    assert browser.driver.name == 'chrome'
