from selene.helpers import merge
from future.utils import iteritems


class LoadableContainer(object):
    def __init__(self):
        if hasattr(self, 'init'):
            self.init()
        self._open = lambda: self

    def init(self):
        """ to be defined in descendants in order to init its sub-elements """
        pass

    def to_open(self, how_to_open_fn):
        self._open = how_to_open_fn
        return self

    def open(self):
        self._open()
        return self

    get = open


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
            for (field, value) in iteritems(options):
                getattr(self, field).set(value)  # todo: think on: `adding (value != None) and` to the start, in case somebody would put None to the opts...
        return self


class PageObject(LoadableContainer, Filler):
    @classmethod
    def get(cls, visit=True):  # todo: think on: is `visit` good name? maybe `open` would be better?
        """ a factory to create and load/open page """
        page = cls()
        if visit and hasattr(page, 'open'):
            page.open()
        return page
