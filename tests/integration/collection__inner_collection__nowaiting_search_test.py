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
from tests.integration.helpers.givenpage import GivenPage


def test_does_not_wait_inner(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_empty()
    elements = session_browser.element('ul').all('.will-appear')

    page.load_body(
        '''
        <ul>Hello to:
            <li class='will-appear'>Bob</li>
            <li class='will-appear' style='display:none'>Kate</li>
        </ul>'''
    )

    assert len(elements) == 2

    page.load_body_with_timeout(
        '''
        <ul>Hello to:
            <li class='will-appear'>Bob</li>
            <li class='will-appear' style='display:none'>Kate</li>
            <li class='will-appear'>Joe</li>
        </ul>''',
        500,
    )

    assert len(elements) == 2


def test_waits_for_parent_in_dom_then_visible(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_empty()
    elements = session_browser.element('#will-appear').all('.item')

    page.load_body(
        '''
        <li class='item'>Bob</li>
        <li class='item' style='display:none'>Kate</li>'''
    )

    page.load_body_with_timeout(
        '''
        <ul id='will-appear' style="display:none">Hello to:
            <li class='item'>Bob</li>
            <li class='item' style='display:none'>Kate</li>
        </ul>''',
        250,
    ).execute_script_with_timeout(
        'document.getElementsByTagName("ul")[0].style = "display:block";', 500
    )

    assert len(elements) == 2
