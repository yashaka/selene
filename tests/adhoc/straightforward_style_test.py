# MIT License
#
# Copyright (c) 2015-2021 Iakiv Kramarenko
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
    # config.browser_name = 'firefox'  # chrome was default

    tasks = ss('#todo-list>li').with_(timeout=config.timeout / 2)
    active_tasks = tasks.filtered_by(have.css_class('active'))

    customized = browser.with_(timeout=config.timeout * 2)
    customized.open('https://todomvc4tasj.herokuapp.com/')
    # open_url('https://www.yahoo.com/')  # or like this
    # browser.driver.get('http://google.com')  # just in case, you can use the driver directly too
    # browser.driver().get('https://todomvc4tasj.herokuapp.com/')  # temporary this works too;)
    is_todo_mvc_loaded = (
        'return (Object.keys(require.s.contexts._.defined).length === 39)'
    )
    browser.with_(timeout=config.timeout * 4).should(
        have.js_returned(True, is_todo_mvc_loaded)
    )  # todo: make it work

    for text in ['1', '2', '3']:
        s('#new-todo').type(text).should(
            have.no.value('')
        ).press_enter().should(
            have.attribute('value').value('')
        )  # todo: ensure autocomplete works here too...
    tasks.should(have.texts('1', '2', '3')).should(have.css_class('active'))
    browser.element('#todo-count').should(have.text('3'))

    tasks[2].s('.toggle').click()
    active_tasks.should(have.texts('1', '2'))
    active_tasks.should(have.no.texts('1', '2', '3'))
    active_tasks.should(have.size(2))

    tasks.filtered_by(have.css_class('completed')).should(have.texts('3'))
    tasks.element_by(not_(have.css_class('completed'))).should(have.text('1'))
    # or
    tasks.element_by(have.no.css_class('completed')).should(have.text('1'))
    tasks.filtered_by(have.no.css_class('completed')).should(
        have.texts('1', '2')
    )

    s(by.link_text('Active')).click()
    tasks[:2].should(have.texts('1', '2'))
    tasks[2].should(be.hidden)  # same as: ...
    tasks[2].should(be.not_.visible)

    tasks.collected(lambda task: task.all('label')).should(
        have.texts('1', '2')
    )
    # tasks.all('label').should(have.texts('1', '2'))

    tasks.collected(lambda task: task.element('label')).should(
        have.texts('1', '2')
    )
    # tasks.all_first('label').should(have.texts('1', '2'))

    s(by.id('toggle-all')).with_(timeout=config.timeout / 2).click()
    # browser.actions.click(s('//*[@id="clear-completed"]')()).perform()
    s('//*[@id="clear-completed"]').click()
    tasks.should(have.size(0))
