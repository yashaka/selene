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


def test_have_url(session_browser):
    GivenPage(session_browser.driver).opened_empty()
    session_browser.should(have.url(session_browser.driver.current_url))
    session_browser.should(
        have.no.url(session_browser.driver.current_url[:-1])
    )


def test_have_url_containing(session_browser):
    GivenPage(session_browser.driver).opened_empty()
    session_browser.should(have.url_containing('empty.html'))
    session_browser.should(have.no.url_containing('start_page.xhtml'))


def test_fails_on_timeout_during_waiting_for_exact_url(session_browser):
    browser = session_browser.with_(timeout=0.1)

    GivenPage(browser.driver).opened_empty()

    with pytest.raises(TimeoutException) as error:
        browser.should(have.url('xttp:/'))
    assert "has url 'xttp:/'" in error.value.msg
    assert 'AssertionError: actual url:' in error.value.msg


def test_fails_on_timeout_during_waiting_for_part_of_url(session_browser):
    browser = session_browser.with_(timeout=0.1)

    GivenPage(browser.driver).opened_empty()

    with pytest.raises(TimeoutException) as error:
        browser.should(have.url_containing('xttp:/'))
    assert "has url containing 'xttp:/'" in error.value.msg
    assert 'AssertionError: actual url:' in error.value.msg
