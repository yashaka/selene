from future.utils import iteritems

from selene.elements import SeleneElement
from selene.helpers import merge
from selene.support.conditions import be
from selene.support.conditions import have
from selene.browser import visit, ss, s


class SelectList(object):
    def __init__(self, element):
        # type: (SeleneElement) -> None
        self._element = element

    def open(self):
        self._element.click()

    def _options(self):
        return self._element.all('option')

    def select_by_value(self, value):
        self._options().element_by(have.value(value)).click()

    def select_by_text(self, text):
        self._options().element_by(have.text(text)).click()

    def select_by_exact_text(self, text):
        self._options().element_by(have.exact_text(text)).click()

    def set(self, value):
        self.open()
        self.select_by_value(value)


class Filler(object):
    def __init__(self, element):
        self._element = element

    def fill_with(self, opts=None, *other_opts, **opts_as_kwargs):
        """
        fills fields of self with values passed in dicts in one of the following ways:
        as one dict via **kwargs in case the order of fields does not matter:
            fill_with(some_field="value", some_other_field="other value")
        as many dicts via *args if the order for some fields does matter:
            fill_with({"field1_should_be_set_first"="value"},
                      {"field_dependent_on_field1"="other value", "other_field": "some other value"})
        """
        if not opts: opts = {}
        list_of_opts = [merge(opts, opts_as_kwargs)] + list(other_opts)
        for options in list_of_opts:
            for (field, value) in iteritems(options):
                getattr(self._element, field).set(value)
        return self


class Order(object):
    def __init__(self):
        self.details = self.Details(s('#order_details'))
        self.add_item = s('#add_item')
        self.items = self.Items(ss('[id^="item"]'))

    def open(self):
        visit('order.html')

    def add_item_with(self, **name_and_other_data):
        self.add_item.click()
        return self.items[-1].fill_with(**name_and_other_data)

    class Details(object):
        def __init__(self, container):
            self._container = container
            self.first_name = container.s('[name="first_name"]')
            self.last_name = container.s('[name="last_name"]')
            self.salutation = SelectList(container.s('#salutation'))
            self.salutation_options = container.ss('#salutation option')

        def fill_with(self, opts=None, *other_opts, **opts_as_kwargs):
            Filler(self).fill_with(opts, *other_opts, **opts_as_kwargs)
            return self

    class Items(object):
        def __init__(self, elements):
            self._elements = elements

        def __getitem__(self, item):
            return self.Item(self._elements[item])

        class Item(object):
            def __init__(self, container):
                self._container = container
                self.name = container.s('.item_name')
                self.other_data = container.s('.item_other_data')

                self.show_advanced_options_selector = container.s('.show_advanced_options_selector')
                self.advanced_options_selector = self.AdvancedOptionsSelector(self._container.s('.advanced_options_selector'))
                self.show_advanced_options = container.s('.show_advanced_options')
                self.advanced_options = self.AdvancedOptions(self._container.ss('.advanced_options .options_list li'))

                self.clear_options = container.s('.clear_options')

            def fill_with(self, opts=None, *other_opts, **opts_as_kwargs):
                Filler(self).fill_with(opts, *other_opts, **opts_as_kwargs)
                return self

            def add_advanced_options(self, *options_data):
                for filter_data in options_data:
                    self.advanced_options_selector.add_filter_with(*filter_data)
                self.advanced_options_selector.apply_filtered_options.click()
                return self

            class AdvancedOptionsSelector(object):
                def __init__(self, container):
                    self._container = container
                    self.add_options_filter = container.s('.add_options_filter')
                    self.apply_filtered_options = container.s('.apply_filtered_options')
                    self.filters_elements = container.ss('[id^="options_filter"]')

                def filter(self, index):
                    return self.OptionsFilter(self.filters_elements[index])

                def add_filter_with(self, *opts_sequence):
                    self.add_options_filter.click()
                    Filler(self.filter(-1)).fill_with(*opts_sequence)
                    return self

                def should_be_hidden(self):
                    self._container.should(be.hidden)

                class OptionsFilter(object):
                    def __init__(self, container):
                        self.option_type = SelectList(container.s('.options_scope_type'))
                        self.scope = SelectList(container.s('.options_scope'))

            class AdvancedOptions(object):
                def __init__(self, elements):
                    self._elements = elements

                def should_be(self, *texts):
                    self._elements.should(have.exact_texts(*texts))

                def should_be_empty(self):
                    self._elements.should(be.empty)

            class AdvancedOption(object):
                def __init__(self):
                    # todo: implement...
                    pass


