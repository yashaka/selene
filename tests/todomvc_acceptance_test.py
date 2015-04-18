from selene.conditions import text, texts, absent
from selene.tools import *


def test_create_task():
    tasks = ss("#todo-list>li")

    visit("http://todomvc.com/examples/troopjs_require/#/")

    for task_text in ["1", "2", "3"]:
        s("#new-todo").set(task_text).press_enter()
    tasks.insist(texts("1", "2", "3"))
    s("#todo-count").insist(text(3))

    tasks[2].s(".toggle").click()
    s("#filters a[href='#/active']").click()

    tasks[:2].insist(texts("1", "2"))
    tasks[2].insist(absent)
