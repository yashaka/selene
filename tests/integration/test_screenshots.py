import os

import pytest
from selenium.common.exceptions import TimeoutException

import selene
from selene import config
from selene.conditions import exact_text
from selene.tools import visit, make_screenshot, s

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def get_screen_id():
    return selene.tools.counter.next() - 1


def test_can_make_screenshot_with_default_name():
    visit(start_page)
    actual = make_screenshot()

    expected = "/Users/sepi/.selene/screenshots/{id}/screen_{id}.png".format(id=get_screen_id())
    assert expected == actual
    assert os.path.exists(actual)


def test_can_make_screenshot_with_custom_name():
    visit(start_page)
    actual = make_screenshot(filename="custom")

    expected = "/Users/sepi/.selene/screenshots/{id}/custom_{id}.png".format(id=get_screen_id())
    assert expected == actual
    assert os.path.exists(actual)


def test_can_save_screenshot_to_custom_folder():
    config.screenshot_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    visit(start_page)
    actual = make_screenshot()

    expected = "/Users/sepi/PycharmProjects/selene/tests/{id}/screen_{id}.png".format(id=get_screen_id())
    assert expected == actual
    assert os.path.isfile(actual)
    assert os.path.exists(actual)


def test_can_make_screenshot_automatically():
    config.screenshot_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    visit(start_page)
    with pytest.raises(TimeoutException) as ex:
        s("#selene_link").should_have(exact_text("Selen site"))
    expected = "/Users/sepi/PycharmProjects/selene/tests/{id}/screen_{id}.png".format(id=get_screen_id())
    assert os.path.exists(expected)
