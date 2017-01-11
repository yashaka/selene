import os

from selene import config
from selene.conditions import exact_text
from selene.tools import visit, make_screenshot, s

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def test_can_make_screenshot_with_default_name():
    visit(start_page)
    path = make_screenshot()
    assert "/Users/sepi/screenshots/screen_0.png" == path


def test_can_make_screenshot_with_custom_name():
    visit(start_page)
    path = make_screenshot(filename="custom")
    assert "/Users/sepi/screenshots/custom_1.png" == path


def test_can_save_screenshot_to_custom_folder():
    config.screenshot_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    visit(start_page)
    path = make_screenshot()
    assert "/Users/sepi/PycharmProjects/selene/tests/screen_2.png" == path
    assert os.path.isfile(path)


def test_can_make_screenshot_automatically():
    visit(start_page)
    s("#selene_link").should_have(exact_text("Selen site"))
