import os

from selenium import webdriver

from selene.conditions import empty, exist, exact_texts, hidden
from selene import config
from selene.tools import set_driver, get_driver
from tests.order.pages.order import Order


def setup_function(m):
    set_driver(webdriver.Firefox())
    config.app_host = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/orderapp/'


def teardown_function(m):
    get_driver().quit()
    config.app_host = ''


def test_it_fills_order():

    order = Order.get()
    order.details.fill_with(first_name='Johanna', last_name='Smith', salutation='Mrs')

    item = order.add_item_with(name='New Test Item', other_data='Some other specific data')
    item.show_advanced_options_selector.click()  # todo: think on how to make autocompletion work after item.
    item.add_advanced_options(
        [{'option_type': 'type1'}, {'scope': 'optionscope2fortype1'}],
        [{'option_type': 'type2'}, {'scope': 'optionscope3fortype2'}]
    )

    item.show_advanced_options.click()
    item.advanced_options.assure(exact_texts('optionscope2fortype1', 'optionscope3fortype2'))

    item.clear_options.click()
    item.advanced_options.assure(empty)

    item.show_advanced_options_selector.click()
    item.advanced_options_selector.assure(hidden)

    # todo: clear options finally


def test_it_fills_order_with_semi_automated_loading_of_widgets():

    order = Order.get()
    order.details.fill_with(first_name='Johanna', last_name='Smith', salutation='Mrs')

    item = order.add_item_with(name='New Test Item', other_data='Some other specific data')
    # item.show_advanced_options_selector.click()
    item.advanced_options_selector.open()
    item.add_advanced_options(
        [{'option_type': 'type1'}, {'scope': 'optionscope2fortype1'}],
        [{'option_type': 'type2'}, {'scope': 'optionscope3fortype2'}]
    )

    # item.show_advanced_options.click()
    item.advanced_options.open().assure(exact_texts('optionscope2fortype1', 'optionscope3fortype2'))

    item.clear_options.click()
    item.advanced_options.assure(empty)

    # item.show_advanced_options_selector.click()
    item.advanced_options_selector.open()
    item.advanced_options_selector.assure(hidden)