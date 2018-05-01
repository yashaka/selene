import os

from selene import config, browser
from selene.conditions import in_dom, hidden, text, size
from selene.support import by
from selene.support.jquery_style_selectors import s

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def setup_module(m):
    config.browser_name = "chrome"
    browser.open_url(start_page)
    s("#hidden_button").should_be(in_dom).should_be(hidden)


def test_get_actual_hidden_webelement():
    s("#hidden_button").get_actual_webelement()


def test_find_selenium_element_from_hidden_element():
    s("#hidden_button").find_element(*by.be_following_sibling())


def test_find_selenium_elements_from_hidden_element():
    s("#hidden_button").find_elements(*by.be_following_sibling())


def test_find_selene_element_from_hidden_element():
    s("#hidden_button").following_sibling.should_have(text("Inner Link"))


def test_find_selene_collection_from_hidden_context():
    s("#hidden_button").ss(by.be_following_sibling()).should_have(size(6))
