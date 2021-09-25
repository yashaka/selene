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

from selene import have, be
from selene.core.exceptions import TimeoutException
from selene.support.shared import browser, config

EMPTY_PAGE_URL = (
    'file://'
    + os.path.abspath(os.path.dirname(__file__))
    + '/../../resources/empty.html'
)


def get_default_screenshot_folder():
    return config.reports_folder


def get_screen_id():
    return next(config.counter) - 1


def test_can_make_screenshot_with_default_name():
    browser.open(EMPTY_PAGE_URL)

    actual = browser.take_screenshot()

    expected = os.path.join(
        get_default_screenshot_folder(),
        f'{get_screen_id()}.png',
    )
    assert actual == expected
    assert os.path.exists(actual)
    assert os.path.isfile(actual)


def test_can_make_screenshot_with_custom_name_with_empty_path():
    browser.open(EMPTY_PAGE_URL)

    actual = browser.take_screenshot(filename="custom.png")

    expected = 'custom.png'
    assert actual == expected
    assert os.path.exists(actual)
    assert os.path.isfile(actual)


def test_can_save_screenshot_to_custom_folder_with_custom_name():
    screenshot_folder = (
        os.path.dirname(os.path.abspath(__file__))
        + '/../../build/screenshots_0'
    )
    browser.open(EMPTY_PAGE_URL)

    actual = browser.take_screenshot(
        path=screenshot_folder, filename="custom.png"
    )

    expected = os.path.join(
        screenshot_folder, 'custom.png'
    )
    assert actual == expected
    assert os.path.exists(actual)
    assert os.path.isfile(actual)


def test_can_make_screenshot_with_custom_folder_specified_as_parameter_with_empty_filename():
    screenshot_folder = (
        os.path.dirname(os.path.abspath(__file__))
        + '/../../build/screenshots_1'
    )
    browser.open(EMPTY_PAGE_URL)

    actual = browser.take_screenshot(path=screenshot_folder)

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
        + '/../../build/screenshots_2'
    )
    browser.open(EMPTY_PAGE_URL)

    actual = browser.take_screenshot()

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

    with pytest.raises(TimeoutException) as ex:
        browser.element("#selene_link").should(have.exact_text("Selen site"))

    expected = os.path.join(
        get_default_screenshot_folder(),
        f'{get_screen_id()}.png',
    )
    assert os.path.exists(expected)
    assert os.path.isfile(expected)


def test_can_get_latest_screenshot_path():
    config.reports_folder = (
        os.path.dirname(os.path.abspath(__file__)) + '/../../build/screenshots'
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
