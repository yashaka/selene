import pytest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selene import Config, Browser


@pytest.fixture(scope='function')
def session_driver():
    chrome_driver = webdriver.Chrome(ChromeDriverManager().install())
    yield chrome_driver
    chrome_driver.quit()


@pytest.fixture(scope='function')
def browser(session_driver):
    yield Browser(Config(driver=session_driver))
