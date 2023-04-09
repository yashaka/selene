import dotenv
import pydantic
import pytest
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selene import browser as mobile, have


class ProjectConfig(pydantic.BaseSettings):
    """
    A project config class to store all project specific settings
    to be used both in tests and core part of the framework,
    like models, data, utils, etc. – i.e. serves as cross-cutting concern.
    Normally to be stored in a separate file.
    """

    bstack_accessKey: str
    bstack_userName: str = 'admin'
    app_package: str = 'org.wikipedia.alpha'

    @property
    def bstack_creds(self):
        return {
            'userName': self.bstack_userName,
            'accessKey': self.bstack_accessKey,
        }


project_config = ProjectConfig(dotenv.find_dotenv())  # type: ignore
"""
A project config instance that is a cross-cutting concern for all project,
that can be used as it is, just via simple hard-code where it's needed,
like in `by_id` helper below.
"""


def by_id(value):
    """
    A helper to create a mobile locator based on id value
    Normally to be stored in a separate file,
    somewhere in `utils` package,
    probably than renamed to id(value) and stored in `utils/by.py` module,
    to be used as `by.id(value)` in tests.
    """
    return AppiumBy.ID, f'{project_config.app_package}:id/{value}'


@pytest.fixture(scope='function')
def app():
    android_options = UiAutomator2Options()
    android_options.app = 'bs://c700ce60cf13ae8ed97705a55b8e022f13c5827c'
    android_options.set_capability(
        'bstack:options',
        {
            'deviceName': 'Google Pixel 7',
            # 'platformVersion': '13.0',
            **project_config.bstack_creds,
        },
    )
    android = mobile.with_(
        driver_options=android_options,
        driver_remote_url='http://hub.browserstack.com/wd/hub',
        rebuild_dead_driver=False,
    )

    yield android

    android.quit()


def test_searches(app):
    # GIVEN
    app.open()

    # WHEN
    app.element((AppiumBy.ACCESSIBILITY_ID, 'Search Wikipedia')).click()
    app.element(by_id('search_src_text')).type('Appium')

    # THEN
    app.all(by_id('page_list_item_title')).should(have.size_greater_than(0))
