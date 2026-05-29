# MIT License
#
# Copyright (c) 2026 Iakiv Kramarenko
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

from selene import have, query
from tests.integration.helpers.givenpage import GivenPage


def test_frame_context_reenter_and_back_to_default_content_on_given_page(
    session_browser,
):
    browser = session_browser.with_(timeout=1.0)
    page = GivenPage(browser.driver)

    page.opened_with_body("""
        <button id="outside" onclick="
            document.getElementById('outside-result').textContent='clicked'
        ">Outside</button>
        <div id="outside-result">initial</div>
        <iframe
            id="f"
            srcdoc="<html><body><div id='inside'>frame text</div></body></html>"
        ></iframe>
        """)

    frame_context = browser.element('#f').get(query._frame_context)

    with frame_context:
        with frame_context:
            browser.element('#inside').should(have.exact_text('frame text'))

    browser.element('#outside').click()
    browser.element('#outside-result').should(have.exact_text('clicked'))
