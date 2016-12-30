from time import sleep

import pytest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selene.browsers import Browser
from selene.factory import start_browser
from selene.tools import get_driver, set_driver


@pytest.mark.parametrize("browser_name", ["firefox",
                                          "chrome"])
def test_factory_can_create_browser(browser_name):
    start_browser(browser_name)
    driver = get_driver()
    assert driver.name == browser_name


def test_can_set_browser_directly():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    set_driver(driver)
    start_browser(Browser.CHROME)
    assert driver.name == Browser.CHROME
    driver.quit()
