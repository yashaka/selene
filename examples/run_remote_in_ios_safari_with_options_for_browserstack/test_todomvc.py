import os

from dotenv import dotenv_values
from selenium import webdriver
from selene import browser, have


class EnvField:
    dotenv = dotenv_values()

    def __init__(self, name=None, default=None):
        self.name = name
        self.default = default

    def __set_name__(self, owner, name):
        self.name = self.name or name

    def __get__(self, instance, owner):
        return os.getenv(self.name, self.dotenv.get(self.name, self.default))


class EnvFields:
    """
    A base class for classes that hold settings as class annotations.
    Each annotation will be automatically initialized
    with an EnvField descriptor instance.
    """

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)

        for a_name, a_type in getattr(cls, '__annotations__', {}).items():
            a_default = getattr(cls, a_name, None)
            if isinstance(a_default, EnvField):
                a_field = a_default
                a_field.name = a_name
                # TODO: store a_type and implement validation based on it
                # a_field.type_ = a_type
            else:
                a_field = EnvField(name=a_name, default=a_default)

            setattr(cls, a_field.name, a_field)

        return obj


def test_complete_task():
    class ProjectConfig(EnvFields):
        bstack_accessKey: str
        # An example of field with default, yet to be overridden by env if present
        bstack_userName: str = 'bob'

        @property
        def bstack_creds(self) -> dict:
            return {
                'userName': self.bstack_userName,
                'accessKey': self.bstack_accessKey,
            }

    project_config = ProjectConfig()

    options = webdriver.ChromeOptions()
    options.set_capability(
        'bstack:options',
        {
            # 'platformName': 'ios',
            'deviceName': 'iPhone 14 Pro Max',
            # 'platformVersion': '16',
            # 'browserName': 'safari',  # default for iPhone
            # 'deviceOrientation': 'portrait',
            'deviceOrientation': 'landscape',
            **project_config.bstack_creds,
        },
    )
    browser.config.driver_options = options
    browser.config.driver_remote_url = 'http://hub.browserstack.com/wd/hub'

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
