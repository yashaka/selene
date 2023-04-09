from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
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
    android_options = UiAutomator2Options()
    android_options.new_command_timeout = 60
    android_options.app = abs_path_at_examples(
        'wikipedia-alpha-universal-release.apk'
    )
    android_options.app_wait_activity = 'org.wikipedia.*'
    # android_options.app_package = 'org.wikipedia.alpha'  # not mandatory

    # # Possible, but not needed, because of Selene's implicit driver init logic
    # browser.config.driver = webdriver.Remote(
    #     command_executor='http://127.0.0.1:4723/wd/hub',
    #     options=android_options,
    # )
    browser.config.driver_options = android_options
    # # Possible, but not needed, because will be used by default:
    # browser.config.driver_remote_url = 'http://127.0.0.1:4723/wd/hub'

    by_id = lambda id: (AppiumBy.ID, f'org.wikipedia.alpha:id/{id}')

    # GIVEN
    browser.open()
    browser.element(by_id('fragment_onboarding_skip_button')).click()

    # WHEN
    browser.element((AppiumBy.ACCESSIBILITY_ID, 'Search Wikipedia')).click()
    browser.element(by_id('search_src_text')).type('Appium')

    # THEN
    browser.all(by_id('page_list_item_title')).should(
        have.size_greater_than(0)
    )
