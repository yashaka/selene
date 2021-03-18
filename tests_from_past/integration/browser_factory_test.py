# MIT License
#
# Copyright (c) 2015-2021 Iakiv Kramarenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os

import pytest

import selene
import selene.api.past.driver

from selene.api.past import config, factory
from selene.api.past import BrowserName
from selene.common.none_object import NoneObject
from selene.api.past import driver, set_driver, open_url

from tests_from_past.past.acceptance import get_test_driver

start_page = (
    'file://'
    + os.path.abspath(os.path.dirname(__file__))
    + '/../resources/start_page.html'
)


@pytest.mark.parametrize("browser_name", ["marionette", "chrome"])
def x_test_factory_can_start_browser_maximized(browser_name):
    webdriver = factory._start_driver(browser_name)
    assert webdriver.name == browser_name


@pytest.mark.parametrize("browser_name", ["marionette", "chrome"])
def x_test_ensure_driver_started(browser_name):
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
    assert factory.driver_has_started("marionette") is False


def test_ensure_driver_has_started():
    driver = factory.ensure_driver_started("chrome")
    assert driver.name == "chrome"


def x_test_ensure_driver_has_started_with_marionette():
    driver = factory.ensure_driver_started("marionette")
    assert driver.name == "firefox"


def test_can_get_set_shared_driver():
    selene.api.past.driver._shared_web_driver_source.driver = NoneObject(
        "NoneObject"
    )
    shared_driver = factory.get_shared_driver()
    assert isinstance(shared_driver, NoneObject)
    factory.set_shared_driver(get_test_driver())
    shared_driver = factory.get_shared_driver()
    assert shared_driver.name == "chrome"
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
