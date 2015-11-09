from selene.elements import SElement
from selene.page_object import PageObject
from selene.tools import visit, ss, s
from selene.widgets import SelectList


class Order(PageObject):
    def init(self):
        self.details = self.Details('#order_details')
        self.add_item = s('#add_item')
        self.items = ss('[id^="item"]').of(self.Item)

    def open(self):
        visit('order.html')

    def add_item_with(self, **name_and_other_data):
        self.add_item.click()
        return self.items[-1].fill_with(**name_and_other_data)

    class Details(SElement):
        def init(self):
            self.first_name = self.s('[name="first_name"]')
            self.last_name = self.s('[name="last_name"]')
            self.salutation = self.s(SelectList('#salutation'))
            self.salutation_options = self.ss('#salutation option')

    class Item(SElement):
        def init(self):
            self.name = self.s('.item_name')
            self.other_data = self.s('.item_other_data')

            self.show_advanced_options_selector = self.s('.show_advanced_options_selector')
            self.advanced_options_selector = self.AdvancedOptionsSelector('.advanced_options_selector', context=self) \
                .to_open(lambda: self.show_advanced_options_selector.click())

            self.show_advanced_options = self.s('.show_advanced_options')
            self.advanced_options = self.ss('.advanced_options .options_list li').of(self.AdvancedOption)\
                .to_open(lambda: self.show_advanced_options.click())

            self.clear_options = self.s('.clear_options')

        def add_advanced_options(self, *options_data):
            for filter_data in options_data:
                self.advanced_options_selector.add_filter_with(*filter_data)
            self.advanced_options_selector.apply_filtered_options.click()
            return self

        class AdvancedOptionsSelector(SElement):
            def init(self):
                self.add_options_filter = self.s('.add_options_filter')
                self.apply_filtered_options = self.s('.apply_filtered_options')
                self.filters = self.ss('[id^="options_filter"]').of(self.OptionsFilter)

            def add_filter_with(self, *opts_sequence):
                self.add_options_filter.click()
                return self.filters[-1].fill_with(*opts_sequence)

            class OptionsFilter(SElement):
                def init(self):
                    self.option_type = SelectList('.options_scope_type', context=self)
                    self.scope = SelectList('.options_scope', context=self)

        # todo: think on: removing it, because it's not needed here...
        class AdvancedOptions(SElement):
            pass

        class AdvancedOption(SElement):
            def init(self):
                # todo: implement...
                pass


