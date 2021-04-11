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

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selene.support.shared import config, browser
from tests.examples.widgets_aka_components_page_objects_style_for_spa_apps.model.widgets import (
    Order,
)


def setup_function():
    config.timeout = 4
    browser.set_driver(webdriver.Chrome(ChromeDriverManager().install()))
    config.base_url = 'file://{}/../../resources/orderapp/'.format(
        os.path.abspath(os.path.dirname(__file__))
    )


def teardown_function():
    browser.quit()


def test_it_fills_order():
    order = Order()

    order.open()
    order.details.fill_with(
        first_name='Johanna',
        last_name='Smith',
        salutation='Mrs',
    )

    item = order.add_item_with(
        name='New Test Item',
        other_data='Some other specific data',
    )
    item.show_advanced_options_selector.click()
    item.add_advanced_options(
        [{'option_type': 'type1'}, {'scope': 'optionscope2fortype1'}],
        [{'option_type': 'type2'}, {'scope': 'optionscope3fortype2'}],
    )

    item.show_advanced_options.click()
    item.advanced_options.should_be(
        'optionscope2fortype1', 'optionscope3fortype2'
    )

    item.clear_options.click()
    item.advanced_options.should_be_empty()

    item.show_advanced_options_selector.click()
    item.advanced_options_selector.should_be_hidden()
