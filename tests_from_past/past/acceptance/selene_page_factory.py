# MIT License
#
# Copyright (c) 2015-2021 Iakiv Kramarenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os

import selene
from selene.api.past import BrowserName
from selene.api.past import exact_text
from selene.api.past import open_url
from selene.support.jquery_style_selectors import s

start_page = (
    'file://'
    + os.path.abspath(os.path.dirname(__file__))
    + '/../resources/start_page.html'
)


def test_can_init_default_browser_on_visit():
    open_url(start_page)
    s("#header").should_have(exact_text("Selene"))


def test_can_init_custom_browser_on_visit():
    selene.config.browser_name = BrowserName.MARIONETTE
    open_url(start_page)
    s("#selene_link").should_have(exact_text("Selene site"))
