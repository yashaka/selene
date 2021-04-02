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
from selene import have
from tests.integration.helpers.givenpage import GivenPage


def test_search_is_lazy_and_does_not_start_on_creation_for_both_collection_and_indexed(
    session_browser,
):
    page = GivenPage(session_browser.driver)
    page.opened_empty()

    non_existent_element = session_browser.all('.non-existing').element_by(
        have.exact_text('Kate')
    )

    assert str(non_existent_element)


def test_search_is_postponed_until_actual_action_like_questioning_displayed(
    session_browser,
):
    page = GivenPage(session_browser.driver)
    page.opened_empty()
    element = session_browser.all('.will-appear').element_by(
        have.exact_text('Kate')
    )

    page.load_body(
        '''
                   <ul>Hello to:
                       <li class="will-appear">Bob</li>
                       <li class="will-appear">Kate</li>
                   </ul>'''
    )

    assert element().is_displayed() is True


def test_search_is_updated_on_next_actual_action_like_questioning_displayed(
    session_browser,
):
    page = GivenPage(session_browser.driver)
    page.opened_empty()
    element = session_browser.all('.will-appear').element_by(
        have.css_class('special')
    )

    page.load_body(
        '''
                   <ul>Hello to:
                       <li class="will-appear">Bob</li>
                       <li class="will-appear special">Kate</li>
                   </ul>'''
    )

    assert element().is_displayed() is True

    page.load_body(
        '''
                   <ul>Hello to:
                       <li class="will-appear">Bob</li>
                       <li class="will-appear special" style="display:none">Kate</li>
                   </ul>'''
    )
    assert element().is_displayed() is False
