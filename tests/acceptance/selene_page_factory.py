import os

import selene
from selene.browsers import Browser
from selene.conditions import exact_text, visible, hidden
from selene.browser import visit, s

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def test_can_init_default_browser_on_visit():
    visit(start_page)
    s("#header").should_have(exact_text("Selene"))


def test_can_init_custom_browser_on_visit():
    selene.config.browser_name = Browser.CHROME
    visit(start_page)
    s("#selene_link").should_have(exact_text("Selene site"))
