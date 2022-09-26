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
from selene import have
from selene.core.condition import Condition
from selene.core.exceptions import TimeoutException
from tests.integration.helpers.givenpage import GivenPage


def test_on_collection(session_browser):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Welcome to:
           <li>Harry from Hogwarts</li>
           <li>Ron from Hogwarts</li>
           <li>Hermione from Hogwarts</li>
        </ul>
        '''
    )

    elements = browser.all('li')

    elements.should(Condition.for_each(have.text('from Hogwarts')))
    elements.should(have.text('from Hogwarts').each)
    try:
        elements.should(have.text('Ron').each)
    except TimeoutException as error:
        assert (
            "browser.all(('css selector', 'li')). each has text Ron\n"
            "\n"
            "Reason: AssertionError: Not matched elements among all with indexes from 0 to 2:\n"
            "browser.all(('css selector', 'li')).cached[0]: actual text: Harry from Hogwarts\n"
            "browser.all(('css selector', 'li')).cached[2]: actual text: Hermione from Hogwarts"
        ) in str(error)
    elements.should(have.text('Ron').each.not_)
    try:
        elements.should(have.text('Ron').not_.each)
    except TimeoutException as error:
        assert (
            "browser.all(('css selector', 'li')). each has no (text Ron)\n"
            "\n"
            "Reason: AssertionError: Not matched elements among all with indexes from 0 to 2:\n"
            "browser.all(('css selector', 'li')).cached[1]: condition not matched"
        ) in str(error)
    try:
        elements.should(have.no.text('Ron').each)
    except TimeoutException as error:
        assert (
            "browser.all(('css selector', 'li')). each has no (text Ron)\n"
            "\n"
            "Reason: AssertionError: Not matched elements among all with indexes from 0 to 2:\n"
            "browser.all(('css selector', 'li')).cached[1]: condition not matched"
        ) in str(error)
