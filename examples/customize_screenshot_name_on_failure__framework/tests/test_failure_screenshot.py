from urllib.parse import quote

import pytest

from selene import browser, have


@pytest.mark.xfail(reason='demonstrates custom failure screenshot naming')
def test_custom_screenshot_name_on_failure():
    html = quote('<h1 id="status">Ready</h1>')

    browser.open(f'data:text/html;charset=utf-8,{html}')

    browser.element('#status').should(have.exact_text('Done'))