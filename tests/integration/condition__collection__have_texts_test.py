# -*- coding: utf-8 -*-

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

import pytest
from selene import have
from selene.core.exceptions import TimeoutException
from tests.integration.helpers.givenpage import GivenPage


def test_should_have_texts(session_browser):
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Alex!</li>
           <li>Yakov!</li>
        </ul>
        '''
    )

    session_browser.all('li').should(
        have.texts('', '')
    )  # funny:) but as it is
    session_browser.all('li').should(have.texts('Alex', 'Yakov'))
    session_browser.all('li').should(have.texts('Alex!', 'Yakov!'))


def test_should_have_texts_exception(session_browser):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Alex</li>
           <li>Yakov</li>
        </ul>
        '''
    )

    with pytest.raises(TimeoutException) as error:
        browser.all('li').should(have.texts('Alex'))
    assert "has texts ('Alex',)" in error.value.msg
    assert (
        "AssertionError: actual visible_texts: ['Alex', 'Yakov']"
        in error.value.msg
    )


def test_should_have_no_texts(session_browser):
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Alex!</li>
           <li>Yakov!</li>
        </ul>
        '''
    )

    session_browser.all('li').should(have.no.texts(' ', ' '))
    session_browser.all('li').should(have.no.texts('', 'Yakov!!'))
    session_browser.all('li').should(have.no.texts('Alex!', 'Yakov!!'))
    session_browser.all('li').should(have.no.texts('Alex!', 'Yakov!', ''))
    session_browser.all('li').should(have.no.texts('Alex!'))


def test_should_have_no_texts_exception(session_browser):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Alex</li>
           <li>Yakov</li>
        </ul>
        '''
    )

    with pytest.raises(TimeoutException) as error:
        browser.all('li').should(have.no.texts('Alex', 'Yakov'))
    # todo: why do we have `has` below, should not it be `have`?
    assert "has no texts ('Alex', 'Yakov')" in error.value.msg
    assert "ConditionNotMatchedError: condition not matched" in error.value.msg
    # todo: should not we see here actual texts in log too?


def test_should_have_text(session_browser):
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Yakov</li>
           <li>Jakob</li>
        </ul>
        '''
    )

    session_browser.all('li').should(have.text('ako'))
    session_browser.all('li').should(have.text(''))
    # todo: this test is a bit weird here...
    # the file is called condition__collection__have_texts_test.py
    # specifying that here we tests collection conditions...
    # but have.text is not a collection condition
    # it is an element condition applied to collection
    # i am not sure that this file is a correct place for such test
    # but we are going to change how a collection can apply an element condition
    # to assert its content
    # we either go `collection.should_each(have.text(''))` way
    # or `collection.should(have.text('').each)` way
    # in the former case probably
    #   we will move this test to condition__element__have_texts_test.py
    # in the latter case probably we keep it here
    # for now let's keep it here, and then we see...


def test_should_have_text_exception(session_browser):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Alex</li>
           <li>Alex</li>
        </ul>
        '''
    )

    with pytest.raises(TimeoutException) as error:
        browser.all('li').should(have.text('Yakov'))
    assert "has text Yakov" in error.value.msg
    assert "AssertionError: actual text: Alex" in error.value.msg


def test_should_have_no_text(session_browser):
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Yakov</li>
           <li>Yakov</li>
        </ul>
        '''
    )

    session_browser.all('li').should(have.no.text('L'))


def test_should_have_no_text_exception(session_browser):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Alex</li>
           <li>Alex</li>
        </ul>
        '''
    )

    with pytest.raises(TimeoutException) as error:
        browser.all('li').should(have.no.text('Alex'))
    assert "has no text Alex" in error.value.msg
    assert "ConditionNotMatchedError: condition not matched" in error.value.msg
