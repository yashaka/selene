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


# TODO: consider breaking it down into separate tests,
#       and remove duplicates with other test suites


def test_have_text__condition_variations(session_browser):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>Hey:
           <li><label>First Name:</label> <span class="name" id="firstname">John 20th</span></li>
           <li><label>Last Name:</label> <span class="name" id="lastname">Doe 2nd</span></li>
        </ul>
        <ul>Your training today:
           <li><label>Pull up:</label><span class='exercise' id="pullup">20</span></li>
           <li><label>Push up:</label><span class='exercise' id="pushup">30</span></li>
        </ul>
        '''
    )

    names = browser.all('.name')
    exercises = browser.all('.exercise')

    exercises.should(have.exact_texts(20, 30))
    exercises.should(have.exact_texts('20', '30'))
    exercises.should(have.texts(2, 3))
    exercises.should(have.texts('2', '3'))
    exercises.should(have.text('0').each)
    exercises.should(have.text(0).each)
    exercises.second.should(have.no.exact_text(20))
    exercises.should(have.exact_text(20).each.not_)
    # exercises.should(have.no.exact_text(20).each)  # TODO: fix it

    try:
        names.should(have.texts(20, 2).not_)
        pytest.fail('should fail on texts mismatch')
    except AssertionError as error:
        assert (
            'Timed out after 0.1s, while waiting for:\n'
            "browser.all(('css selector', '.name')).has no (texts (20, 2))\n"
            '\n'
            'Reason: ConditionNotMatchedError: condition not matched\n'
        ) in str(error)
