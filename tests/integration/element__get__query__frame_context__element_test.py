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

from selene import command, have, query


# TODO: consider implementing the following concept
def x_test_actions_within_frame_context(session_browser):
    browser = session_browser.with_(timeout=1.0)

    # GIVEN even before opened browser

    toolbar = browser.element('.tox-toolbar__primary')
    text_area = browser.element('.tox-edit-area__iframe').get(
        query._frame_element('#tinymce')
    )
    '''
    # Option B:
    text_area = browser.element('.tox-edit-area__iframe')._frame_element('#tinymce')
    # option C:
    text_area = browser._frame('.tox-edit-area__iframe').element('#tinymce')
    '''

    # WHEN
    browser.open('https://the-internet.herokuapp.com/iframe')

    # THEN everything inside frame context
    text_area.element('p').should(
        have.js_property('innerHTML').value(
            'Your content goes here.',
        )
    ).perform(command.select_all)

    # AND (outside frame context)
    toolbar.element('[title=Bold]').click()

    # AND coming back inside frame context
    text_area.element('p').should(
        have.js_property('innerHTML').value('<strong>Your content goes here.</strong>')
    )

    text_area.perform(command.select_all).type(
        'New content',
    ).element('p').should(
        have.js_property('innerHTML').value(
            '<strong>New content</strong>',
        )
    )
