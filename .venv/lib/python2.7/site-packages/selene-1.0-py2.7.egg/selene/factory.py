import atexit

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

import selene
from selene.browsers import Browser


def is_driver_initialized(name):
    try:
        return selene.tools.get_driver().name == name
    except AttributeError:
        return False


def start_browser(name):
    if is_driver_initialized(name):
        return selene.tools.get_driver()

    atexit._run_exitfuncs()
    if name == Browser.CHROME:
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
    else:
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    atexit.register(driver.quit)
    selene.tools.set_driver(driver)
