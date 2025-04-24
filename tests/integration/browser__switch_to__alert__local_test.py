import pytest
from selenium.common.exceptions import NoAlertPresentException

from tests.integration.helpers.givenpage import GivenPage


@pytest.fixture(scope='function')
def with_dismiss_alerts_teardown(session_browser):
    yield
    try:
        while True:
            _ = session_browser.switch_to.alert
            session_browser.switch_to.alert.dismiss()
    except NoAlertPresentException:
        pass


def test_alert_is_present_after_click(session_browser, with_dismiss_alerts_teardown):
    # GIVEN
    GivenPage(session_browser.driver).opened_with_body(
        """
        <p>
        <input id="alert_btn" type="button" onclick="alert('Good morning')" value="Run">
        </p>"""
    )

    # WHEN
    session_browser.element("#alert_btn").click()

    # THEN
    try:
        _ = session_browser.switch_to.alert
    except NoAlertPresentException:
        pytest.fail("Expected alert to be present, but it was not.")


def test_can_accept_alert(session_browser, with_dismiss_alerts_teardown):
    # GIVEN
    GivenPage(session_browser.driver).opened_with_body(
        """
        <p>
        <input id="alert_btn" type="button" onclick="alert('Good morning')" value="Run">
        </p>"""
    )

    # WHEN
    session_browser.element("#alert_btn").click()
    session_browser.switch_to.alert.accept()

    # THEN
    try:
        session_browser.switch_to.alert.accept()
        pytest.fail("Expected no alert to be present, but one was.")
    except NoAlertPresentException:
        pass


def test_can_dismiss_alert(session_browser, with_dismiss_alerts_teardown):
    # GIVEN
    GivenPage(session_browser.driver).opened_with_body(
        """
        <p>
        <input id="alert_btn" type="button" onclick="alert('Good morning')" value="Run">
        </p>"""
    )

    # WHEN
    session_browser.element("#alert_btn").click()
    session_browser.switch_to.alert.dismiss()

    # THEN
    try:
        session_browser.switch_to.alert.accept()
        pytest.fail("Expected no alert to be present, but one was.")
    except NoAlertPresentException:
        pass
