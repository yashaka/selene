from selene import browser, be
from tests import resources


def test_opening_relative_url():
    browser.config.base_url = resources.TODOMVC_URL
    browser.open('/')

    browser.element('#new-todo').should(be.visible)
