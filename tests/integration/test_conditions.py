import os

from selene import config, browser
from selene.browser import driver
from selene.browsers import BrowserName
from selene.conditions import exist
from selene.support.jquery_style_selectors import s

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def setup_module(m):
    config.browser_name = BrowserName.CHROME
    browser.open_url(start_page)


def teardown_module(m):
    driver().quit()


def test_is_matched():
    s('[name="ololo"]').should_not(exist)
