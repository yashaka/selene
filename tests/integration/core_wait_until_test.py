from selene import be
from tests.integration.helpers.givenpage import GivenPage


def test_wait_until_returns_true_when_condition_matches(session_browser):
    browser = session_browser.with_(timeout=0.5)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        """
        <div id="overlay">overlay</div>
        """
    ).execute_script_with_timeout(
        'document.getElementById("overlay").remove();',
        0.25,
    )

    disappeared = browser.element("#overlay").wait_until(be.not_.present_in_dom)

    assert disappeared is True


def test_wait_until_returns_false_on_timeout(session_browser):
    browser = session_browser.with_(timeout=0.15)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        """
        <div id="overlay">overlay</div>
        """
    )

    disappeared = browser.element("#overlay").wait_until(be.not_.present_in_dom)

    assert disappeared is False
