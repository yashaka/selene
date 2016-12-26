from tests.base_test import *
from tests.demo.todomvc.pagemodules_approach.pages import tasks


class TestTodoMVC(BaseTest):

    def test_filter_tasks(self):

        tasks.visit()

        tasks.add("a", "b", "c")
        tasks.should_be("a", "b", "c")

        tasks.toggle("b")

        tasks.filter_active()
        tasks.should_be("a", "c")

        tasks.filter_completed()
        tasks.should_be("b")


