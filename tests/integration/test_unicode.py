# -*- coding: utf-8 -*-
import os

from selene import browser
from selene import config
from selene.browsers import Browser
from selene.conditions import texts, exact_text
from selene.support.jquery_style_selectors import s, ss

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def setup_module(m):
    config.browser_name = Browser.CHROME
    browser.open_url(start_page)


def test_ru_text():
    s("#ru-text").should_have(exact_text(u"Селен"))


def test_ru_text_with_array():
    ss(".list > li").should_have(texts(u"Один", u"Два", u"Три"))
