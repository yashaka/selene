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

import os

from selene import be, have
from selene.support.shared import browser

# TODOMVC_URL = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../../resources/todomvcapp/home.html'
TODOMVC_URL = 'https://todomvc4tasj.herokuapp.com/'
OTHER_PAGE_URL = 'file://{}/../resources/orderapp/order.html'.format(
    os.path.abspath(os.path.dirname(__file__))
)
is_TodoMVC_loaded = (
    'return (Object.keys(require.s.contexts._.defined).length === 39)'
)


def open_todomvc():
    # todo: refactor to use repo copy of todomvc
    browser.open(TODOMVC_URL)
    browser.wait_until(have.js_returned(True, is_TodoMVC_loaded))


def given_at_other_page():
    if not browser.element("#order_details").matching(be.visible):
        browser.open(OTHER_PAGE_URL)


def execute_js(js_string):
    return browser.execute_script(js_string)


def given(*tasks):
    if not browser.element("#new-todo").matching(be.visible):
        open_todomvc()

    import json

    script = 'localStorage.setItem("todos-troopjs", "{}")'.format(
        str(json.dumps(tasks))
        .replace('"', '\\"')
        .replace('\\\\"', '\\\\\\"')
        .replace("False", "false")
    )

    execute_js(script)

    open_todomvc()


def given_empty_tasks():
    given()


def task(task_text, is_completed=False):
    return dict(title=task_text, completed=is_completed)


def given_active(*task_texts):
    return given(*[task(text) for text in task_texts])


when_active = given_active
