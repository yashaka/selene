from selene import browser, be, config


def test_opening_relative_url():
    config.base_url = 'http://todomvc.com/examples/emberjs'
    browser.open_url('/')

    browser.element('#new-todo').should(be.visible)
