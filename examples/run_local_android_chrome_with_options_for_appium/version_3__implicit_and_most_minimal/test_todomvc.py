from appium.options.common import AppiumOptions
from selene import browser, have


# Normally to be stored in a separate file,
# somewhere at project_package/utils/driver_options.py
def android_chrome_options():
    options = AppiumOptions()
    options.platform_name = 'android'  # mandatory
    options.set_capability('browserName', 'chrome')
    return options


def test_complete_task():
    browser.config.driver_options = android_chrome_options()
    browser.config.rebuild_dead_driver = False
    browser.config.base_url = 'https://todomvc.com/examples/emberjs'

    # WHEN
    browser.open('/')

    browser.should(have.title_containing('TodoMVC'))

    # WHEN
    browser.element('#new-todo').type('a').press_enter()
    browser.element('#new-todo').type('b').press_enter()
    browser.element('#new-todo').type('c').press_enter()

    browser.all('#todo-list>li').should(have.exact_texts('a', 'b', 'c'))

    # WHEN
    browser.all('#todo-list>li').element_by(have.exact_text('b')).element(
        '.toggle'
    ).click()

    browser.all('#todo-list>li').by(have.css_class('completed')).should(
        have.exact_texts('b')
    )
    browser.all('#todo-list>li').by(have.no.css_class('completed')).should(
        have.exact_texts('a', 'c')
    )
