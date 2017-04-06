import os
import warnings

from selenium.webdriver.remote.webdriver import WebDriver

import selene.driver
import selene.factory
import selene.config
from selene.common.none_object import NoneObject
from selene.elements import SeleneElement, SeleneCollection

from selene.wait import wait_for


def quit_driver():
    warnings.warn("use selene.browser.quit() instead", DeprecationWarning)
    get_driver().quit()


def set_driver(driver):
    # type: (WebDriver) -> None
    warnings.warn("use selene.browser.set_driver(webdriver) instead", DeprecationWarning)
    if selene.factory.is_another_driver(driver):
        selene.factory.kill_all_started_drivers()
    selene.factory.set_shared_driver(driver)


def get_driver():
    # type: () -> WebDriver
    warnings.warn("use selene.browser.driver() instead", DeprecationWarning)
    return selene.factory.ensure_driver_started(selene.config.browser_name)


def visit(absolute_or_relative_url):
    """
    Loads a web page in the current browser session.
    :param absolute_or_relative_url:
        an absolute url to web page in case of config.base_url is not specified,
        otherwise - relative url correspondingly

    :Usage:
        visit('http://mydomain.com/subpage1')
        visit('http://mydomain.com/subpage2')
        # OR
        config.base_url = 'http://mydomain.com'
        visit('/subpage1')
        visit('/subpage2')
    """
    warnings.warn("use selene.browser.visit() instead", DeprecationWarning)
    # todo: refactor next line when app_host is removed
    base_url = selene.config.app_host if selene.config.app_host else selene.config.base_url
    get_driver().get(base_url + absolute_or_relative_url)


def element(css_selector_or_by):
    warnings.warn("use selene.browser.element(css_selector_or_by) instead",
                  DeprecationWarning)
    return SeleneElement.by_css_or_by(css_selector_or_by, selene.driver._shared_driver)


def s(css_selector_or_by):
    warnings.warn("use selene.support.jquery_style_selectors.s(css_selector_or_by) instead",
                  DeprecationWarning)
    return SeleneElement.by_css_or_by(css_selector_or_by, selene.driver._shared_driver)


def elements(css_selector_or_by):
    warnings.warn("use selene.browser.elements(css_selector_or_by) or selene.browser.ss(css_selector_or_by) instead",
                  DeprecationWarning)
    return SeleneCollection.by_css_or_by(css_selector_or_by, selene.driver._shared_driver)


def ss(css_selector_or_by):
    warnings.warn("use selene.support.jquery_style_selectors.ss(css_selector_or_by) instead",
                  DeprecationWarning)
    return SeleneCollection.by_css_or_by(css_selector_or_by, selene.driver._shared_driver)


_latest_screenshot = NoneObject("selene.tools._latest_screenshot")


def take_screenshot(path=None, filename=None):
    warnings.warn("use selene.browser.take_screenshot() instead", DeprecationWarning)
    if not path:
        path = selene.config.reports_folder
    if not filename:
        filename = "screen_{id}".format(id=next(selene.config.counter))
    screenshot_path = os.path.join(path,
                                   "{}.png".format(filename))

    folder = os.path.dirname(screenshot_path)
    if not os.path.exists(folder):
        os.makedirs(folder)

    get_driver().get_screenshot_as_file(screenshot_path)
    global _latest_screenshot
    _latest_screenshot = screenshot_path
    return screenshot_path


def latest_screenshot():
    warnings.warn("use selene.browser.latest_screenshot() instead", DeprecationWarning)
    return _latest_screenshot


# todo: consider adding aliases, like: wait_until, wait_brhwser_to
def wait_to(webdriver_condition, timeout=None, polling=None):
    warnings.warn("use selene.browser.wait_to(webdriver_condition, timeout, polling) instead", DeprecationWarning)
    if timeout is None:
        timeout = selene.config.timeout
    if polling is None:
        polling = selene.config.poll_during_waits

    return wait_for(get_driver(), webdriver_condition, timeout, polling)


def execute_script(script, *args):
    warnings.warn("use selene.browser.execute_script(script, *args) instead", DeprecationWarning)
    return get_driver().execute_script(script, *args)
