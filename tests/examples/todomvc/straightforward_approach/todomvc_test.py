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
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selene import have, be, by, browser, support
from selene.support._extensions.webdriver_manager import ChromeType


def setup_module():
    browser.config.driver = webdriver.Chrome(
        service=Service(
            support._extensions.webdriver_manager.patch._to_find_chromedrivers_from_115(
                ChromeDriverManager(chrome_type=ChromeType.GOOGLE)
            ).install()
        )
    )
    browser.config.timeout = 4


def teardown_module():
    browser.quit()


class TestTodoMVC:
    def test_filter_tasks(self):
        browser.open('https://todomvc4tasj.herokuapp.com/')
        clear_completed_js_loaded = "return $._data($('#clear-completed').get(0), 'events').hasOwnProperty('click')"
        browser.wait.for_(have.script_returned(True, clear_completed_js_loaded))
        browser.wait.for_(have.title('TroopJS • TodoMVC'))

        browser.element('#new-todo').should(be.enabled).set_value('a').press_enter()
        browser.element('#new-todo').should(be.enabled).set_value('b').press_enter()
        browser.element('#new-todo').should(be.enabled).set_value('c').press_enter()

        browser.all("#todo-list>li").should(have.texts('a', 'b', 'c'))

        browser.all("#todo-list>li").element_by(have.exact_text('b')).element(
            ".toggle"
        ).click()

        browser.element(by.link_text("Active")).click()
        browser.all("#todo-list>li").by(be.visible).should(have.texts('a', 'c'))

        browser.element(by.link_text("Completed")).click()
        browser.all("#todo-list>li").by(be.visible).should(have.texts('b'))
