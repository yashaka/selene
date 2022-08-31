import pytest

from selene import be
from selene.support.shared import browser


def test_shared_browser_not_reopen_on_action_after_been_closed():
    browser.open('https://duckduckgo.com/')
    browser.element('#search_form_input_homepage,#searchbox_input').click()

    browser.quit()

    with pytest.raises(RuntimeError) as error:
        browser.element('#search_form_input_homepage,#searchbox_input').click()
    assert 'Webdriver has been closed.' in str(error.value)
    assert 'You need to call open(url) to open a browser again.' in str(
        error.value
    )


def test_shared_browser_starts_after_unexpectedly_closed_in_previous_test():
    browser.open('https://duckduckgo.com/')

    browser.element('#search_form_input_homepage,#searchbox_input').click()

    browser.element('#search_form_input_homepage,#searchbox_input').should(
        be.visible
    )


def test_shared_browser_reopens_on_url_open_action():
    browser.open('https://duckduckgo.com/')
    browser.element('#search_form_input_homepage,#searchbox_input').click()

    browser.quit()
    browser.open('https://duckduckgo.com/')

    browser.element('#search_form_input_homepage,#searchbox_input').click()
