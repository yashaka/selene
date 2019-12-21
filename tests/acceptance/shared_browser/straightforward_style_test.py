# MIT License
#
# Copyright (c) 2015-2019 Iakiv Kramarenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from selene.api import *


def test_selene_demo():
    # todo: uncomment and fix (fails with dataclasses.FrozenInstanceError: cannot assign to field 'timeout')
    # config.timeout = 6

    tasks = ss('#todo-list>li')
    active_tasks = tasks.filtered_by(have.css_class('active'))

    browser.open_url('https://todomvc4tasj.herokuapp.com/')
    is_todo_mvc_loaded = 'return (Object.keys(require.s.contexts._.defined).length === 39)'
    browser.should(have.js_returned_true(is_todo_mvc_loaded))

    for text in ['1', '2', '3']:
        s('#new-todo').type(text).press_enter()
    tasks.should(have.texts('1', '2', '3')).should(have.css_class('active'))
    s('#todo-count').should(have.text('3'))

    tasks[2].s('.toggle').click()
    active_tasks.should(have.texts('1', '2'))
    active_tasks.should(have.size(2))

    tasks.filtered_by(have.css_class('completed')).should(have.texts('3'))
    tasks.element_by(not_(have.css_class('completed'))).should(have.text('1'))
    tasks.filtered_by(not_(have.css_class('completed'))).should(have.texts('1', '2'))

    s(by.link_text('Active')).click()
    tasks[:2].should(have.texts('1', '2'))
    tasks[2].should(be.hidden)

    s(by.id('toggle-all')).click()
    s('//*[@id="clear-completed"]').click()
    tasks.should(be.empty)
