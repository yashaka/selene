import dotenv
import pydantic
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selene import browser, have


def test_searches():
    class ProjectConfig(pydantic.BaseSettings):
        bstack_accessKey: str
        bstack_userName: str = 'bob'

        @property
        def bstack_creds(self):
            return {
                'userName': self.bstack_userName,
                'accessKey': self.bstack_accessKey,
            }

    project_config = ProjectConfig(dotenv.find_dotenv())

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
    app = browser.with_(
        driver_options=android_options,
        driver_remote_url='http://hub.browserstack.com/wd/hub',
    )

    by_id = lambda id: (AppiumBy.ID, f'org.wikipedia.alpha:id/{id}')

    # GIVEN
    app.open()  # not needed, but to explicitly force appium to open app

    # WHEN
    app.element((AppiumBy.ACCESSIBILITY_ID, 'Search Wikipedia')).click()
    app.element(by_id('search_src_text')).type('Appium')

    # THEN
    app.all(by_id('page_list_item_title')).should(have.size_greater_than(0))
