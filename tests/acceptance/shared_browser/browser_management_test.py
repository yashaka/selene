import pytest

from selene import be
from selene.support.shared import browser


def test_shared_browser_not_reopen_on_action_after_been_closed():
    browser.open('http://google.ru')
    browser.element('[name="q"]').click()

    browser.quit()

    with pytest.raises(RuntimeError) as error:
        browser.element('[name="q"]').click()
    assert 'Webdriver has been closed.' in str(error.value)
    assert 'You need to call open(url) to open a browser again.' in str(error.value)


def test_shared_browser_starts_after_unexpectedly_closed_in_previous_test():
    browser.open('http://google.ru')

    browser.element('[name="q"]').click()

    browser.element('[name="q"]').should(be.visible)


def test_shared_browser_reopens_on_url_open_action():
    browser.open('http://google.ru')
    browser.element('[name="q"]').click()

    browser.quit()
    browser.open('http://google.ru')

    browser.element('[name="q"]').click()
