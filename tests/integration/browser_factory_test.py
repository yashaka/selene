import os

import pytest

import selene
import selene.driver

from selene import config
from selene import factory
from selene.browsers import BrowserName
from selene.common.none_object import NoneObject
from selene.browser import driver, set_driver, open_url

from tests.acceptance.helpers.helper import get_test_driver

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


@pytest.mark.parametrize("browser_name", ["firefox",
                                          "chrome"])
def test_factory_can_start_browser_maximized(browser_name):
    webdriver = factory._start_driver(browser_name)
    assert webdriver.name == browser_name


@pytest.mark.parametrize("browser_name", ["firefox",
                                          "chrome"])
def test_ensure_driver_started(browser_name):
    factory.ensure_driver_started(browser_name)
    assert driver().name == browser_name


def test_ensure_driver_started__when__set_browser_directly():
    webdriver = get_test_driver()
    set_driver(webdriver)
    factory.ensure_driver_started(BrowserName.CHROME)
    assert driver().name == BrowserName.CHROME
    driver().quit()


def test_is_driver_still_opened():
    webdriver = get_test_driver()
    assert factory.is_driver_still_open(webdriver)
    webdriver.quit()
    assert factory.is_driver_still_open(webdriver) is False


def test_driver_has_started():
    factory._start_driver("chrome")
    assert factory.driver_has_started("chrome")
    assert factory.driver_has_started("firefox") is False


def test_ensure_driver_has_started():
    driver = factory.ensure_driver_started("chrome")
    assert driver.name == "chrome"


def test_can_get_set_shared_driver():
    selene.driver._shared_web_driver_source.driver = NoneObject("NoneObject")
    shared_driver = factory.get_shared_driver()
    assert isinstance(shared_driver, NoneObject)
    factory.set_shared_driver(get_test_driver())
    shared_driver = factory.get_shared_driver()
    assert shared_driver.name == "firefox"
    shared_driver.quit()


def test_can_hold_autocreated_browser_open():
    config.hold_browser_open = True
    open_url(start_page)
    webdriver = driver()
    factory.kill_all_started_drivers()
    assert factory.is_driver_still_open(webdriver)
    webdriver.quit()


def test_can_auto_close_browser():
    config.hold_browser_open = False
    open_url(start_page)
    webdriver = driver()
    factory.kill_all_started_drivers()
    assert factory.is_driver_still_open(webdriver) is False

