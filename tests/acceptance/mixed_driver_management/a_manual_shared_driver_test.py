# MIT License
#
# Copyright (c) 2015-2020 Iakiv Kramarenko
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
from webdriver_manager.chrome import ChromeDriverManager

from selene.support.conditions import have
from selene.support.shared import browser, config

todomvc_url = 'https://todomvc4tasj.herokuapp.com/'
is_TodoMVC_loaded = 'return (Object.keys(require.s.contexts._.defined).length === 39)'


def setup_module():
    config.driver = webdriver.Chrome(
        ChromeDriverManager().install())  # todo: was firefox here... should it be here?


def teardown_module():
    browser.driver.quit()


def test_add_tasks():
    browser.open(todomvc_url)
    browser.should(have.js_returned(True, is_TodoMVC_loaded))

    browser.element('#new-todo').set_value('a').press_enter()
    browser.element('#new-todo').set_value('b').press_enter()
    browser.element('#new-todo').set_value('c').press_enter()

    browser.all("#todo-list>li").should(have.texts('a', 'b', 'c'))
