import pytest

from selene.factory import start_browser
from selene.tools import get_driver


@pytest.mark.parametrize("browser_name", ["firefox",
                                          "chrome"])
def test_factory_create_browser(browser_name):
    start_browser(browser_name)
    driver = get_driver()
    assert driver.name == browser_name
