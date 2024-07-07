# MIT License
#
# Copyright (c) 2024 Iakiv Kramarenko
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

from selene import have
from selene.core import match
from tests.integration.helpers.givenpage import GivenPage


# todo: consider breaking it down into separate tests


def test_have_attribute__condition_variations(session_browser):
    browser = session_browser.with_(timeout=0.1)
    ss = lambda selector: browser.all(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>Hey:
           <li><label>First Name:</label> <input type="text" class="name" id="firstname" value="John 20th"></li>
           <li><label>Last Name:</label> <input type="text" class="name" id="lastname" value="Doe 2nd"></li>
        </ul>
        <ul>Your training today:
           <li><label>Pull up:</label><input type="text" class='exercise' id="pullup" value="20"></li>
           <li><label>Push up:</label><input type="text" class='exercise' id="pushup" value="30"></li>
        </ul>
        '''
    )

    names = browser.all('.name')
    exercises = browser.all('.exercise')

    # the following passes too, cause js prop exists, are we ok with that?
    browser.element('ul').should(have.attribute('id'))

    names.should(have.attribute('id').values('firstname', 'lastname'))
    names.should(have.attribute('id').values_containing('first', 'last'))

    exercises.should(have.attribute('value').values(20, 30))
    try:
        exercises.should(have.attribute('value').values(2, 3))
        pytest.fail('should fail on values mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', '.exercise')).has attribute 'value' with values "
            "[2, 3]\n"
            '\n'
            "Reason: ConditionMismatch: actual value attributes: ['20', '30']\n"
            'Screenshot: '
        ) in str(error)
    exercises.should(match.attribute('value').values(2, 3).not_)
    exercises.should(match.values(2, 3).not_)
    exercises.should(have.attribute('value').values(2, 3).not_)
    exercises.should(have.values(2, 3).not_)
    exercises.should(have.no.attribute('value').values(2, 3))
    exercises.should(have.no.values(2, 3))
    names.should(have.attribute('value').values_containing(20, 2))
    try:
        exercises.should(have.attribute('value').values_containing(200, 300))
        pytest.fail('should fail on values mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', '.exercise')).has attribute 'value' with values "
            "containing [200, 300]\n"
            '\n'
            "Reason: ConditionMismatch: actual value attributes: ['20', '30']\n"
            'Screenshot: '
        ) in str(error)
    names.should(have.attribute('id').values_containing(20, 2).not_)
    names.should(have.no.attribute('id').values_containing(20, 2))
    try:
        names.should(have.no.attribute('value').values_containing(20, 2))
        pytest.fail('should fail on values mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', '.name')).has no (attribute 'value' with values "
            "containing [20, 2])\n"
            '\n'
            "Reason: ConditionMismatch: actual value attributes: ['John 20th', 'Doe "
            "2nd']\n"
        ) in str(error)

    names.should(match.attribute('id').value('name').each.not_)
    names.should(have.attribute('id').value('name').each.not_)
    names.should(have.no.attribute('id').value('name').each)
    exercises.first.should(have.attribute('value').value(20))
    exercises.first.should(have.attribute('value').value_containing(2))
    names.should(have.attribute('id').value_containing('name').each)
    try:
        names.should(have.attribute('id').value_containing('first').each)
        pytest.fail('should fail on values mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', '.name')). each has attribute 'id' with value "
            "containing 'first'\n"
            '\n'
            'Reason: AssertionError: Not matched elements among all with indexes from 0 '
            'to 1:\n'
            "browser.all(('css selector', '.name')).cached[1]: actual attribute id: "
            'lastname\n'
            'Screenshot: '
        ) in str(error)
    # assuming two inputs for names: #firstname and #lastname
    # not each name contain 'first' (one contain 'last' instead of 'first')
    names.should(have.attribute('id').value_containing('first').each.not_)
    # but each can not contain 'first'! ;)
    try:
        names.should(have.no.attribute('id').value_containing('first').each)
        pytest.fail('should fail on values mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', '.name')). each has no (attribute 'id' with "
            "value containing 'first')\n"
            '\n'
            'Reason: AssertionError: Not matched elements among all with indexes from 0 '
            'to 1:\n'
            "browser.all(('css selector', '.name')).cached[0]: actual attribute id: "
            'firstname\n'
            'Screenshot: '
        ) in str(error)

    # with .or_
    ss('.name').should(
        have.attribute('id')
        .value_containing('first')
        .or_(have.attribute('id').value_containing('last'))
        .each
    )
    try:
        ss('.name').should(
            have.attribute('id')
            .value_containing('first')
            .or_(have.attribute('id').value_containing('last'))
            .each.not_
        )
        pytest.fail('should fail on values mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', '.name')).not ( each has attribute 'id' with "
            "value containing 'first' or has attribute 'id' with value containing "
            "'last')\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'  # todo: improve details
        ) in str(error)
    ss('.exercise').should(
        have.no.attribute('id')
        .value_containing('push')
        .or_(have.no.attribute('id').value_containing('pull'))
        .each
    )
    try:
        ss('.exercise').should(
            have.no.attribute('id')
            .value_containing('pu')
            .or_(have.no.attribute('id').value_containing('up'))
            .each
        )
        pytest.fail('should fail on values mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', '.exercise')). each has no (attribute 'id' with "
            "value containing 'pu') or has no (attribute 'id' with value containing "
            "'up')\n"
            '\n'
            'Reason: AssertionError: Not matched elements among all with indexes from 0 '
            'to 1:\n'
            "browser.all(('css selector', '.exercise')).cached[0]: actual attribute id: "
            'pullup; actual attribute id: pullup\n'  # todo: why is it doubled? – fix if needed
            "browser.all(('css selector', '.exercise')).cached[1]: actual attribute id: "
            'pushup; actual attribute id: pushup\n'
        ) in str(error)
    try:
        ss('.name,.exercise').should(
            have.attribute('id')
            .value_containing('first')
            .or_(have.attribute('id').value_containing('last'))
            .each
        )
        pytest.fail('should fail on values mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', '.name,.exercise')). each has attribute 'id' "
            "with value containing 'first' or has attribute 'id' with value containing "
            "'last'\n"
            '\n'
            'Reason: AssertionError: Not matched elements among all with indexes from 0 '
            'to 3:\n'
            "browser.all(('css selector', '.name,.exercise')).cached[2]: actual attribute "
            'id: pullup; actual attribute id: pullup\n'
            "browser.all(('css selector', '.name,.exercise')).cached[3]: actual attribute "
            'id: pushup; actual attribute id: pushup\n'
        ) in str(error)

    # todo: add .and_ tests similar to .or_ ones

    # aliases
    exercises.first.should(have.value(20))
    exercises.first.should(have.value_containing(2))
    exercises.should(have.values(20, 30))
    exercises.should(have.values_containing(2, 3))
