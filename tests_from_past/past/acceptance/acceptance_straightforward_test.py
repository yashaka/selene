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

from selene.api import *

# app_url = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/todomvcapp/home.html'
from selene.api.past import not_

app_url = 'https://todomvc4tasj.herokuapp.com/'
# is_TodoMVC_loaded = ('return '
#                      '$._data($("#new-todo").get(0), "events").hasOwnProperty("keyup") && '
#                      '$._data($("#toggle-all").get(0), "events").hasOwnProperty("change") && '
#                      '$._data($("#todo-list").get(0), "events").hasOwnProperty("change") && '
#                      '$._data($("#clear-completed").get(0), "events").hasOwnProperty("click")')
is_TodoMVC_loaded = 'return (Object.keys(require.s.contexts._.defined).length === 39)'


class TestTodoMVC(object):

    def test_selene_demo(self):
        tasks = ss("#todo-list>li")
        active_tasks = tasks.filtered_by(have.css_class("active"))

        browser.open_url(app_url)
        browser.should(have.js_returned_true(is_TodoMVC_loaded))

        for task_text in ["1", "2", "3"]:
            s("#new-todo").set_value(task_text).press_enter()
        tasks.should(have.texts("1", "2", "3")).should_each(have.css_class("active"))
        s("#todo-count").should(have.text('3'))

        tasks[2].s(".toggle").click()
        active_tasks.should(have.texts("1", "2"))
        active_tasks.should(have.size(2))

        tasks.filtered_by(have.css_class("completed")).should(have.texts("3"))
        tasks.element_by(not_(have.css_class("completed"))).should(have.text("1"))
        tasks.filtered_by(not_(have.css_class("completed"))).should(have.texts("1", "2"))

        s(by.link_text("Active")).click()
        tasks[:2].should(have.texts("1", "2"))
        tasks[2].should(be.hidden)

        s(by.id("toggle-all")).click()
        s("//*[@id='clear-completed']").click()
        tasks.should(be.empty)
