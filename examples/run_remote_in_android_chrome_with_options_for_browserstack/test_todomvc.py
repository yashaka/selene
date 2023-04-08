import os

from dotenv import dotenv_values
from selenium import webdriver
from selene import browser, have


class EnvField:
    dotenv = dotenv_values()

    def __init__(self, env_name=None, default=None):
        self.env_name = env_name
        self.default = default

    def __set_name__(self, owner, name):
        self.env_name = self.env_name or name

    def __get__(self, instance, owner):
        return os.getenv(
            self.env_name, self.dotenv.get(self.env_name, self.default)
        )


def test_complete_task():
    class ProjectConfig:
        bstack_userName = EnvField()
        bstack_accessKey = EnvField()

    project_config = ProjectConfig()

    options = webdriver.ChromeOptions()
    options.set_capability(
        'bstack:options',
        {
            'deviceName': 'Google Pixel 7',
            # 'browserName': 'chrome',  # default for Pixel
            # 'deviceOrientation': 'landscape',
            'deviceOrientation': 'portrait',
            'userName': project_config.bstack_userName,
            'accessKey': project_config.bstack_accessKey,
        },
    )
    browser.config.driver_options = options
    browser.config.driver_remote_url = 'http://hub.browserstack.com/wd/hub'
    # To speed tests a bit
    # by not checking if driver is alive before each action
    browser.config.rebuild_dead_driver = False

    # WHEN
    browser.open('https://todomvc.com/examples/emberjs/')

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
