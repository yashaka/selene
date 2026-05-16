# MIT License
#
# Copyright (c) 2015-2022 Iakiv Kramarenko
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

import pytest
from selenium.webdriver.common.keys import Keys

from selene import have, query
from tests.integration.helpers.givenpage import GivenPage


def test_element_execute_script_variants_and_deprecated_private_alias(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body("""
        <input id='name' value='old'/>
        """)
    element = session_browser.element('#name')

    element.execute_script('element.value = arguments[0]', 'new')
    element.should(have.value('new'))

    with pytest.warns(DeprecationWarning):
        element._execute_script('element.value = args[0]', 'legacy')
    element.should(have.value('legacy'))


def test_element_set_type_send_keys_press_and_clear(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body("""
        <input id='field'/>
        """)
    field = session_browser.element('#field')

    field.set_value('ab')
    field.type('cd')
    field.send_keys(Keys.BACKSPACE)
    field.press('!')
    field.should(have.value('abc!'))

    field.press_tab()
    field.press_escape()
    field.clear()
    field.should(have.value(''))


def test_element_set_alias_and_press_enter(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body("""
        <form id='form' onsubmit="event.preventDefault(); document.getElementById('status').textContent='submitted';">
          <input id='field'/>
        </form>
        <div id='status'>idle</div>
        """)
    field = session_browser.element('#field')

    field.set('hello').press_enter()
    session_browser.element('#status').should(have.exact_text('submitted'))


def test_element_submit_click_double_context_and_hover(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body("""
        <style>
          #hover-target.hovered { outline: 2px solid red; }
        </style>
        <form id='form' onsubmit="event.preventDefault(); document.getElementById('status').textContent='submitted';">
          <input id='field'/>
          <button id='submit' type='submit'>Submit</button>
        </form>
        <div id='status'>idle</div>
        <button id='clickable'
                onclick="window.__clicks=(window.__clicks||0)+1"
                ondblclick="window.__dbl=(window.__dbl||0)+1"
                oncontextmenu="event.preventDefault(); window.__ctx=(window.__ctx||0)+1">Click me</button>
        <div id='hover-target' onmouseover="this.classList.add('hovered')">Hover me</div>
        """)

    session_browser.element('#field').type('value')
    session_browser.element('#form').submit()
    session_browser.element('#status').should(have.exact_text('submitted'))

    clickable = session_browser.element('#clickable')
    clickable.click()
    clickable.double_click()
    clickable.context_click()

    assert session_browser.driver.execute_script('return window.__clicks') >= 1
    assert session_browser.driver.execute_script('return window.__dbl') == 1
    assert session_browser.driver.execute_script('return window.__ctx') == 1

    session_browser.element('#hover-target').hover()
    session_browser.element('#hover-target').should(have.css_class('hovered'))


def test_element_relative_search_aliases_and_cached_lookup(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body("""
        <section id='root'>
          <ul>
            <li class='item'>one</li>
            <li class='item'>two</li>
          </ul>
        </section>
        """)

    root = session_browser.element('#root')
    root.s('ul').ss('.item').should(have.exact_texts('one', 'two'))

    second = root.element('ul').all('.item').second.cached
    assert second.get(query.text) == 'two'
