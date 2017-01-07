import atexit
from time import sleep

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
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


def is_another_driver(driver):
    try:
        return get_shared_driver().session_id != driver.session_id
    except AttributeError:
        return False


def driver_has_started(name):
    try:
        shared_driver = get_shared_driver()
        return shared_driver.name == name and shared_driver.session_id
    except AttributeError:
        return False


def kill_all_started_drivers():
    atexit._run_exitfuncs()


def ensure_driver_started(name):
    if driver_has_started(name):
        return get_shared_driver()

    return _start_driver(name)


def _start_driver(name):
    kill_all_started_drivers()
    if name == Browser.CHROME:
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
    elif name == Browser.MARIONETTE:
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    else:
        driver = webdriver.Firefox()
    set_shared_driver(driver)
    _register_driver(driver)
    return driver



def _register_driver(driver):
    atexit.register(driver.quit)
