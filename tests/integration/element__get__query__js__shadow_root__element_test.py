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

from selene import have, query
from tests.integration.helpers.givenpage import GivenPage


def test_actions_on_shadow_root_element(session_browser):
    # GIVEN
    browser = session_browser.with_(timeout=0.5)
    page = GivenPage(browser.driver)
    paragraphs = browser.all('my-paragraph')

    # WHEN even before opened browser
    paragraph_1_shadow = paragraphs.first.get(query.js.shadow_root)
    paragraph_2_shadow = paragraphs.second.get(query.js.shadow_root)
    my_shadowed_text_1 = paragraph_1_shadow.element('[name=my-text]')
    my_shadowed_text_2 = paragraph_2_shadow.element('[name=my-text]')
    # AND
    page.opened_with_body('''
        <my-paragraph>Let's have some different text!</my-paragraph>
        <my-paragraph>Let's have some different text!\nIn a list!</my-paragraph>
        ''')
    page.execute_script('''
        document.querySelectorAll('my-paragraph').forEach(element => {
            element.attachShadow({mode: 'open'}).innerHTML =
                '<span name="my-text">My default text</span>'
        })
        ''')

    # THEN
    my_shadowed_text_1.should(have.exact_text("My default text"))
    my_shadowed_text_2.should(have.exact_text("My default text"))

    # WHEN failed
    try:
        my_shadowed_text_1.should(have.exact_text("My WRONG text"))
        pytest.fail('should have failed on size mismatch')
    except AssertionError as error:
        # THEN
        assert (
            'Message: \n'
            '\n'
            'Timed out after 0.5s, while waiting for:\n'
            "browser.all(('css selector', 'my-paragraph'))[0]: shadow root.element(('css "
            "selector', '[name=my-text]')).has exact text My WRONG text\n"
            '\n'
            'Reason: AssertionError: actual text: My default text\n'
        ) in str(error)
