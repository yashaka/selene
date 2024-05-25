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
from tests.integration.helpers.givenpage import GivenPage


# TODO: consider breaking it down into separate tests


def test_have_property__condition_variations(session_browser):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>Hey:
           <li><label>First Name:</label> <input type="text" class="name" id="firstname" value=""></li>
           <li><label>Last Name:</label> <input type="text" class="name" id="lastname" value=""></li>
        </ul>
        <ul>Your training today:
           <li><label>Pull up:</label><input type="text" class='exercise' id="pullup" value=""></li>
           <li><label>Push up:</label><input type="text" class='exercise' id="pushup" value=""></li>
        </ul>
        '''
    )

    names = browser.all('.name')
    exercises = browser.all('.exercise')

    names.first.type('John 20th')
    names.second.type('Doe 2nd')
    exercises.first.type('20')
    exercises.second.type('30')

    # the following passes too, cause js prop exists, are we ok with that?
    browser.element('ul').should(have.attribute('id'))

    exercises.should(have.js_property('value').values(20, 30))
    names.should(have.js_property('value').values_containing(20, 2))
    try:
        names.should(have.js_property('value').values_containing(20, 2).not_)
        pytest.fail('should fail on values mismatch')
    except AssertionError as error:
        assert (
            'Timed out after 0.1s, while waiting for:\n'
            "browser.all(('css selector', '.name')).has no (js property 'value' with values "
            "containing '(20, 2)')\n"
            '\n'
            'Reason: ConditionNotMatchedError: condition not matched\n'
        ) in str(error)

    exercises.first.should(have.js_property('value').value(20))
    exercises.first.should(have.js_property('value').value_containing(2))
