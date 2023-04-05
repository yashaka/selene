import os
from selenium import webdriver
from selene import browser, have


def test_complete_task():
    options = webdriver.ChromeOptions()
    options.browser_version = '100.0'
    options.set_capability('screenResolution', '1920x1080x24')
    options.set_capability('enableVNC', True)
    options.set_capability('enableVideo', True)
    browser.config.driver_options = options
    browser.config.remote_url = (
        f'https://{os.getenv("LOGIN")}:{os.getenv("PASSWORD")}@'
        f'selenoid.autotests.cloud/wd/hub'
    )

    browser.open('http://todomvc.com/examples/emberjs/')
    browser.should(have.title_containing('TodoMVC'))

    browser.element('#new-todo').type('a').press_enter()
    browser.element('#new-todo').type('b').press_enter()
    browser.element('#new-todo').type('c').press_enter()
    browser.all('#todo-list>li').should(have.exact_texts('a', 'b', 'c'))

    browser.all('#todo-list>li').element_by(have.exact_text('b')).element(
        '.toggle'
    ).click()
    browser.all('#todo-list>li').by(have.css_class('completed')).should(
        have.exact_texts('b')
    )
    browser.all('#todo-list>li').by(have.no.css_class('completed')).should(
        have.exact_texts('a', 'c')
    )
