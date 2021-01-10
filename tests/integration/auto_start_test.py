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

from selene import have
from selene.support.shared import browser, config
from tests.integration.helpers.givenpage import GivenPage
from tests_from_past.past.acceptance.helpers.helper import get_test_driver


def test_manual_start():
    driver = get_test_driver()
    config.driver = driver

    GivenPage(browser.driver).opened_with_body(
        '<h1 id="header">Selene</h1>')

    browser.element("#header").should(have.exact_text("Selene"))


def test_manual_start_2():
    GivenPage(browser.driver).opened_with_body(
        '<a id="selene_link">Selene site</a>')

    browser.element("#selene_link").should(have.exact_text("Selene site"))


def test_auto_start():
    GivenPage(browser.driver).opened_with_body(
        '<h1 id="header">Selene</h1>')

    browser.element("#header").should(have.exact_text("Selene"))


def test_auto_start_2():
    GivenPage(browser.driver).opened_with_body(
        '<a id="selene_link">Selene site</a>')

    browser.element("#selene_link").should(have.exact_text("Selene site"))


def teardown_module():
    browser.driver.quit()
