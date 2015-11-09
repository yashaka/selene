import os

from selene import config, visit, s
from selene.conditions import absent, present, has_text


def setup_module():
    config.app_host = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/resources/testapp/'


def test_absent_condition():
    visit('elements.html')
    s('.ffff').insist(absent)


def test_present_condition():
    visit('elements.html')
    s('.css').insist(present)


def test_has_test_condition():
    visit('elements.html')
    s('ol > li').insist(has_text)
