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

from selene import be
from selene.core import match
from selene.core.condition import Match
from tests.integration.helpers.givenpage import GivenPage


# todo: consider refactoring to parametrized test such type of tests
# todo: make the style consistent


# TODO: break down into more atomic tests (probably not fully atomic)
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

    # present in dom?
    # - hidden passes
    hidden.should(match.present_in_dom)
    hidden.should(be.present_in_dom)
    # - visible passes
    visible.should(be.present_in_dom)
    # - absent fails
    try:
        absent.should(be.present_in_dom)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).is present in DOM\n"
            '\n'
            'Reason: ConditionMismatch: Message: no such element: Unable to locate '
            'element: {"method":"css selector","selector":"#absent"}\n'
            '  (Session info:'  # ' chrome=126.0.6478.62); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # '\n'
        ) in str(error)

    # not present in dom?
    # - absent passes
    absent.should(match.present_in_dom.not_)
    absent.should(match.present_in_dom.not_.not_.not_)
    absent.should(be.not_.present_in_dom)
    # - hidden fails
    try:
        hidden.should(be.not_.present_in_dom)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is not (present in DOM)\n"
            '\n'
            'Reason: ConditionMismatch: actual: '
            '<selenium.webdriver.remote.webelement.WebElement '
            '(session='  # '"ac89fc2bc06d3524caaba592c7075eff", '
            # 'element="f.1252E8A34F76BC81CF07D439B7DBFF6E.d.ABCFA422CE62624352BE6330D21B8F4B.e.2")>\n'
        ) in str(error)
    # - visible fails
    try:
        visible.should(be.not_.present_in_dom)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).is not (present in DOM)\n"
            '\n'
            'Reason: ConditionMismatch: actual: '
            '<selenium.webdriver.remote.webelement.WebElement '
            '(session='  # '"ac89fc2bc06d3524caaba592c7075eff", '
            # 'element="f.1252E8A34F76BC81CF07D439B7DBFF6E.d.ABCFA422CE62624352BE6330D21B8F4B.e.2")>\n'
        ) in str(error)

    # absent in dom?
    # - absent passes
    absent.should(match.absent_in_dom)
    absent.should(match.absent_in_dom.not_.not_)
    absent.should(be.absent_in_dom)
    # - hidden fails
    try:
        hidden.should(be.absent_in_dom)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is absent in DOM\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
            # todo: DESIRED: to see actual webelement, maybe even its html
        ) in str(error)
    # - visible fails
    try:
        visible.should(be.absent_in_dom)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).is absent in DOM\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
            # todo: DESIRED: to see actual webelement, maybe even its html
        ) in str(error)

    # not absent in dom?
    # - hidden passes
    hidden.should(be.not_.absent_in_dom)
    # - visible passes
    visible.should(be.not_.absent_in_dom)
    # - absent fails  # todo: CONSIDER: logging webelement info
    try:
        absent.should(be.not_.absent_in_dom)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).is not (absent in DOM)\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
        ) in str(error)

    # hidden in dom?
    # - hidden passes
    hidden.should(be.hidden_in_dom)  # same ↙️
    hidden.should(be.present_in_dom.and_(be.not_.visible))
    # - absent fails
    try:
        absent.should(be.hidden_in_dom)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).is present in DOM and is not "
            '(visible)\n'
            '\n'
            'Reason: ConditionMismatch: Message: no such element: Unable to locate '
            'element: {"method":"css selector","selector":"#absent"}\n'
            '  (Session info: '  # 'chrome=126.0.6478.62); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
        ) in str(error)
    # - visible fails # TODO: improve message to be more descriptive
    try:
        visible.should(be.hidden_in_dom)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).is present in DOM and is not "
            '(visible)\n'
            '\n'
            'Reason: ConditionMismatch: condition not matched'
        ) in str(error)

    # not hidden in dom?
    # - absent passes
    absent.should(be.not_.hidden_in_dom)
    absent.should(match.hidden_in_dom.not_)
    # - visible passes
    visible.should(be.not_.hidden_in_dom)
    # - hidden fails  # todo: CONSIDER: adding "hidden in DOM: " prefix before (... and ...)
    #                 # todo: DESIRED: log more info about webelement, like its html
    try:
        hidden.should(be.not_.hidden_in_dom)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is not (present in DOM and is "
            'not (visible))\n'
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
        ) in str(error)


