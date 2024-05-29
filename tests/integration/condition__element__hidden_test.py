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

from selene import be, have
from tests.integration.helpers.givenpage import GivenPage


def test_should_be_hidden__passed_and_failed__compared_to_be_visible(session_browser):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <button id="hidden" style="display: none">Press me</button>
        <button id="visible" style="display: block">Press me</button>
        '''
    )

    hidden = browser.element("#hidden")
    visible = browser.element("#visible")

    # THEN
    visible.should(be.not_.hidden)
    try:
        visible.should(be.hidden)
        pytest.fail("on mismatch")
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).is hidden\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
        ) in str(error)
    visible.should(be.not_.hidden)  # same as prev, but just to compare...
    try:
        hidden.should(be.not_.hidden)
        pytest.fail("on mismatch")
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is not (hidden)\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
        ) in str(error)
    visible.should(be.not_.visible.not_)
    hidden.should(be.not_.hidden.not_)

    hidden.should(be.in_dom).should(be.not_.visible).should(be.hidden)
    try:
        hidden.should(be.visible)
        pytest.fail("on mismatch")
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is visible\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
        ) in str(error)

    hidden.should(be.not_.visible)
    try:
        hidden.should(be.not_.visible.not_)
        pytest.fail("on mismatch")
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is visible\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
        ) in str(error)

    hidden.should(be.not_.hidden.not_)
    try:
        hidden.should(be.not_.hidden)
        pytest.fail("on mismatch")
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is not (hidden)\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
        ) in str(error)


def test_action_on_element_found_relatively_from_hidden_element(session_browser):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <button id="hidden" style="display: none">Press me</button>
        <div>
            <a href="#first">go to Heading 1</a>
            <a href="#second">go to Heading 2</a>
        </div>
        <h1 id="first">Heading 1</h2>
        <h2 id="second">Heading 2</h2>
        '''
    )
    hidden_element = browser.element("#hidden")

    hidden_element.element('./following-sibling::*/a[2]').click()

    assert 'second' in browser.driver.current_url
