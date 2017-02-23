from selene.browser import execute_script
from tests.examples.todomvc.pagemodules_approach.pages import tasks


class TestTodoMVC(object):

    def teardown(self):
        execute_script('localStorage.clear()')

    def test_filter_tasks(self):

        tasks.visit()

        tasks.add('a', 'b', 'c')
        tasks.should_be('a', 'b', 'c')

        tasks.toggle('b')

        tasks.filter_active()
        tasks.should_be('a', 'c')

        tasks.filter_completed()
        tasks.should_be('b')
        
    def test_clear_completed(self):
        tasks.visit()

        tasks.add('a', 'b', 'c')
        tasks.toggle('b')
        tasks.clear_completed()
        
        tasks.should_be('a', 'c')



