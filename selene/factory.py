import atexit

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

import selene
from selene.browsers import Browser
import selene.tools


def _get_shared_driver():
    return selene.driver._shared_web_driver_source.driver


def is_driver_initialized(name):
    try:
        return _get_shared_driver().name == name
    except AttributeError:
        return False


def start_browser(name):
    if is_driver_initialized(name):
        return _get_shared_driver()

    atexit._run_exitfuncs()
    if name == Browser.CHROME:
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
    elif name == Browser.MARIONETTE:
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    else:
        driver = webdriver.Firefox()
    atexit.register(driver.quit)
    selene.tools.set_driver(driver)
    return driver
