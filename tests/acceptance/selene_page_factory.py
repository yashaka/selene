import os

import selene
from selene.browsers import BrowserName
from selene.conditions import exact_text, visible, hidden
from selene.browser import open_url
from selene.support.jquery_style_selectors import s

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def test_can_init_default_browser_on_visit():
    open_url(start_page)
    s("#header").should_have(exact_text("Selene"))


def test_can_init_custom_browser_on_visit():
    selene.config.browser_name = BrowserName.CHROME
    open_url(start_page)
    s("#selene_link").should_have(exact_text("Selene site"))
