from selene import have
from selene.support.shared import config, browser, SharedConfig


def setup_module():
    config.hold_browser_open = True


def teardown_module():
    config.hold_browser_open = SharedConfig().hold_browser_open


def test_open_browser_with_hold():
    browser.open('http://todomvc.com/examples/emberjs/')

    browser.element('#new-todo').type('a').press_enter()


def test_browser_still_opened():
    browser.element('#new-todo').type('b').press_enter()

    browser.all('#todo-list>li').should(have.texts('a', 'b'))
