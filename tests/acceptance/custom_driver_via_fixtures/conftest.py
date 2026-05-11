import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from selene import Config, Browser, support


@pytest.fixture(scope='function')
def driver_per_test():
    chrome_driver = webdriver.Chrome(service=Service())

    yield chrome_driver

    chrome_driver.quit()


@pytest.fixture(scope='function')
def browser(driver_per_test):
    yield Browser(
        Config(
            driver=driver_per_test,
        )
    )
