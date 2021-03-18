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
from selenium.common.exceptions import NoAlertPresentException

from tests.integration.helpers.givenpage import GivenPage


def test_can_accept_alert(session_browser):
    GivenPage(session_browser.driver).opened_with_body(
        """
        <p>
        <input id="alert_btn" type="button" onclick="alert('Good morning')" value="Run">
        </p>"""
    )

    session_browser.element("#alert_btn").click()
    session_browser.switch_to.alert.accept()

    try:
        session_browser.switch_to.alert.accept()
        assert False, 'actual: alert presents, expected: alert not present'
    except NoAlertPresentException:
        assert True


def test_can_dismiss_confirm_dialog(session_browser):
    GivenPage(session_browser.driver).opened_with_body(
        """
        <p>
        <input id="alert_btn" type="button" onclick="alert('Good morning')" value="Run">
        </p>"""
    )

    session_browser.element("#alert_btn").click()
    session_browser.switch_to.alert.dismiss()

    try:
        session_browser.switch_to.alert.accept()
        assert False, 'actual: alert presents, expected: alert not present'
    except NoAlertPresentException:
        assert True


def test_alert_is_present(session_browser):
    GivenPage(session_browser.driver).opened_with_body(
        """
        <p>
        <input id="alert_btn" type="button" onclick="alert('Good morning')" value="Run">
        </p>"""
    )

    session_browser.element("#alert_btn").click()

    try:
        session_browser.switch_to.alert.accept()
        assert True
    except NoAlertPresentException:
        assert False, 'actual: alert not present, expected: alert is present'
