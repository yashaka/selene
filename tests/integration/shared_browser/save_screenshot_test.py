# MIT License
#
# Copyright (c) 2015-2022 Iakiv Kramarenko
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
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

from selene import have, be
from selene.core.exceptions import TimeoutException
from selene.support.shared import browser, config
from tests.helpers import headless_chrome_options


EMPTY_PAGE_URL = (
    'file://'
    + os.path.abspath(os.path.dirname(__file__))
    + '/../../resources/empty.html'
)

ORIGINAL_DEFAULT_SCREENSHOT_FOLDER = config.reports_folder
ORIGINAL_TIMEOUT = config.timeout


def setup_function():
    config.reports_folder = ORIGINAL_DEFAULT_SCREENSHOT_FOLDER
    config.timeout = ORIGINAL_TIMEOUT


def setup_module():
    browser.config.driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
        ),
        options=headless_chrome_options(),
    )


def teardown_module():
    browser.driver.quit()


def get_default_screenshot_folder():
    return config.reports_folder


def get_screen_id():
    return next(config.counter) - 1


def test_can_make_screenshot_with_default_name():
    browser.open(EMPTY_PAGE_URL)

    actual = browser.save_screenshot()

    expected = os.path.join(
        get_default_screenshot_folder(),
        f'{get_screen_id()}.png',
    )
    assert actual == expected
    assert os.path.exists(actual)
    assert os.path.isfile(actual)


def test_can_make_screenshot_with_custom_name_with_empty_path():
    browser.open(EMPTY_PAGE_URL)

    actual = browser.save_screenshot(file="custom.png")

    expected = 'custom.png'
    assert actual == expected
    assert os.path.exists(actual)
    assert os.path.isfile(actual)


def test_can_save_screenshot_to_custom_folder_with_custom_name():
    file = (
        os.path.dirname(os.path.abspath(__file__))
        + f'/../../build/screenshots_{next(browser.config.counter)}/custom.png'
    )
    browser.open(EMPTY_PAGE_URL)

    actual = browser.save_screenshot(file=file)

    expected = file
    assert actual == expected
    assert os.path.exists(actual)
    assert os.path.isfile(actual)


def test_can_make_screenshot_with_custom_folder_specified_as_parameter_with_empty_filename():
    screenshot_folder = (
        os.path.dirname(os.path.abspath(__file__))
        + f'/../../build/screenshots_{next(browser.config.counter)}'
    )
    browser.open(EMPTY_PAGE_URL)

    actual = browser.save_screenshot(file=screenshot_folder)

    expected = os.path.join(
        screenshot_folder,
        f'{get_screen_id()}.png',
    )
    assert actual == expected
    assert os.path.exists(actual)
    assert os.path.isfile(actual)


def test_can_save_screenshot_to_custom_folder_specified_through_config():
    config.reports_folder = (
        os.path.dirname(os.path.abspath(__file__))
        + f'/../../build/screenshots_{next(browser.config.counter)}'
    )
    browser.open(EMPTY_PAGE_URL)

    actual = browser.save_screenshot()

    expected = os.path.join(
        get_default_screenshot_folder(),
        f'{get_screen_id()}.png',
    )
    assert expected == actual
    assert os.path.isfile(actual)
    assert os.path.exists(actual)


def test_can_make_screenshot_automatically():
    browser.open(EMPTY_PAGE_URL)
    config.timeout = 0.1

    with pytest.raises(TimeoutException):
        browser.element("#selene_link").should(have.exact_text("Selen site"))

    expected = os.path.join(
        get_default_screenshot_folder(),
        f'{get_screen_id()}.png',
    )
    assert os.path.exists(expected)
    assert os.path.isfile(expected)


def test_can_get_last_screenshot_path():
    config.reports_folder = (
        os.path.dirname(os.path.abspath(__file__))
        + f'/../../build/screenshots_{next(browser.config.counter)}'
    )
    browser.open(EMPTY_PAGE_URL)
    config.timeout = 0.1

    with pytest.raises(TimeoutException):
        browser.element("#s").should(be.visible)

    picture = browser.last_screenshot
    expected = os.path.join(config.reports_folder, f'{get_screen_id()}.png')
    assert picture == expected
    assert os.path.exists(picture)
    assert os.path.isfile(picture)


def test_can_get_latest_screenshot_path():
    config.reports_folder = (
        os.path.dirname(os.path.abspath(__file__))
        + f'/../../build/screenshots_{next(browser.config.counter)}'
    )
    browser.open(EMPTY_PAGE_URL)
    config.timeout = 0.1

    with pytest.raises(TimeoutException):
        browser.element("#s").should(be.visible)

    picture = browser.last_screenshot
    expected = os.path.join(config.reports_folder, f'{get_screen_id()}.png')
    assert picture == expected
    assert os.path.exists(picture)
    assert os.path.isfile(picture)
