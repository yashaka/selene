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

    options = UiAutomator2Options()
    options.app = 'bs://c700ce60cf13ae8ed97705a55b8e022f13c5827c'
    options.set_capability(
        'bstack:options',
        {
            'deviceName': 'Google Pixel 7',
            # 'platformVersion': '13.0',
            **project_config.bstack_creds,
        },
    )
    browser.config.driver_options = options
    browser.config.driver_remote_url = 'http://hub.browserstack.com/wd/hub'
    # To speed tests a bit
    # by not checking if driver is alive before each action
    browser.config.rebuild_dead_driver = False

    by_id = lambda id: (AppiumBy.ID, f'org.wikipedia.alpha:id/{id}')

    # GIVEN
    browser.open()  # not needed, but to explicitly force appium to open app

    # WHEN
    browser.element((AppiumBy.ACCESSIBILITY_ID, 'Search Wikipedia')).click()
    browser.element(by_id('search_src_text')).type('Appium')

    # THEN
    browser.all(by_id('page_list_item_title')).should(
        have.size_greater_than(0)
    )
