from selene import *
from selene.conditions import text, texts, hidden, css_class, size


def setup_module():
    settings.screenshot_on_element_fail = False


def test_create_task():
    tasks = ss(".todo-list>li")
    active = css_class("active")
    completed = css_class("completed")

    visit("http://todomvc.com/examples/troopjs_require/#/", False)

    for task_text in ["1", "2", "3"]:
        s(".new-todo").set(task_text).press_enter()
    tasks.insist(texts("1", "2", "3")).insist_each(active)
    s(".todo-count").insist(text(3))

    tasks[2].s(".toggle").click()
    tasks.filter(active).insist(texts("1", "2"))
    tasks.filter(active).insist(size(2))
    tasks.filter(completed).insist(texts("3"))

    s(".filters a[href='#/active']").click()
    tasks[:2].insist(texts("1", "2"))
    tasks[2].insist(hidden)
