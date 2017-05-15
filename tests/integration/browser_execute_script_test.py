import logging
import os

from selene import config
from selene import browser
from selene.support.jquery_style_selectors import s

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def setup_module(m):
    config.browser_name = "chrome"


def test_can_scroll_to_via_js():
    browser.open_url(start_page)
    logging.warning(browser.driver().current_url)
    browser.driver().set_window_size(300, 400)
    link = s("#invisible_link")
    # browser.driver().execute_script("arguments[0].scrollIntoView();", link)
    # - this code does not work because SeleneElement is not JSON serializable, and I don't know the way to fix it
    #   - because all available in python options needs a change to json.dumps call - adding a second parameter to it
    #     and specify a custom encoder, but we can't change this call inside selenium webdriver implementation
    browser.driver().execute_script("arguments[0].scrollIntoView();", link.get_actual_webelement())
    link.click()
