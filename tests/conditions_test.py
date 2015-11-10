import os

from selene import settings, visit, s
from selene.conditions import absent, present, has_text


def setup_module():
    settings.app_host = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/resources/testapp/'
    visit('elements.html')


def test_absent_condition():
    s('.ffff').insist(absent)


def test_present_condition():
    s('.css').insist(present)


def test_has_test_condition():
    s('ol > li').insist(has_text)
