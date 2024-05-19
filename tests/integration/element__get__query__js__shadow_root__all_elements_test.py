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
import logging

import pytest

from selene import command, have, query, support


def test_actions_on_shadow_roots_of_all_elements(session_browser):
    # GIVEN
    browser = session_browser.with_(timeout=0.5)
    paragraphs = browser.all('my-paragraph')

    # WHEN even before opened browser
    paragraph_shadow_roots = paragraphs.get(query.js.shadow_roots)
    my_shadowed_texts = paragraph_shadow_roots.all('[name=my-text]')
    # AND
    browser.open('https://the-internet.herokuapp.com/shadowdom')

    # THEN
    my_shadowed_texts.should(have.exact_texts('My default text', 'My default text'))
    paragraphs.should(
        have.exact_texts(
            "Let's have some different text!",
            "Let's have some different text!\nIn a list!",
        )
    )

    # WHEN failed
    try:
        my_shadowed_texts.should(have.exact_texts('My WRONG text', 'My WRONG text'))
        pytest.fail('should have failed on size mismatch')
    except AssertionError as error:
        # THEN
        assert (
            'Message: \n'
            '\n'
            'Timed out after 0.5s, while waiting for:\n'
            "browser.all(('css selector', 'my-paragraph')): shadow roots.all(('css "
            "selector', '[name=my-text]')).has exact texts ('My WRONG text', 'My WRONG "
            "text')\n"
            '\n'
            "Reason: AssertionError: actual visible_texts: ['My default text', 'My "
            "default text']\n"
        ) in str(error)
