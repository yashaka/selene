import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options

from examples.run_cross_platform import project
from selene import browser


@pytest.fixture(scope='function', autouse=True)
def driver_management():
    # TODO: move all values to project.config
    if project.config.context == 'bstack_android':
        options = UiAutomator2Options()
        options.app = 'bs://c700ce60cf13ae8ed97705a55b8e022f13c5827c'
        options.set_capability(
            'bstack:options',
            {
                'deviceName': 'Google Pixel 7',
                # 'platformVersion': '13.0',
                **project.config.bstack_creds,
            },
        )
        browser.config.driver_options = options
        browser.config.driver_remote_url = 'http://hub.browserstack.com/wd/hub'
        browser.config.driver = webdriver.Remote(
            command_executor=browser.config.driver_remote_url,
            options=browser.config.driver_options,
        )
        # To speed tests a bit
        # by not checking if driver is alive before each action
        browser.config.rebuild_dead_driver = False
    elif project.config.context == 'local_web':
        browser.config.base_url = 'https://www.wikipedia.org'
        browser.config._get_base_url_on_open_with_no_args = True

    yield

    browser.quit()
