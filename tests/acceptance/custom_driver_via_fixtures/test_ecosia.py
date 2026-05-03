# MIT License
#
# Copyright (c) 2015-2022 Iakiv Kramarenko
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
from selene import by, have


def _hide_cookie_overlays(browser):
    browser.driver.execute_script(
        """
        const selectors = [
          '.banner.cookie-notice',
          '.cookie-notice',
          '[class*="cookie"][class*="notice"]',
          '[class*="cookie"][class*="banner"]',
        ];
        selectors.forEach((selector) => {
          document.querySelectorAll(selector).forEach((node) => {
            node.style.display = 'none';
            node.style.visibility = 'hidden';
            node.style.pointerEvents = 'none';
          });
        });
        """
    )


def test_search(browser):
    browser.open('https://www.ecosia.org/')
    browser.element(by.name('q')).type(
        'github yashaka/selene python User-oriented API'
    ).press_enter()

    _hide_cookie_overlays(browser)
    first_result_link = browser.all('.web-result').first.element('.result__link')
    try:
        first_result_link.click()
    except Exception:
        # Ecosia may render consent overlay after results are already present.
        _hide_cookie_overlays(browser)
        browser.driver.execute_script(
            "arguments[0].click();",
            first_result_link.locate(),
        )

    browser.should(have.title_containing('yashaka/selene'))
