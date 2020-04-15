# MIT License
#
# Copyright (c) 2015-2019 Iakiv Kramarenko
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
from selene import Config, be, command, have
from selene.core.exceptions import TimeoutException
from selene.support.jquery_style_selectors import s
from selene.support.shared import browser


# def test_basic_case():
#     browser.open('http://todomvc4tasj.herokuapp.com/')
#     browser.element('#new-todo').perform(command.js.type(' lk@ї\nи₴"j;k*7 \n')).press_enter()


# def kuku_hook(error):
#     msg = error.msg.replace('file://', 'KUKU')
#     return TimeoutException(msg)
#
#
# def test_scrn():
#     browser.config.hook_wait_failure = kuku_hook
#
#     browser.open("https://google.com")
#     s("child").with_(Config(timeout=4)).should(be.visible)


# def test_collected():
#     browser.open('http://todomvc.com/examples/emberjs/')
#     browser.element('#new-todo').type('a').press_enter()
#     browser.all('li').collected(lambda its: its.element('.toggle'))\
#         .should(have.size(4))


# def test_temp():
    # browser.open('http://todomvc.com/examples/emberjs/')
    # browser.open('https://todomvc4tasj.herokuapp.com/')
    # is_todo_mvc_loaded = 'return (Object.keys(require.s.contexts._.defined).length === 39)'
    # browser.with_(timeout=browser.config.timeout*4).should(have.js_returned_true(is_todo_mvc_loaded))

    # browser.element('#new-todo').type('a').press_enter()
    # browser.all('#task-list>li').element_by(have.exact_text('a.')).double_click()
    # browser.all('#todo-list>li').element_by(have.exact_text('a.')).double_click()
    # browser.element('//*[@id="task-list"]//li[.//text()="a"]').double_click()
    # browser.all('#todo-list>li').element_by(have.exact_text('a')).double_click()\
    #     .type("b").press_enter()

    # browser.element('#new-todo').type('first task').press_enter()
    # browser.element('#new-todo').type('a').press_enter()
    # browser.all('#todo-list>li').should(have.exact_texts('first task', 'a'))
    #
    # browser.all('#todo-list>li').element_by(have.exact_text('a')).double_click()
    # browser.element('.edit').type('b').press_enter()

    # browser.element('#new-todo').with_(Config(timeout=2)).should(have.value('foo'))
    # browser.all('#todo-list>li').should(have.exact_texts('a'))

