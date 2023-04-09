import pytest
from appium.options.android import UiAutomator2Options

from examples.run_cross_platform import project
from selene import browser


@pytest.fixture(scope='function', autouse=True)
def driver_management():
    # TODO: move all values to project.config
    if project.config.context is project.Context.bstack_android:
        android_options = UiAutomator2Options()
        android_options.app = 'bs://c700ce60cf13ae8ed97705a55b8e022f13c5827c'
        android_options.set_capability(
            'bstack:options',
            {
                'deviceName': 'Google Pixel 7',
                # 'platformVersion': '13.0',
                **project.config.bstack_creds,
            },
        )
        browser.config.driver_options = android_options
        browser.config.driver_remote_url = 'http://hub.browserstack.com/wd/hub'
    elif project.config.context is project.Context.local_web:
        browser.config.base_url = 'https://www.wikipedia.org'
        # if not set, will load nothing on browser.open() for web, but just init driver:
        browser.config._get_base_url_on_open_with_no_args = True

    yield

    browser.quit()
