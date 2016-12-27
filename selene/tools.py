from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

import selene.driver
from selene import config
from selene.elements import SeleneElement, SeleneCollection
import atexit


def exit():
    get_driver().quit()


def set_driver(driver):
    # type: (WebDriver) -> None
    atexit.register(exit)
    selene.driver._shared_web_driver_source.driver = driver


def get_driver():
    # type: () -> WebDriver
    return selene.driver._shared_web_driver_source.driver


def is_driver_initialized():
    try:
        get_driver().session_id
        return True
    except AttributeError:
        return False


def visit(absolute_or_relative_url):
    """
    Loads a web page in the current browser session.
    :param absolute_or_relative_url:
        an absolute url to web page in case of config.app_host is not specified,
        otherwise - relative url correspondingly

    :Usage:
        visit('http://mydomain.com/subpage1')
        visit('http://mydomain.com/subpage2')
        # OR
        config.app_host = 'http://mydomain.com'
        visit('/subpage1')
        visit('/subpage2')
    """
    if not is_driver_initialized():
        set_driver(webdriver.Firefox(executable_path=GeckoDriverManager().install()))
    get_driver().get(config.app_host + absolute_or_relative_url)


def s(css_selector_or_by):
    # return SElement(css_selector_or_locator)
    return SeleneElement.by_css_or_by(css_selector_or_by, selene.driver._shared_driver)


element = s


def ss(css_selector_or_by):
    # return SElementsCollection(css_selector_or_locator, of=of)
    return SeleneCollection.by_css_or_by(css_selector_or_by, selene.driver._shared_driver)


elements = ss
