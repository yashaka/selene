from selene import Browser, Config
from tests.integration.helpers import givenpage


def test_sets_window_size_on_open(chrome_driver):
    # GIVEN
    browser = Browser(
        Config(
            driver=chrome_driver,
            window_width=640,
            window_height=480,
        )
    )

    # WHEN
    browser.open(givenpage.EMPTY_PAGE_URL)
    window_size = browser.driver.get_window_size()

    # THEN
    assert window_size['width'] == 640
    assert window_size['height'] == 480
