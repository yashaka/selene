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

from selene import browser, command, have, query
from tests import const


def teardown_function():
    browser.quit()


class WYSIWYG:
    toolbar = browser.element('.tox-toolbar__primary')
    text_area_frame = query._frame_context(browser.element('.tox-edit-area__iframe'))
    text_area = browser.element('#tinymce')

    def open(self):
        browser.open(const.TINYMCE_URL)
        return self

    def set_bold(self):
        self.toolbar.element('[aria-label=Bold]').click()
        return self

    @text_area_frame._within
    def should_have_text_html(self, text_html):
        self.text_area.should(have.js_property('innerHTML').value(text_html))
        return self

    @text_area_frame._within
    def select_all_text(self):
        self.text_area.perform(command.select_all)
        return self

    @text_area_frame._within
    def reset_to(self, text):
        self.text_area.perform(command.select_all).type(text)
        return self


def test_page_object_steps_within_frame_context():
    wysiwyg = WYSIWYG().open()

    wysiwyg.should_have_text_html(
        '<p>Hello, World!</p>',
    ).select_all_text().set_bold().should_have_text_html(
        '<p><strong>Hello, World!</strong></p>',
    )

    wysiwyg.reset_to('New content').should_have_text_html(
        '<p><strong>New content</strong></p>',
    )
