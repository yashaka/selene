import os

from selenium.webdriver.remote.webdriver import WebDriver

import selene.driver
import selene.factory
import selene.config
from selene.elements import SeleneElement, SeleneCollection
from selene.wait import wait_for


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
    get_driver().get(selene.config.app_host + absolute_or_relative_url)


def s(css_selector_or_by):
    # return SElement(css_selector_or_locator)
    return SeleneElement.by_css_or_by(css_selector_or_by, selene.driver._shared_driver)


element = s


def ss(css_selector_or_by):
    # return SElementsCollection(css_selector_or_locator, of=of)
    return SeleneCollection.by_css_or_by(css_selector_or_by, selene.driver._shared_driver)


elements = ss


def take_screenshot(path=None, filename=None):
    if not path:
        path = selene.config.screenshot_folder
    if not filename:
        filename = "screen_{id}".format(id=next(selene.config.counter))
    screenshot_path = "{path}/{name}.png".format(path=path,
                                                 name=filename)
    folder = os.path.dirname(screenshot_path)
    if not os.path.exists(folder):
        os.makedirs(folder)

    get_driver().get_screenshot_as_file(screenshot_path)
    return screenshot_path


# todo: consider adding aliases, like: wait_until, wait_brhwser_to
def wait_to(webdriver_condition, timeout=None, polling=None):
    if timeout is None:
        timeout = selene.config.timeout
    if polling is None:
        polling = selene.config.poll_during_waits

    return wait_for(get_driver(), webdriver_condition, timeout, polling)


def execute_script(script, *args):
    return get_driver().execute_script(script, *args)
