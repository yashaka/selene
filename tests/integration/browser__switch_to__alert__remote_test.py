import pytest
from selenium.common.exceptions import NoAlertPresentException

from tests.integration.helpers.givenpage import GivenPage


@pytest.fixture(scope='function')
def with_dismiss_alerts_teardown(the_module_remote_browser):
    browser = the_module_remote_browser

    yield

    try:
        while True:
            _ = browser.switch_to.alert
            browser.switch_to.alert.dismiss()
    except NoAlertPresentException:
        pass


def test_alert_is_present_after_click(the_module_remote_browser, with_dismiss_alerts_teardown):
    # GIVEN
    browser = the_module_remote_browser
    GivenPage(browser.driver).opened_with_body(
        """
        <p>
        <input id="alert_btn" type="button" onclick="alert('Good morning')" value="Run">
        </p>
        """
    )

    # WHEN
    browser.element("#alert_btn").click()

    # THEN
    try:
        _ = browser.switch_to.alert
    except NoAlertPresentException:
        pytest.fail("Expected alert to be present, but it was not.")


def test_can_accept_alert(the_module_remote_browser, with_dismiss_alerts_teardown):
    # GIVEN
    browser = the_module_remote_browser
    GivenPage(browser.driver).opened_with_body(
        """
        <p>
        <input id="alert_btn" type="button" onclick="alert('Good morning')" value="Run">
        </p>
        """
    )

    # WHEN
    browser.element("#alert_btn").click()
    browser.switch_to.alert.accept()

    # THEN
    try:
        browser.switch_to.alert.accept()
        pytest.fail("Expected no alert to be present, but one was.")
    except NoAlertPresentException:
        pass


def test_can_dismiss_alert(the_module_remote_browser, with_dismiss_alerts_teardown):
    # GIVEN
    browser = the_module_remote_browser
    GivenPage(browser.driver).opened_with_body(
        """
        <p>
        <input id="alert_btn" type="button" onclick="alert('Good morning')" value="Run">
        </p>
        """
    )

    # WHEN
    browser.element("#alert_btn").click()
    browser.switch_to.alert.dismiss()

    # THEN
    try:
        browser.switch_to.alert.accept()
        pytest.fail("Expected no alert to be present, but one was.")
    except NoAlertPresentException:
        pass
