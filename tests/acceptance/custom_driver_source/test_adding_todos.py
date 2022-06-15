# MI
# T License
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
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

from selene import by, have, Browser, Config
import pytest

from selene.support.webdriver import WebHelper


class Settings:
    driver: Optional[WebDriver] = None
    reset_driver: bool = False


@pytest.fixture(scope='module')
def web():
    def managed_driver() -> WebDriver:
        from selenium import webdriver

        def create_chrome():
            from selenium.webdriver.chrome.service import (
                Service as ChromeService,
            )

            return webdriver.Chrome(
                service=ChromeService(
                    ChromeDriverManager(
                        chrome_type=ChromeType.GOOGLE
                    ).install()
                ),
                options=webdriver.ChromeOptions(),
            )

        # if _driver and Help(_driver).has_browser_still_alive():
        #     return _driver
        #
        # _driver = create_chrome()

        if (
            Settings.reset_driver
            and Settings.driver
            and WebHelper(Settings.driver).is_browser_still_alive()
        ):
            Settings.driver.quit()
            Settings.reset_driver = False

        if (
            Settings.driver is None
            or not WebHelper(Settings.driver).is_browser_still_alive()
        ):
            Settings.driver = create_chrome()

        return Settings.driver

    browser = Browser(Config(driver=managed_driver))

    yield browser

    Settings.driver.quit()


def test_add_todo_1(web):
    web.open('https://todomvc.com/examples/emberjs/')
    web.element('#new-todo').type('a').press_enter()
    web.all('#todo-list>li').should(have.exact_texts('a'))


def test_add_todo_2_at_same_page(web):
    web.element('#new-todo').type('b').press_enter()
    web.all('#todo-list>li').should(have.exact_texts('a', 'b'))


def test_add_todo_3_at_new_page_in_fresh_browser(web):
    Settings.reset_driver = True
    assert Settings.reset_driver
    web.open('https://todomvc.com/examples/emberjs/')
    assert not Settings.reset_driver

    web.element('#new-todo').type('c').press_enter()
    web.all('#todo-list>li').should(have.exact_texts('c'))


def test_add_todo_4_at_same_page(web):
    web.element('#new-todo').type('d').press_enter()
    web.all('#todo-list>li').should(have.exact_texts('c', 'd'))
