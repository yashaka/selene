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
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selene.support.shared import browser
from tests.integration.helpers.givenpage import GivenPage


def setup_module():
    browser.set_driver(webdriver.Chrome(ChromeDriverManager().install()))
    browser.driver().set_window_size(300, 400)


def teardown_module():
    browser.quit()


def test_can_scroll_to_via_js():
    GivenPage(browser.driver).opened_with_body(
        '''
        <div id="paragraph" style="margin: 400px">
        </div>
        <a id="not-viewable-link" href="#header"/>
        <h1 id="header">Heading 1</h2>
        '''
    )
    link = browser.element("#not-viewable-link")
    # browser.driver().execute_script("arguments[0].scrollIntoView();", link)
    # - this code does not work because SeleneElement is not JSON serializable, and I don't know the way to fix it
    #   - because all available in python options needs a change to json.dumps call - adding a second parameter to it
    #     and specify a custom encoder, but we can't change this call inside selenium webdriver implementation

    browser.execute_script("arguments[0].scrollIntoView();", link())
    link.click()
    # actually, selene .click() scrolls to any element in dom, so it's not an option fo
    # in this case we should find another way to check page is scrolled down or to choose another script.

    assert "header" in browser.driver.current_url
