import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

from selene import Config, Browser
from selene.support.by import name


@pytest.fixture(scope='function')
def driver_per_test():
    chrome_driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
        )
    )
    yield chrome_driver
    chrome_driver.quit()


@pytest.fixture(scope='function')
def browser(driver_per_test):
    yield Browser(
        Config(
            driver=driver_per_test,
        )
    )
