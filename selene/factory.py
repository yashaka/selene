import atexit

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

import selene
from selene import config
from selene.browsers import Browser
import selene.tools


def set_shared_driver(driver):
    selene.driver._shared_web_driver_source.driver = driver
    config.browser_name = driver.name


def get_shared_driver():
    return selene.driver._shared_web_driver_source.driver


def driver_has_started(name):
    try:
        return get_shared_driver().name == name
    except AttributeError:
        return False


def kill_all_started_browsers():
    atexit._run_exitfuncs()


def start_browser(name):
    if driver_has_started(name):
        return get_shared_driver()

    kill_all_started_browsers()
    if name == Browser.CHROME:
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
    elif name == Browser.MARIONETTE:
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    else:
        driver = webdriver.Firefox()
    atexit.register(driver.quit)
    selene.tools.set_driver(driver)
    return driver
