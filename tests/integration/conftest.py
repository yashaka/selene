import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.core.utils import ChromeType

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
        chrome_driver = webdriver.Chrome(
            service=ChromeService(
                ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
            )
        )
    yield chrome_driver
    chrome_driver.quit()


@pytest.fixture(scope='session')
def firefox_driver(request):
    gecko_driver = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install())
    )
    yield gecko_driver
    gecko_driver.quit()


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
        chrome_driver = webdriver.Chrome(
            service=ChromeService(
                ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
            )
        )
    yield Browser(Config(driver=chrome_driver))
    chrome_driver.quit()
