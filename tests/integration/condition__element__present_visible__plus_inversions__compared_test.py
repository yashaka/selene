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
from selene.core import match
from tests.integration.helpers.givenpage import GivenPage


# TODO: consider refactoring to parametrized test such type of tests


def test_should_be_hidden__passed_and_failed__compared_to_be_visible(session_browser):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <!--<button id="absent">Press me</button>-->
        <button id="hidden" style="display: none">Press me</button>
        <button id="visible" style="display: block">Press me</button>
        '''
    )

    absent = browser.element("#absent")
    hidden = browser.element("#hidden")
    visible = browser.element("#visible")

    # THEN

    absent.should(match.present_in_dom.not_)
    absent.should(match.present_in_dom.not_.not_.not_)
    absent.should(be.not_.present_in_dom)

    absent.should(match.absent_in_dom)
    absent.should(match.absent_in_dom.not_.not_)
    absent.should(be.absent_in_dom)
    hidden.should(match.present_in_dom)
    hidden.should(be.present_in_dom)
    hidden.should(be.hidden_in_dom)  # same ↙️
    hidden.should(be.present_in_dom.and_(be.not_.visible))
    hidden.should(be.not_.visible)
    hidden.should(be.not_.absent_in_dom)  # TODO: rename to be.not_.absent_in_dom?

    absent.should(match.visible.not_)
    absent.should(be.not_.visible)
    absent.should(be.hidden)  # TODO: should it fail?
    absent.should(be.not_.hidden_in_dom)
    absent.should(match.hidden_in_dom.not_)

    visible.should(match.visible)
    visible.should(be.visible)
    visible.should(be.not_.hidden)
    visible.should(be.not_.hidden_in_dom)
    visible.should(be.present_in_dom)
    visible.should(be.not_.absent_in_dom)

    # TODO: review and extend/finalize coverage below

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
            'Reason: ConditionMismatch: actual: '
            '<selenium.webdriver.remote.webelement.WebElement '  # TODO: improve message to be more descriptive
            '(session='  # '"97b05cc66201233552e08f811a803a52", '
            # 'element="f.C6C48B539DD5CC96F853F6845EBBF304.d.8D394C190A7F06E3E7290DB3EC3B5816.e.3")>\n'
        ) in str(error)

    hidden.should(be.not_.visible)
    try:
        hidden.should(be.not_.visible.not_)
        pytest.fail("on mismatch")
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is visible\n"
            '\n'
            'Reason: ConditionMismatch: actual: '
            '<selenium.webdriver.remote.webelement.WebElement '  # TODO: improve message to be more descriptive
            '(session='  # '"57800fadbf59376eabca878008e29802", '
            # 'element="f.608E5EE7EEFFB3C64BC358E54EEE615C.d.0BAD00B7AAB6B016AD90BB0421824CA4.e.2")>\n'
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


def x_test_deprecated_should_be_absent__passed_and_failed__compared_(session_browser):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <!--<button id="absent">Press me</button>-->
        <button id="hidden" style="display: none">Press me</button>
        <button id="visible" style="display: block">Press me</button>
        '''
    )

    absent = browser.element("#absent")
    hidden = browser.element("#hidden")
    visible = browser.element("#visible")

    # THEN

    absent.should(match.present.not_)
    absent.should(match.present.not_.not_.not_)
    absent.should(be.not_.present)

    absent.should(match.absent)
    absent.should(match.absent.not_.not_)
    absent.should(be.absent)
    hidden.should(match.present)
    hidden.should(be.present)
    hidden.should(be.hidden_in_dom)  # same ↙️
    hidden.should(be.present.and_(be.not_.visible))
    hidden.should(be.not_.visible)
    hidden.should(be.not_.absent)  # TODO: rename to be.not_.absent_in_dom?

    absent.should(match.visible.not_)
    absent.should(be.not_.visible)
    absent.should(be.hidden)  # TODO: should it fail?
    absent.should(be.not_.hidden_in_dom)
    absent.should(match.hidden_in_dom.not_)

    visible.should(match.visible)
    visible.should(be.visible)
    visible.should(be.not_.hidden)
    visible.should(be.not_.hidden_in_dom)
    visible.should(be.present)
    visible.should(be.not_.absent)


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
