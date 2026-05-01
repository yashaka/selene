from selene import be
from tests.integration.helpers.givenpage import GivenPage


def test_wait_until_for_not_present_in_dom_returns_true_when_element_disappears(
    session_browser,
):
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

    matched = browser.element("#overlay").wait_until(be.not_.present_in_dom)

    assert matched is True


def test_wait_until_for_not_present_in_dom_returns_false_on_timeout(session_browser):
    browser = session_browser.with_(timeout=0.15)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        """
        <div id="overlay">overlay</div>
        """
    )

    matched = browser.element("#overlay").wait_until(be.not_.present_in_dom)

    assert matched is False


def test_wait_until_for_visible_returns_true_when_element_appears(session_browser):
    browser = session_browser.with_(timeout=0.5)
    page = GivenPage(browser.driver)
    page.opened_with_body("<div id='container'></div>").execute_script_with_timeout(
        """
        const element = document.createElement("div");
        element.id = "delayed";
        element.textContent = "ready";
        document.getElementById("container").appendChild(element);
        """,
        0.25,
    )

    matched = browser.element("#delayed").wait_until(be.visible)

    assert matched is True


def test_wait_until_for_visible_returns_false_on_timeout_when_element_absent(
    session_browser,
):
    browser = session_browser.with_(timeout=0.15)
    page = GivenPage(browser.driver)
    page.opened_with_body("<div id='container'></div>")

    matched = browser.element("#delayed").wait_until(be.visible)

    assert matched is False


def test_wait_until_for_present_in_dom_returns_true_when_element_already_present(
    session_browser,
):
    browser = session_browser.with_(timeout=0.15)
    page = GivenPage(browser.driver)
    page.opened_with_body("<div id='ready'>ready</div>")

    matched = browser.element("#ready").wait_until(be.present_in_dom)

    assert matched is True


def test_wait_until_for_visible_returns_false_without_throwing_timeout_exception(
    session_browser,
):
    browser = session_browser.with_(timeout=0.15)
    page = GivenPage(browser.driver)
    page.opened_with_body("<div id='container'></div>")

    try:
        matched = browser.element("#delayed").wait_until(be.visible)
    except Exception as error:
        raise AssertionError(
            "wait_until should return False on timeout instead of raising"
        ) from error

    assert matched is False
