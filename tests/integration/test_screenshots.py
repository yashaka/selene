import os

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from selene import config
from selene.conditions import exact_text
from selene.tools import visit, take_screenshot, s, set_driver, get_driver

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'
original_default_screenshot_folder = config.screenshot_folder
origina_timeout = config.timeout


def setup_function(f):
    config.screenshot_folder = original_default_screenshot_folder
    config.timeout = origina_timeout


def setup_module(m):
    set_driver(webdriver.Firefox())


def teardown_module(m):
    get_driver().quit()


def get_default_screenshot_folder():
    return config.screenshot_folder


def get_screen_id():
    return config.counter.next() - 1


def test_can_make_screenshot_with_default_name():
    visit(start_page)
    actual = take_screenshot()

    # todo: adjust to work on windows too:)
    expected = '{path}/screen_{id}.png'.format(path=get_default_screenshot_folder(),
                                               id=get_screen_id())
    assert expected == actual
    assert os.path.exists(actual)


def test_can_make_screenshot_with_custom_name():
    visit(start_page)
    actual = take_screenshot(filename="custom")

    expected = '{path}/custom.png'.format(path=get_default_screenshot_folder())
    assert expected == actual
    assert os.path.exists(actual)


def test_can_save_screenshot_to_custom_folder_specified_through_config():
    config.screenshot_folder = os.path.dirname(os.path.abspath(__file__)) + '/../../build/screenshots'
    visit(start_page)
    actual = take_screenshot()

    expected = '{path}/screen_{id}.png'.format(path=config.screenshot_folder,
                                               id=get_screen_id())
    assert expected == actual
    assert os.path.isfile(actual)
    assert os.path.exists(actual)


def test_can_save_screenshot_to_custom_folder_specified_as_parameter():
    screenshot_folder = os.path.dirname(os.path.abspath(__file__)) + '/../../build/screenshots'
    visit(start_page)
    actual = take_screenshot(path=screenshot_folder)

    expected = '{path}/screen_{id}.png'.format(path=screenshot_folder,
                                               id=get_screen_id())
    assert expected == actual
    assert os.path.isfile(actual)
    assert os.path.exists(actual)


def test_can_save_screenshot_to_custom_folder_with_custom_name():
    screenshot_folder = os.path.dirname(os.path.abspath(__file__)) + '/../../build/screenshots'
    visit(start_page)
    actual = take_screenshot(path=screenshot_folder,
                             filename="custom_file_in_custom_folder")

    expected = '{path}/custom_file_in_custom_folder.png'.format(path=screenshot_folder)
    assert expected == actual
    assert os.path.isfile(actual)
    assert os.path.exists(actual)


def test_can_make_screenshot_automatically():
    visit(start_page)
    config.timeout = 0.1
    with pytest.raises(TimeoutException) as ex:
        s("#selene_link").should_have(exact_text("Selen site"))
    expected = '{path}/screen_{id}.png'.format(path=get_default_screenshot_folder(),
                                               id=get_screen_id())
    assert os.path.exists(expected)
