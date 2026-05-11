from appium.options.common import AppiumOptions
from selene import browser, have


def test_complete_task():
    mobile_options = AppiumOptions()
    mobile_options.new_command_timeout = 60
    # Mandatory, also tells Selene to build Appium driver:
    mobile_options.platform_name = 'android'
    mobile_options.set_capability('browserName', 'chrome')

    browser.config.driver_options = mobile_options
    # Not mandatory (because same value in defaults), but let's be explicit now:
    browser.config.driver_remote_url = 'http://127.0.0.1:4723/wd/hub'
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
