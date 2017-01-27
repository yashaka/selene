import pytest

import selene
from selene import factory
from selene.browsers import Browser
from selene.common.none_object import NoneObject
from selene.tools import get_driver, set_driver
from tests.acceptance.helpers.helper import get_test_driver


@pytest.mark.parametrize("browser_name", ["firefox",
                                          "chrome"])
def test_factory_can_start_browser_maximized(browser_name):
    driver = factory._start_driver(browser_name)
    assert driver.name == browser_name


@pytest.mark.parametrize("browser_name", ["firefox",
                                          "chrome"])
def test_factory_can_create_browser(browser_name):
    factory.ensure_driver_started(browser_name)
    assert get_driver().name == browser_name


def test_can_set_browser_directly():
    driver = get_test_driver()
    set_driver(driver)
    factory.ensure_driver_started(Browser.CHROME)
    assert get_driver().name == Browser.CHROME
    get_driver().quit()
    driver.quit()


def test_is_driver_still_opened():
    driver = get_test_driver()
    assert factory.is_driver_still_open(driver)
    driver.quit()
    assert factory.is_driver_still_open(driver) is False


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
