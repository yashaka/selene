from selene.helpers import merge


class Filler(object):
    # todo: think on renaming to #filled_with taking into account that method returns self...
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
            for (field, value) in options.iteritems():
                getattr(self, field).set(value)  # todo: think on: `adding (value != None) and` to the start, in case somebody would put None to the opts...
        return self


class PageObject(Filler):
    @classmethod
    def get(cls, visit=True):  # todo: think on: is `visit` good name? maybe `open` would be better?
        """ a factory to create and load/open page """
        page = cls()
        if visit and hasattr(page, 'open'):
            page.open()
        return page

    # todo: think on: mixing in the selene.elements.Container class instead of defining this constructor here
    def __init__(self):
        if hasattr(self, 'init'):
            self.init()