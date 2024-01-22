import os

from dotenv import dotenv_values
from selenium import webdriver
from selene import browser, have
from tests import resources


def test_complete_task():
    dotenv = dotenv_values()

    class ProjectConfig:
        selenoid_login = os.getenv('selenoid_login', dotenv.get('selenoid_login'))
        selenoid_password = os.getenv(
            'selenoid_password', dotenv.get('selenoid_password')
        )

    options = webdriver.ChromeOptions()
    options.browser_version = '100.0'
    options.set_capability(
        'selenoid:options',
        {
            'screenResolution': '1920x1080x24',
            'enableVNC': True,
            'enableVideo': True,
            'enableLog': True,
        },
    )
    browser.config.driver_options = options
    browser.config.driver_remote_url = (
        f'https://{ProjectConfig.selenoid_login}:{ProjectConfig.selenoid_password}@'
        f'selenoid.autotests.cloud/wd/hub'
    )

    browser.open(resources.TODOMVC_URL)
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
