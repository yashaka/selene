import logging
import os

from selene import config
from selene.browser import open_url, driver
from selene.support.jquery_style_selectors import s

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def setup_module(m):
    config.browser_name = "chrome"


def test_can_scroll_to():
    open_url(start_page)
    logging.warning(driver().current_url)
    driver().set_window_size(300, 400)
    s("#invisible_link").scroll_to().click()
