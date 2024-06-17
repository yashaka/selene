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
from tests import const


class StringHandler(logging.Handler):
    terminator = '\n'

    def __init__(self):
        logging.Handler.__init__(self)
        self.stream = ''

    def emit(self, record):
        try:
            msg = self.format(record)
            # issue 35046: merged two stream.writes into one.
            self.stream += msg + self.terminator
        except Exception:
            self.handleError(record)


log = logging.getLogger(__file__)
log.setLevel(20)
handler = StringHandler()
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)


class LogToStringStreamContext:
    def __init__(self, title, params):
        self.title = title
        self.params = params

    def __enter__(self):
        log.info('%s: STARTED', self.title)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            log.info('%s: PASSED', self.title)
        else:
            log.info('%s: FAILED:\n\n%s\n%s', self.title, exc_type, exc_val)


def test_actions_on_frame_element_with_logging(session_browser):
    browser = session_browser.with_(
        timeout=0.5,
        _wait_decorator=support._logging.wait_with(context=LogToStringStreamContext),
    )

    # GIVEN even before opened browser

    toolbar = browser.element('.tox-toolbar__primary')
    text_area_frame = browser.element('.tox-edit-area__iframe').get(
        query._frame_context
    )
    text_area = text_area_frame._element('#tinymce')
    '''
    # TODO: consider Option B:
    text_area = browser._frame('.tox-edit-area__iframe').element('#tinymce')
    # – maybe even:
    #   (if we don't want to put something into browser that is not mobile relevant)
    text_area = web.frame('.tox-edit-area__iframe').element('#tinymce')
    # but isn't browser already a web?
    # shouldn't we substitute browser with context?
    # and then have browser or web for web context and mobile or app for mobile context?
    '''

    # WHEN
    browser.open(const.TINYMCE_URL)

    # THEN everything inside frame context
    text_area.element('p').should(
        have.js_property('innerHTML').value(
            'Hello, World!',
        )
    ).perform(command.select_all)

    # AND (outside frame context)
    toolbar.element('[aria-label=Bold]').click()

    # AND coming back inside frame context
    text_area.element('p').should(
        have.js_property('innerHTML').value('<strong>Hello, World!</strong>')
    )

    text_area.perform(command.select_all).type(
        'New content',
    ).element('p').should(
        have.js_property('innerHTML').value(
            '<strong>New content</strong>',
        )
    )

    # WHEN failed
    try:
        text_area.all('p').should(have.size(10))  # actual size is 1
        pytest.fail('should have failed on size mismatch')
    except AssertionError:
        # THEN everything is logged:
        assert (
            "element('.tox-edit-area__iframe'): element('#tinymce').element('p'): should "
            "have js property 'innerHTML' with value 'Hello, World!': STARTED\n"
            "element('.tox-edit-area__iframe'): element('#tinymce').element('p'): should "
            "have js property 'innerHTML' with value 'Hello, World!': PASSED\n"
            "element('.tox-edit-area__iframe'): element('#tinymce').element('p'): send "
            '«select all» keys shortcut as ctrl+a or cmd+a for mac: STARTED\n'
            "element('.tox-edit-area__iframe'): element('#tinymce').element('p'): send "
            '«select all» keys shortcut as ctrl+a or cmd+a for mac: PASSED\n'
            "element('.tox-toolbar__primary').element('[aria-label=Bold]'): click: STARTED\n"
            "element('.tox-toolbar__primary').element('[aria-label=Bold]'): click: PASSED\n"
            "element('.tox-edit-area__iframe'): element('#tinymce').element('p'): should "
            "have js property 'innerHTML' with value '<strong>Hello, World!</strong>': STARTED\n"
            "element('.tox-edit-area__iframe'): element('#tinymce').element('p'): should "
            "have js property 'innerHTML' with value '<strong>Hello, World!</strong>': PASSED\n"
            "element('.tox-edit-area__iframe'): element('#tinymce'): send «select all» "
            'keys shortcut as ctrl+a or cmd+a for mac: STARTED\n'
            "element('.tox-edit-area__iframe'): element('#tinymce'): send «select all» "
            'keys shortcut as ctrl+a or cmd+a for mac: PASSED\n'
            "element('.tox-edit-area__iframe'): element('#tinymce'): type: New content: "
            'STARTED\n'
            "element('.tox-edit-area__iframe'): element('#tinymce'): type: New content: "
            'PASSED\n'
            "element('.tox-edit-area__iframe'): element('#tinymce').element('p'): should "
            "have js property 'innerHTML' with value '<strong>New content</strong>': "
            'STARTED\n'
            "element('.tox-edit-area__iframe'): element('#tinymce').element('p'): should "
            "have js property 'innerHTML' with value '<strong>New content</strong>': "
            'PASSED\n'
            "element('.tox-edit-area__iframe'): element('#tinymce').all('p'): should have "
            'size 10: STARTED\n'
            "element('.tox-edit-area__iframe'): element('#tinymce').all('p'): should have "
            'size 10: FAILED:\n'
            '\n'
            "<class 'selene.core.exceptions.TimeoutException'>\n"
            'Message: \n'
            '\n'
            'Timed out after 0.5s, while waiting for:\n'
            "browser.element(('css selector', '.tox-edit-area__iframe')): element(('css "
            "selector', '#tinymce')).all(('css selector', 'p')).has size 10\n"
            '\n'
            'Reason: ConditionMismatch: actual size: 1\n'
        ) in handler.stream
