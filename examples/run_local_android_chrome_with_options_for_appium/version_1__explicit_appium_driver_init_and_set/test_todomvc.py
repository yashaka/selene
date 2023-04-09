from appium import webdriver
from appium.options.common import AppiumOptions
from selene import browser, have


def test_complete_task():
    mobile_options = AppiumOptions()
    mobile_options.new_command_timeout = 60
    # Mandatory, also tells Selene to build Appium driver:
    mobile_options.platform_name = 'android'
    mobile_options.set_capability('browserName', 'chrome')

    browser.config.driver = webdriver.Remote(
        command_executor='http://127.0.0.1:4723/wd/hub',
        options=mobile_options,
    )
    # To speed tests a bit
    # by not checking if driver is alive before each action
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
