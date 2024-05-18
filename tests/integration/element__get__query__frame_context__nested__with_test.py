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

from selene import command, have, query, be


# TODO: break down into 2 tests
def test_actions_on_nested_frames_element_via_with_statement(session_browser):
    browser = session_browser.with_(timeout=1.0)

    # GIVEN even before opened browser
    browser.open('https://the-internet.herokuapp.com/nested_frames')

    # WHEN
    with browser.element('[name=frame-top]').get(query._frame_context):
        with browser.element('[name=frame-middle]').get(query._frame_context):
            browser.element(
                '#content',
                # THEN
            ).should(have.exact_text('MIDDLE'))
        # AND
        browser.element('[name=frame-right]').should(be.visible)

    # WHEN failed
    try:
        with browser.element('[name=frame-top]').get(query._frame_context):
            with browser.element('[name=frame-middle]').get(
                query._nested_frame_context
            ):
                browser.element(
                    '#content',
                ).should(have.exact_text('LEFT'))
        pytest.fail('should have failed on text mismatch')
    except AssertionError as error:
        # THEN
        assert (
            'Message: \n'
            '\n'
            'Timed out after 1.0s, while waiting for:\n'
            "browser.element(('css selector', '#content')).has exact text LEFT\n"
            '\n'
            'Reason: AssertionError: actual text: MIDDLE\n'
        ) in str(error)
