import logging
import os

import itertools
from selenium.webdriver.remote.webdriver import WebDriver

import selene.driver
import selene.factory
from selene import config
from selene.elements import SeleneElement, SeleneCollection

counter = itertools.count()


def quit_driver():
    get_driver().quit()


def set_driver(driver):
    # type: (WebDriver) -> None
    if selene.factory.is_another_driver(driver):
        selene.factory.kill_all_started_drivers()
    selene.factory.set_shared_driver(driver)


def get_driver():
    # type: () -> WebDriver
    return selene.factory.ensure_driver_started(selene.config.browser_name)


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


def make_screenshot(filename="screen"):
    id = next(counter)
    screen_dir = config.screenshot_folder
    screenshot_path = "{path}/{name}_{id}.png".format(path=screen_dir,
                                                      name=filename,
                                                      id=id)
    if not os.path.exists(screen_dir):
        os.makedirs(screen_dir)

    get_driver().get_screenshot_as_file(screenshot_path)
    #logging.warning("\nScreenshot saved to {}".format(screenshot_path))
    return screenshot_path
