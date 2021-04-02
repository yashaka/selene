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


def test_search_does_not_start_on_creation_for_both_parent_and_inner(
    session_browser,
):
    GivenPage(session_browser.driver).opened_empty()

    non_existent_element = session_browser.element(
        '#not-existing-element'
    ).element('.not-existing-inner')

    assert str(non_existent_element)


def test_search_is_postponed_until_actual_action_like_questioning_displayed(
    session_browser,
):
    element = session_browser.element('#will-be-existing-element').element(
        '.will-exist-inner'
    )
    page = GivenPage(session_browser.driver)
    page.opened_empty()

    page.load_body(
        '''
        <h1 id="will-be-existing-element">
            <span class="will-exist-inner">Hello</span> kitty:*
        </h1>'''
    )
    answer = element().is_displayed()

    assert answer is True


def test_search_is_updated_on_next_actual_action_like_questioning_displayed(
    session_browser,
):
    element = session_browser.element('#will-be-existing-element').element(
        '.will-exist-inner'
    )
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        '''
        <h1 id="will-be-existing-element">
            <span class="will-exist-inner">Hello</span> kitty:*
        </h1>
        '''
    )
    assert element().is_displayed() is True

    page.load_body(
        '''
        <h1 id="will-be-existing-element">
            <span class="will-exist-inner" style="display:none">
              Hello
            </span> kitty:*
        </h1>'''
    )
    new_answer = element().is_displayed()

    assert new_answer is False


def test_search_finds_exactly_inside_parent(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        '''
        <a href="#first">go to Heading 2</a>
        <p>
            <a href="#second">go to Heading 2</a>
            <h1 id="first">Heading 1</h1>
            <h2 id="second">Heading 2</h2>
        /p>'''
    )

    session_browser.element('p').element('a').click()

    assert "second" in session_browser.driver.current_url
