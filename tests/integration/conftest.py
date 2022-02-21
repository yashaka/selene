import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

from selene import Config, Browser
from tests.helpers import headless_chrome_options


@pytest.fixture(scope='session')
def chrome_driver(request):
    if request.config.getoption('--headless'):
        chrome_driver = webdriver.Chrome(
            ChromeDriverManager().install(),
            options=headless_chrome_options(),
        )
    else:
        chrome_driver = webdriver.Chrome(service=Service(
        ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
    ))
    yield chrome_driver
    chrome_driver.quit()


@pytest.fixture(scope='function')
def session_browser(chrome_driver):
    yield Browser(Config(driver=chrome_driver))


@pytest.fixture(scope='function')
def function_browser(request):
    if request.config.getoption('--headless'):
        chrome_driver = webdriver.Chrome(
            ChromeDriverManager().install(),
            options=headless_chrome_options(),
        )
    else:
        chrome_driver = webdriver.Chrome(service=Service(
        ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
    ))
    yield Browser(Config(driver=chrome_driver))
    chrome_driver.quit()
