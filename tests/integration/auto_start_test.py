import os

from selene.conditions import exact_text
from selene.tools import visit, s, set_driver, get_driver
from tests.acceptance.helpers.helper import get_test_driver

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def test_manual_start():
    driver = get_test_driver()
    set_driver(driver)
    visit(start_page)
    s("#header").should_have(exact_text("Selene"))


def test_manual_start_2():
    visit(start_page)
    s("#selene_link").should_have(exact_text("Selene site"))

def test_auto_start():
    visit(start_page)
    s("#header").should_have(exact_text("Selene"))


def test_auto_start_2():
    visit(start_page)
    s("#selene_link").should_have(exact_text("Selene site"))

def teardown_module(m):
    get_driver().quit()
