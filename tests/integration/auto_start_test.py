import os

from selene.conditions import exact_text
from selene.browser import open_url, set_driver, driver
from selene.support.jquery_style_selectors import s
from tests.acceptance.helpers.helper import get_test_driver

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def test_manual_start():
    driver = get_test_driver()
    set_driver(driver)
    open_url(start_page)
    s("#header").should_have(exact_text("Selene"))


def test_manual_start_2():
    open_url(start_page)
    s("#selene_link").should_have(exact_text("Selene site"))

def test_auto_start():
    open_url(start_page)
    s("#header").should_have(exact_text("Selene"))


def test_auto_start_2():
    open_url(start_page)
    s("#selene_link").should_have(exact_text("Selene site"))

def teardown_module(m):
    driver().quit()
