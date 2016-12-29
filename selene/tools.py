from selenium.webdriver.remote.webdriver import WebDriver

import selene.driver
from selene import config
from selene.elements import SeleneElement, SeleneCollection
import selene.factory


def quit_driver():
    get_driver().quit()


def set_driver(driver):
    # type: (WebDriver) -> None
    selene.driver._shared_web_driver_source.driver = driver
    config.browser_name = driver.name


def get_driver():
    # type: () -> WebDriver
    return selene.factory.start_browser(selene.config.browser_name)


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
    get_driver().get(config.app_host + absolute_or_relative_url)


def s(css_selector_or_by):
    # return SElement(css_selector_or_locator)
    return SeleneElement.by_css_or_by(css_selector_or_by, selene.driver._shared_driver)


element = s


def ss(css_selector_or_by):
    # return SElementsCollection(css_selector_or_locator, of=of)
    return SeleneCollection.by_css_or_by(css_selector_or_by, selene.driver._shared_driver)


elements = ss
