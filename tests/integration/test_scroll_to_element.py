import os

from selene import config
from selene.tools import visit, s, get_driver

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def setup_module(m):
    config.browser_name = "chrome"


def test_can_scroll_to():
    visit(start_page)
    get_driver().set_window_size(300, 400)
    s("#invisible_link").scroll_to().click()
