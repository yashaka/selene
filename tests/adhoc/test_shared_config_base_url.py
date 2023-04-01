from selene import browser, be


def test_opening_relative_url():
    browser.config.base_url = 'http://todomvc.com/examples/emberjs'
    browser.open('/')

    browser.element('#new-todo').should(be.visible)
