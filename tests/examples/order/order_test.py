import os

from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager

from selene import config
from selene.tools import set_driver, get_driver
from tests.examples.order.app_model.order_widgets import Order


def setup_function(m):
    config.timeout = 4
    set_driver(webdriver.Firefox(executable_path=GeckoDriverManager().install()))
    config.app_host = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../../resources/orderapp/'


def teardown_function(m):
    get_driver().quit()
    config.app_host = ''


def test_it_fills_order():

    order = Order()

    order.open()
    order.details.fill_with(first_name='Johanna', last_name='Smith', salutation='Mrs')

    item = order.add_item_with(name='New Test Item', other_data='Some other specific data')
    item.show_advanced_options_selector.click()
    item.add_advanced_options(
        [{'option_type': 'type1'}, {'scope': 'optionscope2fortype1'}],
        [{'option_type': 'type2'}, {'scope': 'optionscope3fortype2'}]
    )

    item.show_advanced_options.click()
    item.advanced_options.should_be('optionscope2fortype1', 'optionscope3fortype2')

    item.clear_options.click()
    item.advanced_options.should_be_empty()

    item.show_advanced_options_selector.click()
    item.advanced_options_selector.should_be_hidden()