import os

import pytest
from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selene.support._extensions.webdriver_manager import ChromeType

from selene import Config, Browser, support
from tests.helpers import headless_chrome_options


@pytest.fixture(scope='session')
def chrome_driver(request):
    dotenv = dotenv_values()
    headless = (
        str(request.config.getoption('--headless', dotenv.get('headless'))).lower()
        == 'true'
    )
    if headless:
        chrome_driver = webdriver.Chrome(
            options=headless_chrome_options(),
            service=ChromeService(
                support._extensions.webdriver_manager.patch._to_find_chromedrivers_from_115(
                    ChromeDriverManager(chrome_type=ChromeType.GOOGLE)
                ).install()
            ),
        )
    else:
        chrome_driver = webdriver.Chrome(
            service=ChromeService(
                support._extensions.webdriver_manager.patch._to_find_chromedrivers_from_115(
                    ChromeDriverManager(chrome_type=ChromeType.GOOGLE)
                ).install()
            )
        )
    yield chrome_driver
    chrome_driver.quit()


@pytest.fixture(scope='function')
def a_remote_browser():
    options = webdriver.ChromeOptions()
    options.browser_version = '100.0'
    options.set_capability(
        'selenoid:options',
        {
            'screenResolution': '1920x1080x24',
            'enableVNC': True,
            'enableVideo': True,
            'enableLog': True,
        },
    )
    project_config = dotenv_values()
    browser_ = Browser(
        Config(
            driver_options=options,
            driver_remote_url=(
                f'https://{project_config["LOGIN"]}:{project_config["PASSWORD"]}@'
                f'selenoid.autotests.cloud/wd/hub'
            ),
        )
    )

    yield browser_

    browser_.quit()


@pytest.fixture(scope='module')
def the_module_remote_browser():
    dotenv = dotenv_values()

    class ProjectConfig:
        selenoid_login = os.getenv('selenoid_login', dotenv.get('selenoid_login'))
        selenoid_password = os.getenv(
            'selenoid_password', dotenv.get('selenoid_password')
        )

    options = webdriver.ChromeOptions()
    options.browser_version = '100.0'
    options.set_capability(
        'selenoid:options',
        {
            'screenResolution': '1920x1080x24',
            'enableVNC': True,
            'enableVideo': True,
            'enableLog': True,
        },
    )

    browser_ = Browser(
        Config(
            driver_options=options,
            driver_remote_url=(
                f'https://{ProjectConfig.selenoid_login}:'
                f'{ProjectConfig.selenoid_password}@'
                f'selenoid.autotests.cloud/wd/hub'
            ),
        )
    )

    yield browser_

    browser_.quit()


@pytest.fixture(scope='session')
def firefox_driver():
    gecko_driver = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install())
    )
    yield gecko_driver
    gecko_driver.quit()


# TODO: in fact its a_browser_with_session_driver,
#       where a_ means a new one with fresh config, but old same driver
#       should we rename it?
@pytest.fixture(scope='function')
def session_browser(chrome_driver):
    yield Browser(Config(driver=chrome_driver))


@pytest.fixture(scope='function')
def function_browser(request):
    if request.config.getoption('--headless', True):
        chrome_driver = webdriver.Chrome(
            options=headless_chrome_options(),
            service=ChromeService(
                support._extensions.webdriver_manager.patch._to_find_chromedrivers_from_115(
                    ChromeDriverManager(chrome_type=ChromeType.GOOGLE)
                ).install()
            ),
        )
    else:
        chrome_driver = webdriver.Chrome(
            service=ChromeService(
                support._extensions.webdriver_manager.patch._to_find_chromedrivers_from_115(
                    ChromeDriverManager(chrome_type=ChromeType.GOOGLE)
                ).install()
            )
        )
    yield Browser(Config(driver=chrome_driver))
    chrome_driver.quit()
