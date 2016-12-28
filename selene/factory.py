import atexit

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from selene.browsers import Browser
from selene.tools import get_driver, set_driver


def is_driver_initialized(name):
    try:
        return get_driver().name == name
    except AttributeError:
        return False


def start_browser(name):
    if is_driver_initialized(name):
        return get_driver()

    if name == Browser.CHROME:
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
    else:
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    atexit.register(driver.quit)
    set_driver(driver)
