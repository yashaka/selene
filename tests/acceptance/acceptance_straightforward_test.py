import os
from selene.api import *


# app_url = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/todomvcapp/home.html'
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

        s(by.link_text("Active")).click()
        tasks[:2].should(have.texts("1", "2"))
        tasks[2].should(be.hidden)

        s("#toggle-all").click()
        s("#clear-completed").click()
        tasks.should(be.empty)
