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
import pytest

from selene import Browser, _Config
from tests.integration.helpers import givenpage


def test_changes_window_size_on_open_according_to_config(chrome_driver):
    browser = Browser(_Config())
    browser.config.window_width = 640
    browser.config.window_height = 480

    browser.open(givenpage.EMPTY_PAGE_URL)

    assert browser.driver.get_window_size()['width'] == 640
    assert browser.driver.get_window_size()['height'] == 480


@pytest.fixture(scope='function')
def reset_window_size_afterwards():
    yield

    from selene import browser, Config

    browser.config.window_width = Config().window_width
    browser.config.window_height = Config().window_height


def test_changes_window_size_on_shared_browser_open_according_to_config(
    chrome_driver, reset_window_size_afterwards
):
    from selene import browser

    browser.config.window_width = 640
    browser.config.window_height = 480

    browser.open(givenpage.EMPTY_PAGE_URL)

    assert browser.driver.get_window_size()['width'] == 640
    assert browser.driver.get_window_size()['height'] == 480
