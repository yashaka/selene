import os

from selenium.webdriver.remote.webdriver import WebDriver

import selene.config
import selene.driver
import selene.factory
from selene import helpers
from selene.common.none_object import NoneObject
from selene.elements import SeleneElement, SeleneCollection
from selene.wait import wait_for


def quit_driver():
    driver().quit()


def quit():
    quit_driver()


def close():
    driver().close()


def set_driver(webdriver):
    # type: (WebDriver) -> None
    if selene.factory.is_another_driver(webdriver):
        selene.factory.kill_all_started_drivers()
    selene.factory.set_shared_driver(webdriver)


def driver():
    # type: () -> WebDriver
    return selene.factory.ensure_driver_started(selene.config.browser_name)


def open_url(absolute_or_relative_url):
    """
    Loads a web page in the current browser session.
    :param absolgenerateute_or_relative_url:
        an absolute url to web page in case of config.base_url is not specified,
        otherwise - relative url correspondingly

    :Usage:
        open_url('http://mydomain.com/subpage1')
        open_url('http://mydomain.com/subpage2')
        # OR
        config.base_url = 'http://mydomain.com'
        open_url('/subpage1')
        open_url('/subpage2')
    """
    # todo: refactor next line when app_host is removed
    base_url = selene.config.app_host if selene.config.app_host else selene.config.base_url
    driver().get(base_url + absolute_or_relative_url)


def element(css_selector_or_by):
    return SeleneElement.by_css_or_by(css_selector_or_by, selene.driver._shared_driver)


def elements(css_selector_or_by):
    return SeleneCollection.by_css_or_by(css_selector_or_by, selene.driver._shared_driver)

def all(css_selector_or_by):
    return elements(css_selector_or_by)


latest_screenshot = NoneObject("selene.browser._latest_screenshot")


def take_screenshot(path=None, filename=None):
    if not path:
        path = selene.config.reports_folder
    if not filename:
        filename = "screen_{id}".format(id=next(selene.config.counter))

    screenshot_path = helpers.take_screenshot(driver(), path, filename)

    global _latest_screenshot
    _latest_screenshot = screenshot_path

    return screenshot_path


# todo: consider adding aliases, like: wait_until, wait_brhwser_to
def wait_to(webdriver_condition, timeout=None, polling=None):
    if timeout is None:
        timeout = selene.config.timeout
    if polling is None:
        polling = selene.config.poll_during_waits

    return wait_for(driver(), webdriver_condition, timeout, polling)


def should(webdriver_condition, timeout=None, polling=None):
    return wait_to(webdriver_condition, timeout, polling)


def execute_script(script, *args):
    return driver().execute_script(script, *args)


def title():
    return driver().title
