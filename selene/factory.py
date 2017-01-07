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
    driver_name = driver.name
    if not is_same_driver(driver):
        kill_all_started_drivers()
    selene.driver._shared_web_driver_source.driver = driver
    config.browser_name = driver_name


def get_shared_driver():
    return selene.driver._shared_web_driver_source.driver


def is_same_driver(driver):
    try:
        return get_shared_driver().session_id == driver.session_id
    except AttributeError:
        return False


def driver_has_started(name):
    try:
        shared_driver = get_shared_driver()
        return shared_driver.name == name
    except AttributeError:
        return False


def kill_all_started_drivers():
    atexit._run_exitfuncs()


def start_driver(name):
    if driver_has_started(name):
        return get_shared_driver()

    kill_all_started_drivers()
    if name == Browser.CHROME:
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
    elif name == Browser.MARIONETTE:
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    else:
        binary = FirefoxBinary("/home/sergey/Downloads/firefox/firefox")
        driver = webdriver.Firefox(firefox_binary=binary)
    set_shared_driver(driver)
    _register_driver(driver)
    return driver


def _register_driver(driver):
    atexit.register(driver.quit)
