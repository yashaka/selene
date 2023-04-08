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
import atexit
import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # type: ignore
from webdriver_manager.core.utils import ChromeType  # type: ignore

from selene import have, be, browser, Browser, Config, command
from selene.core import query
from selene.core.exceptions import TimeoutException
from tests import resources
from tests.helpers import headless_chrome_options

EMPTY_PAGE_URL = resources.url('empty.html')


@pytest.fixture(scope='module')
def the_driver():
    driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
        ),
        options=headless_chrome_options(),
    )

    yield driver

    driver.quit()


@pytest.fixture(scope='function')
def a_browser(the_driver):
    browser_ = Browser(Config(driver=the_driver, hold_driver_at_exit=True))

    yield browser_

    # ...


@pytest.fixture(scope='function')
def with_process_exit_teardown():
    # ...

    yield

    atexit._run_exitfuncs()


def test_can_make_screenshot_with_default_name(a_browser):
    a_browser.open(EMPTY_PAGE_URL)

    screenshot_path = a_browser.get(query.screenshot_saved())

    assert os.path.exists(screenshot_path)
    assert os.path.isfile(screenshot_path)
    assert screenshot_path == os.path.join(
        a_browser.config.reports_folder,
        f'{next(browser.config._counter) - 1}.png',
    )


def test_can_make_screenshot_with_custom_name_with_empty_path(a_browser):
    a_browser.open(EMPTY_PAGE_URL)

    screenshot_path = a_browser.get(query.screenshot_saved(path='custom.png'))

    assert os.path.exists(screenshot_path)
    assert os.path.isfile(screenshot_path)
    assert screenshot_path == 'custom.png'


def test_can_make_screenshot_with_custom_path_to_folder_without_png_file_name(
    a_browser,
):
    custom_folder = os.path.join(
        a_browser.config.reports_folder,
        f'custom_folder_{next(a_browser.config._counter)}',
    )
    a_browser.open(EMPTY_PAGE_URL)

    screenshot_path = a_browser.get(query.screenshot_saved(path=custom_folder))

    assert os.path.exists(screenshot_path)
    assert os.path.isfile(screenshot_path)
    assert screenshot_path == os.path.join(
        custom_folder,
        f'{next(browser.config._counter) - 1}.png',
    )


def test_can_save_screenshot_to_custom_folder_specified_through_config(
    a_browser,
):
    custom_folder = os.path.join(
        a_browser.config.reports_folder,
        f'custom_folder_{next(a_browser.config._counter)}',
    )
    a_browser.config.reports_folder = custom_folder
    a_browser.open(EMPTY_PAGE_URL)

    screenshot_path = a_browser.get(query.screenshot_saved())

    assert os.path.exists(screenshot_path)
    assert os.path.isfile(screenshot_path)
    assert screenshot_path == os.path.join(
        custom_folder,
        f'{next(a_browser.config._counter) - 1}.png',
    )


def test_saves_screenshot_on_failure(a_browser):
    a_browser.open(EMPTY_PAGE_URL)

    with pytest.raises(TimeoutException):
        a_browser.element("#selene_link").with_(timeout=0.1).should(
            have.exact_text("Selen site")
        )

    expected_path = os.path.join(
        a_browser.config.reports_folder,
        f'{next(a_browser.config._counter) - 1}.png',
    )
    assert os.path.exists(expected_path)
    assert os.path.isfile(expected_path)


def test_remembers_last_saved_screenshot(
    a_browser, with_process_exit_teardown
):
    a_browser.open(EMPTY_PAGE_URL)

    # WHEN on failure
    with pytest.raises(TimeoutException):
        a_browser.element("#does-not-exist").with_(timeout=0.1).should(
            be.visible
        )

    # assert a_browser.config.last_screenshot == os.path.join(
    assert a_browser.config.last_screenshot == os.path.join(
        a_browser.config.reports_folder,
        f'{next(a_browser.config._counter) - 1}.png',
    )

    # WHEN on explicit save
    a_browser.perform(command.save_screenshot())

    # THEN overriden
    assert a_browser.config.last_screenshot == os.path.join(
        a_browser.config.reports_folder,
        f'{next(a_browser.config._counter) - 1}.png',
    )

    # WHEN on explicit save on another browser with shared last_screenshot
    another = a_browser.with_(driver_name='firefox', hold_driver_at_exit=False)
    another.perform(command.save_screenshot())

    # THEN overriden
    assert (
        another.config.last_screenshot
        == a_browser.config.last_screenshot
        == os.path.join(
            a_browser.config.reports_folder,
            f'{next(a_browser.config._counter) - 1}.png',
        )
    )

    # WHEN on explicit save on another browser with own last_screenshot
    another = a_browser.with_(
        driver_name='firefox', hold_driver_at_exit=False, last_screenshot=None
    )
    another.perform(command.save_screenshot())

    # THEN not overriden but stored separately
    assert another.config.last_screenshot != a_browser.config.last_screenshot
    assert another.config.last_screenshot == os.path.join(
        a_browser.config.reports_folder,
        f'{next(a_browser.config._counter) - 1}.png',
    )