def test_visible__passed_and_failed__compared_to_inline_Match(
    session_browser,
):
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

    # visible?
    # - visible passes
    visible.should(match.visible)
    visible.should(be.visible)
    # - hidden fails
    # -- when defined inline via Match with actual
    try:
        hidden.should(
            Match(
                'is visible',
                actual=lambda element: element.locate(),
                by=lambda actual: actual.is_displayed(),
            )
        )
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is visible\n"
            '\n'
            'Reason: ConditionMismatch: actual: '
            '<selenium.webdriver.remote.webelement.WebElement '
            '(session='  # '"dc1570b7584dcc0deeb942678e3b5e84", '
            # 'element="f.9CB983FB72464DAD5E0EB030047C49FF.d.AD05D6B5AD406A101AF7788EC21322D8.e.2")>\n'
        ) in str(error)
    # -- when defined inline via Match with actual as (webelement, html)
    try:
        hidden.should(
            Match(
                'is visible',
                actual=lambda element: (
                    webelement := element.locate(),
                    webelement.get_attribute('outerHTML'),
                ),
                by=lambda actual: actual[0].is_displayed(),
            )
        )
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is visible\n"
            '\n'
            'Reason: ConditionMismatch: actual: '
            '(<selenium.webdriver.remote.webelement.WebElement '
            '(session='  # '"fabd9a48b4b154b55eb562e0e61a25a5", '
            # 'element="f.0C5C82B6D3AD2AE4A6E796CFCCA98D65.d.040890CF8CA8AB4E2F702249A3EA92FF.e.3")>, '
        ) in str(error)
        assert (
            '\'<button id="hidden" style="display: none">Press me</button>\')\n'
        ) in str(error)
    # -- when defined inline via Match with actual and describe_actual
    #    TODO: Do we need it? (not implemented yet)
    '''
    try:
        hidden.should(
            Match(
                'is visible',
                actual=lambda element: element.locate(),
                by=lambda actual: actual.is_displayed(),
                describe_actual=lambda actual: (
                    actual and actual.get_attribute('outerHTML')
                ),
            )
        )
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is visible\n"
            '\n'
            'Reason: ConditionMismatch: actual: '
            '\'<button id="hidden" style="display: none">Press me</button>\')\n'
        ) in str(error)
    '''
    # -- when defined inline via Match without actual
    try:
        hidden.should(
            Match('is visible', by=lambda element: element.locate().is_displayed())
        )
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is visible\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
        ) in str(error)
    # -- when reused from be.*  # todo: CONSIDER: logging webelement info as actual
    try:
        hidden.should(be.visible)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is visible\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
        ) in str(error)
    # - absent fails
    try:
        absent.should(be.visible)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).is visible\n"
            '\n'
            'Reason: ConditionMismatch: Message: no such element: Unable to locate '
            'element: {"method":"css selector","selector":"#absent"}\n'
            '  (Session info:'  # ' chrome=126.0.6478.62); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # ':\n'
            # 'condition not matched\n'
        ) in str(error)


def test_not_visible__passed_and_failed(
    session_browser,
):
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

    # not visible?
    # - hidden passes
    hidden.should(match.visible.not_)
    hidden.should(be.not_.visible)
    hidden.should(be.not_.visible.not_.not_)
    # - absent passes
    absent.should(be.not_.visible)
    absent.should(be.not_.visible.not_.not_)
    # - visible fails # todo: CONSIDER: logging webelement info, like outerHTML
    try:
        visible.should(be.not_.visible)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).is not (visible)\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
        ) in str(error)


def test_hidden__passed_and_failed(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    s = lambda selector: browser.element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <!--<button id="absent">Press me</button>-->
        <button id="hidden" style="display: none">Press me</button>
        <button id="visible" style="display: block">Press me</button>
        '''
    )

    # hidden?

    # - absent passes
    s('#absent').should(be.hidden)
    s('#absent').should(be.hidden.not_.not_)

    # - hidden passes
    s('#hidden').should(be.hidden)

    # - visible fails  # todo: CONSIDER: logging webelement info, like outerHTML
    try:
        s('#visible').should(be.hidden)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).is hidden\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
        ) in str(error)


ABSENT_HIDDEN_VISIBLE_BUTTONS = '''
<!--<button id="absent">Press me</button>-->
<button id="hidden" style="display: none">Press me</button>
<button id="visible" style="display: block">Press me</button>
'''


def test_not_hidden__passed_and_failed(
    session_browser,
):
    GivenPage(session_browser.driver).opened_with_body(ABSENT_HIDDEN_VISIBLE_BUTTONS)
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)

    # not hidden?

    # - visible passes
    s('#visible[style="display: block"]').should(be.not_.hidden)
    s('#visible[style="display: block"]').should(be.not_.hidden.not_.not_)

    # - hidden fails  # todo: CONSIDER: logging webelement info, like outerHTML
    try:
        s('#hidden[style="display: none"]').should(be.not_.hidden)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden[style=\"display: none\"]')).is "
            'not (hidden)\n'
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
        ) in str(error)

    # - absent fails  # todo: CONSIDER: reimplement condition to be not "as_not" based
    #                 #       so the error message will contain reason as failure
    try:
        s('#absent').should(be.not_.hidden)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).is not (hidden)\n"
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
