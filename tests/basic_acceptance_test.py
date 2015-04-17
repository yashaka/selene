import os
from selene import config
from selene.conditions import empty, eq, absent
from tests.resources.pages.order import Order
from selene.tools import *

config.app_host = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/resources/testapp/'


def test_it_fills_order():

    order = Order.get()
    order.details.fill_with(first_name='Johanna', last_name='Smith', salutation='Mrs')

    item = order.add_item_with(name='New Test Item', other_data='Some other specific data')
    item.add_advanced_options(
        [{'option_type': 'type1'}, {'scope': 'optionscope2fortype1'}],
        [{'option_type': 'type2'}, {'scope': 'optionscope3fortype2'}]
    )

    item.advanced_options.assure(eq(['optionscope2fortype1', 'optionscope3fortype2'], mapped='text'))

    item.clear_options.click()
    item.advanced_options.insist(empty)

    item.show_advanced_options_selector.click()
    item.advanced_options_selector.insist(absent)

    # todo: clear options finally

test_it_fills_order()


