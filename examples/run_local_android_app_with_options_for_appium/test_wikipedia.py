from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from appium import webdriver
from selene import browser, have


def abs_path_at_examples(relative_path):
    import examples  # pylint: disable=import-outside-toplevel
    from pathlib import Path  # pylint: disable=import-outside-toplevel

    return (
        Path(examples.__file__)
        .parent.joinpath(relative_path)
        .absolute()
        .__str__()
    )


def test_searches():
    options = UiAutomator2Options()
    options.new_command_timeout = 60
    options.app = abs_path_at_examples('wikipedia-alpha-universal-release.apk')
    # options.app_package = 'org.wikipedia.alpha'
    options.app_wait_activity = 'org.wikipedia.*'

    browser.config.driver_options = options
    browser.config.driver_remote_url = 'http://127.0.0.1:4723/wd/hub'
    browser.config.driver = webdriver.Remote(
        command_executor=browser.config.driver_remote_url,
        options=browser.config.driver_options,
    )
    # To speed tests a bit
    # by not checking if driver is alive before each action
    browser.config.rebuild_dead_driver = False

    by_id = lambda id: (AppiumBy.ID, f'org.wikipedia.alpha:id/{id}')

    # GIVEN
    browser.element(by_id('fragment_onboarding_skip_button')).click()

    # WHEN
    browser.element((AppiumBy.ACCESSIBILITY_ID, 'Search Wikipedia')).click()
    browser.element(by_id('search_src_text')).type('Appium')

    # THEN
    browser.all(by_id('page_list_item_title')).should(
        have.size_greater_than(0)
    )
