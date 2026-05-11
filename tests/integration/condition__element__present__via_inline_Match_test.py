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
from selenium.common import NoSuchElementException

from selene import be, have
from selene.core import match
from selene.core.condition import Match, Condition
from selene.core.exceptions import ConditionMismatch
from tests.integration.helpers.givenpage import GivenPage


# TODO: review coverage: consider breaking down into atomic tests
def test_should_be_present__via_inline_Match__passed_and_failed(session_browser):
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
    # visible = browser.element("#visible")

    # THEN
    # - with actual failure as True on inversion
    absent.should(
        Match(
            'present',
            actual=lambda element: element.locate(),
            by=lambda actual: actual is not None,
            # todo: cover cases without _falsy_exceptions (here and below)
            _falsy_exceptions=(NoSuchElementException,),
        ).not_
    )
    # - with actual failure as True on inversion via Condition.as_not
    absent.should(
        Condition.as_not(
            Match(
                'present',
                actual=lambda element: element.locate(),
                by=lambda actual: actual is not None,
                _falsy_exceptions=(NoSuchElementException,),
            ),
            'absent',
        )
    )
    # - with actual failure as True on inversion via re-wrap into Condition
    # todo: add similar tests for other cases where we assert error message
    absent.should(
        Condition(
            'absent',
            Match(
                'present',
                actual=lambda element: element.locate(),
                by=lambda actual: actual is not None,
                _falsy_exceptions=(NoSuchElementException,),
            ).not_,
        )
    )
    # - with actual failure as True on inversion via re-wrap into Match
    # todo: add similar tests for other cases where we assert error message
    absent.should(
        Match(
            'absent',
            by=Match(
                'present',
                actual=lambda element: element.locate(),
                by=lambda actual: actual is not None,
                _falsy_exceptions=(NoSuchElementException,),
            ).not_,
        )
    )
    # - with actual failure
    try:
        absent.should(
            Match(
                'present',
                actual=lambda element: element.locate(),
                by=lambda actual: actual is not None,
                _falsy_exceptions=(NoSuchElementException,),
            )
        )
        pytest.fail('expected failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).present\n"
            '\n'
            'Reason: ConditionMismatch: Message: no such element: Unable to locate '
            'element: {"method":"css selector","selector":"#absent"}\n'
            '  (Session info:'  # ' chrome=125.0.6422.142); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
        ) in str(error)
    # - with actual failure on negated inversion via Condition.as_not
    #   (with lost reason details)
    try:
        absent.should(
            Condition.as_not(
                Match(
                    'present',
                    actual=lambda element: element.locate(),
                    by=lambda actual: actual is not None,
                ),
                'absent',
            ).not_
        )
        pytest.fail('expected failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).not (absent)\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
            '  (Session info: '  # 'chrome=126.0.6478.182); For documentation on this error, '
        ) in str(error)
    # ↪ compared to ↙
    # - with actual failure but wrapped into test on negated inversion via Condition.as_not
    #   (YET with SAME lost reason details) TODO: should we bother?
    try:
        absent.should(
            Condition.as_not(
                Condition(
                    'present',
                    ConditionMismatch._to_raise_if_not_actual(
                        query=lambda element: element.locate(),
                        by=lambda actual: actual is not None,
                    ),
                    _falsy_exceptions=(NoSuchElementException,),
                ),
                'absent',
            ).not_
        )
        pytest.fail('expected failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).not (absent)\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
        ) in str(error)
    # ↪ compared to ↙
    # - with by failure on negated inversion via Condition.as_not
    #   (YET with SAME lost reason details) TODO: should we bother?
    try:
        absent.should(
            Condition.as_not(
                Match(
                    'present',
                    by=lambda element: element.locate() is not None,
                ),
                'absent',
            ).not_
        )
        pytest.fail('expected failure')
    except AssertionError as error:
        assert (
            'Message: \n'
            '\n'
            'Timed out after 0.1s, while waiting for:\n'
            "browser.element(('css selector', '#absent')).not (absent)\n"
            '\n'
            'Reason: NoSuchElementException: Message: no such element: Unable to locate '
            'element: {"method":"css selector","selector":"#absent"}\n'
            '  (Session info: '  # 'chrome=126.0.6478.182); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # ':\n'
            # 'condition not matched; For documentation on this error, please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
        ) in str(error)
    # - with actual mismatch on inversion (without 'is' prefix in name)
    try:
        hidden.should(
            Match(
                'present',
                actual=lambda element: element.locate(),
                by=lambda actual: actual is not None,
            ).not_
        )
        pytest.fail('expected mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).not (present)\n"
            '\n'
            'Reason: ConditionMismatch: actual: '
            '<selenium.webdriver.remote.webelement.WebElement '
            '(session='  # '"b34b8642ff3b4a05cab2d1e6e7d7f2c7", '
            # 'element=f.8519179ED653D79AE97335F0BE9F6CC7.d.FB35FED598AED63006F71DA20E973E7F.e.3")>\n'
        ) in str(error)
    # - with actual mismatch on inversion (without 'is' prefix in name)
    try:
        hidden.should(
            Match(
                'is present',
                actual=lambda element: element.locate(),
                by=lambda actual: actual is not None,
            ).not_
        )
        pytest.fail('expected mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is not (present)\n"
            '\n'
            'Reason: ConditionMismatch: actual: '
            '<selenium.webdriver.remote.webelement.WebElement '
            '(session='  # '"b34b8642ff3b4a05cab2d1e6e7d7f2c7", '
            # 'element=f.8519179ED653D79AE97335F0BE9F6CC7.d.FB35FED598AED63006F71DA20E973E7F.e.3")>\n'
        ) in str(error)
    # - with by failure as True on inversion
    absent.should(
        Match(
            'present',
            by=lambda element: element.locate() is not None,
            _falsy_exceptions=(NoSuchElementException,),
        ).not_
    )
    # - with by failure
    try:
        absent.should(
            Match(
                'present',
                by=lambda element: element.locate() is not None,
                _falsy_exceptions=(NoSuchElementException,),
            )
        )
        pytest.fail('expected failure')
    except AssertionError as error:
        assert (
            # TODO: one problem with this error... that it tells about Mismatch
            #       but in fact its a Failure
            #       (i.e. and actual exception not comparison mismatch)
            "browser.element(('css selector', '#absent')).present\n"
            '\n'
            'Reason: ConditionMismatch: Message: no such element: Unable to locate '
            'element: {"method":"css selector","selector":"#absent"}\n'
            '  (Session info:'  # ' chrome=125.0.6422.142); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # ':\n'
            # 'condition not matched\n'  # TODO: this ending is not needed...
            #                                  but should we bother?
        ) in str(error)
    # - with by mismatch on inversion (without 'is' prefix in name)
    try:
        hidden.should(
            Match('present', by=lambda element: element.locate() is not None).not_
        )
        pytest.fail('expected mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).not (present)\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
        ) in str(error)
    # - with by mismatch on inversion (with 'is' prefix in name)
    try:
        hidden.should(
            Match('is present', by=lambda element: element.locate() is not None).not_
        )
        pytest.fail('expected mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is not (present)\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
        ) in str(error)
