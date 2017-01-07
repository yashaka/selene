import pytest

from selene.browsers import Browser
from selene.factory import start_driver
from selene.tools import get_driver, set_driver
from tests.acceptance.helpers.helper import get_test_driver


@pytest.mark.parametrize("browser_name", ["firefox",
                                          "chrome"])
def test_factory_can_create_browser(browser_name):
    start_driver(browser_name)
    assert get_driver().name == browser_name


def test_can_set_browser_directly():
    driver = get_test_driver()
    set_driver(driver)
    start_driver(Browser.CHROME)
    assert get_driver().name == Browser.CHROME
    get_driver().quit()
    driver.quit()