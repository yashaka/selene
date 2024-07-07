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


# todo: should we use parametrized tests here to combine not enabled + disabled?


def test_should_be_enabled__passed_and_failed(session_browser):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <!--<button id="absent">Press me</button>-->
        <button id="hidden" style="display: none">Press me</button>
        <button id="hidden-disabled" disabled style="display: none">Press me</button>
        <button id="visible-enabled" style="display: block">Press me</button>
        <button id="visible-disabled" disabled style="display: block">Press me</button>
        '''
    )

    # THEN

    # enabled?
    # - visible & enabled passes
    s('#visible-enabled').should(be.enabled)
    s('#visible-enabled').should(be.enabled.not_.not_)
    # - visible & disabled fails with mismatch
    try:
        s('#visible-disabled').should(be.enabled)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible-disabled')).is enabled\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
            'Screenshot: '
        ) in str(error)
    # - hidden & enabled passes
    s('#hidden').should(be.enabled)
    # - hidden & disabled fails with mismatch
    try:
        s('#hidden-disabled').should(be.enabled)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden-disabled')).is enabled\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
            'Screenshot: '
        ) in str(error)
    # - absent fails with failure
    try:
        s('#absent').should(be.enabled)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            'Message: \n'
            '\n'
            'Timed out after 0.1s, while waiting for:\n'
            "browser.element(('css selector', '#absent')).is enabled\n"
            '\n'
            'Reason: NoSuchElementException: Message: no such element: Unable to locate '
            'element: {"method":"css selector","selector":"#absent"}\n'
            '  (Session info:'  # ' chrome=126.0.6478.62); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # ':\n'
            # 'condition not matched\n'
        ) in str(error)


def test_should_be_not_enabled__passed_and_failed(
    session_browser,
):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <!--<button id="absent">Press me</button>-->
        <button id="hidden" style="display: none">Press me</button>
        <button id="hidden-disabled" disabled style="display: none">Press me</button>
        <button id="visible-enabled" style="display: block">Press me</button>
        <button id="visible-disabled" disabled style="display: block">Press me</button>
        '''
    )

    # THEN

    # not enabled?
    # - visible & enabled fails with mismatch
    try:
        s('#visible-enabled').should(be.not_.enabled)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible-enabled')).is not (enabled)\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
            'Screenshot: '
        ) in str(error)
    # - visible & disabled passed
    s('#visible-disabled').should(match.enabled.not_)
    s('#visible-disabled').should(be.not_.enabled)
    # - hidden & enabled fails with mismatch
    try:
        s('#hidden').should(be.not_.enabled)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is not (enabled)\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
            'Screenshot: '
        ) in str(error)
    # - hidden & disabled passed
    s('#hidden-disabled').should(be.not_.enabled)
    # - absent fails with failure
    try:
        s('#absent').should(be.not_.enabled)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            'Message: \n'
            '\n'
            'Timed out after 0.1s, while waiting for:\n'
            "browser.element(('css selector', '#absent')).is not (enabled)\n"
            '\n'
            'Reason: NoSuchElementException: Message: no such element: Unable to locate '
            'element: {"method":"css selector","selector":"#absent"}\n'
            '  (Session info:'  # ' chrome=126.0.6478.62); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # ':\n'
            # 'condition not matched\n'
        ) in str(error)


