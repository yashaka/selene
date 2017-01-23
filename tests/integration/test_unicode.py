# -*- coding: utf-8 -*-
import os

from selene import config
from selene.browsers import Browser
from selene.conditions import text, texts
from selene.tools import visit, s, ss

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def setup_module(m):
    config.browser_name = Browser.CHROME
    visit(start_page)


def test_ru_text():
    s("#ru-text").should_have(text("Селен"))


def test_ru_text_with_array():
    ss(".list > li").should_have(texts("Один", "Два", "Три"))
