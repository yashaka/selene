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
import os

import pytest

from selene import have, Config
from selene.support.shared import browser
from tests.integration.helpers.givenpage import GivenPage

empty_page = 'file://{}/../resources/empty.html'.format(
    os.path.abspath(os.path.dirname(__file__))
)


@pytest.fixture(scope='module')
def with_shared_browser_defaults_after_test_module():
    ...

    yield

    browser.quit()
    browser.config.driver = ...

    browser.config.browser_name = Config().browser_name


@pytest.fixture(scope='function')
def given_reset_shared_browser_driver(
    with_shared_browser_defaults_after_test_module,
):
    browser.quit()
    browser.config.driver = ...

    yield

    ...


def test_can_init_default_chrome_browser_on_visit(
    given_reset_shared_browser_driver,
):
    browser.open(empty_page)
    GivenPage(browser.driver).opened_with_body(
        '''
        <h1 id="header">Selene</h1>'''
    )

    browser.element("#header").should(have.exact_text("Selene"))
    assert browser.driver.name == 'chrome'


def test_can_init_custom_firefox_browser_on_visit(
    given_reset_shared_browser_driver,
):
    browser.config.browser_name = 'firefox'

    browser.open(empty_page)
    GivenPage(browser.driver).opened_with_body(
        '''
        <a id="selene_link">Selene site</a>
        '''
    )

    browser.element("#selene_link").should(have.exact_text("Selene site"))
    assert browser.driver.name == 'firefox'


def test_can_init_another_browser_after_custom_only_after_custom_browser_quit(
    given_reset_shared_browser_driver,
):
    # AND
    browser.config.browser_name = 'firefox'
    browser.open(empty_page)
    assert browser.driver.name == 'firefox'
    firefox_session_id = browser.driver.session_id

    # WHEN
    browser.config.browser_name = 'chrome'

    # THEN
    assert browser.driver.name == 'firefox'
    assert browser.driver.session_id == firefox_session_id

    # WHEN
    browser.open(empty_page)

    # THEN
    assert browser.driver.name == 'firefox'
    assert browser.driver.session_id == firefox_session_id

    # WHEN
    browser.quit()
    # AND
    browser.open(empty_page)

    # THEN
    assert browser.driver.name == 'chrome'
    assert browser.driver.session_id != firefox_session_id