def test_should_be_disabled__passed_and_failed(
    session_browser,
):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <!--<button id="absent">Press me</button>-->
        <button id="hidden" style="display: none">Press me</button>
        <button id="hidden-disabled" disabled style="display: none">Press me</button>
        <button id="visible-enabled" style="display: block">Press me</button>
        <button id="visible-disabled" disabled style="display: block">Press me</button>
        '''
    )

    # THEN

    # disabled?
    # - visible & enabled fails with mismatch
    try:
        s('#visible-enabled').should(be.disabled)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible-enabled')).is not (enabled)\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
            'Screenshot: '
        ) in str(error)
    # - visible & disabled passed
    s('#visible-disabled').should(match.disabled)
    s('#visible-disabled').should(be.disabled)
    # - hidden & enabled fails with mismatch
    try:
        s('#hidden').should(be.not_.enabled)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is not (enabled)\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
            'Screenshot: '
        ) in str(error)
    # - hidden & disabled passed
    s('#hidden-disabled').should(be.disabled)
    # - absent fails with failure
    try:
        s('#absent').should(be.disabled)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            'Message: \n'
            '\n'
            'Timed out after 0.1s, while waiting for:\n'
            "browser.element(('css selector', '#absent')).is not (enabled)\n"
            '\n'
            'Reason: NoSuchElementException: Message: no such element: Unable to locate '
            'element: {"method":"css selector","selector":"#absent"}\n'
            '  (Session info:'  # ' chrome=126.0.6478.62); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # ':\n'
            # 'condition not matched\n'
        ) in str(error)


def test_should_be_not_disabled__passed_and_failed(session_browser):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <!--<button id="absent">Press me</button>-->
        <button id="hidden" style="display: none">Press me</button>
        <button id="hidden-disabled" disabled style="display: none">Press me</button>
        <button id="visible-enabled" style="display: block">Press me</button>
        <button id="visible-disabled" disabled style="display: block">Press me</button>
        '''
    )

    # THEN

    # enabled?
    # - visible & enabled passes
    s('#visible-enabled').should(be.not_.disabled)
    s('#visible-enabled').should(be.not_.disabled.not_.not_)
    # - visible & disabled fails with mismatch
    try:
        s('#visible-disabled').should(be.not_.disabled)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible-disabled')).is enabled\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
            'Screenshot: '
        ) in str(error)
    # - hidden & enabled passes
    s('#hidden').should(be.not_.disabled)
    # - hidden & disabled fails with mismatch
    try:
        s('#hidden-disabled').should(be.not_.disabled)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden-disabled')).is enabled\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
            'Screenshot: '
        ) in str(error)
    # - absent fails with failure
    try:
        s('#absent').should(be.not_.disabled)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            'Message: \n'
            '\n'
            'Timed out after 0.1s, while waiting for:\n'
            "browser.element(('css selector', '#absent')).is enabled\n"
            '\n'
            'Reason: NoSuchElementException: Message: no such element: Unable to locate '
            'element: {"method":"css selector","selector":"#absent"}\n'
            '  (Session info:'  # ' chrome=126.0.6478.62); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # ':\n'
            # 'condition not matched\n'
        ) in str(error)


def test_should_be_clickable__passed_and_failed(session_browser):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <!--<button id="absent">Press me</button>-->
        <button id="hidden" style="display: none">Press me</button>
        <button id="hidden-disabled" disabled style="display: none">Press me</button>
        <button id="visible-enabled" style="display: block">Press me</button>
        <button id="visible-disabled" disabled style="display: block">Press me</button>
        '''
    )

    # THEN

    # clickable?
    # - visible & enabled passes
    s('#visible-enabled').should(match.clickable)
    s('#visible-enabled').should(be.clickable)
    s('#visible-enabled').should(be.clickable.not_.not_)
    # - visible & disabled fails with mismatch
    #   todo: consider to add more consistent with usage description in error, like
    #         is clickable: is visible and is enabled
    try:
        s('#visible-disabled').should(be.clickable)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible-disabled')).is visible and is "
            'enabled\n'
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
            'Screenshot: '
        ) in str(error)
    # - hidden & enabled fails with mismatch
    try:
        s('#hidden').should(be.clickable)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is visible and is enabled\n"
            '\n'
            'Reason: ConditionMismatch: actual html element: <button id="hidden" '
            'style="display: none">Press me</button>\n'
        ) in str(error)
    # - hidden & disabled fails with mismatch
    try:
        s('#hidden-disabled').should(be.clickable)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden-disabled')).is visible and is "
            'enabled\n'
            '\n'
            'Reason: ConditionMismatch: actual html element: <button id="hidden-disabled" '
            'disabled="" style="display: none">Press me</button>\n'
        ) in str(error)
    # - absent fails with failure
    try:
        s('#absent').should(be.clickable)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            'Message: \n'
            '\n'
            'Timed out after 0.1s, while waiting for:\n'
            "browser.element(('css selector', '#absent')).is visible and is enabled\n"
            '\n'
            'Reason: ConditionMismatch: Message: no such element: Unable to locate '
            'element: {"method":"css selector","selector":"#absent"}\n'
            '  (Session info:'  # ' chrome=126.0.6478.62); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # ':\n'
            # 'condition not matched\n'
        ) in str(error)
