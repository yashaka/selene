import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

from selene import Config, Browser


@pytest.fixture(scope='function')
def session_driver():
    chrome_driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
        )
    )
    yield chrome_driver
    chrome_driver.quit()


@pytest.fixture(scope='function')
def browser(session_driver):
    yield Browser(Config(driver=session_driver))
