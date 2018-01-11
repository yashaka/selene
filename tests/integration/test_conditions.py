import os

from selene import config, browser
from selene.browser import driver
from selene.browsers import BrowserName
from selene.conditions import is_matched
from selene.support.conditions import be
from selene.support.jquery_style_selectors import s

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def setup_module(m):
    config.browser_name = BrowserName.CHROME
    browser.open_url(start_page)


def teardown_module(m):
    driver().quit()


def test_is_matched():
    unexisting_element = s('[name="ololo"]')
    assert is_matched(condition=be.in_dom, webelement=unexisting_element) is False
