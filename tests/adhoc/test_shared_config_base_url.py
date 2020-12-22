from selene import be
from selene.support.shared import browser


def test_opening_relative_url():
    browser.config.base_url = 'http://todomvc.com/examples/emberjs'
    browser.open('/')

    browser.element('#new-todo').should(be.visible)
