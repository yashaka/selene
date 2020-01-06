from selene import browser, be, config


def test_complete_task():
    config.base_url = 'http://todomvc.com/examples/emberjs'
    browser.open('/')

    browser.element('#new-todo').should(be.visible)
