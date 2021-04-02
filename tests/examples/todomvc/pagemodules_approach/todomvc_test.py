# MIT License
#
# Copyright (c) 2015-2021 Iakiv Kramarenko
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
from selene.support.shared import browser
from tests.examples.todomvc.pagemodules_approach.pages import tasks


class TestTodoMVC:
    def teardown(self):
        browser.execute_script('localStorage.clear()')

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
