import types

import pytest

from selene.core import match
from selene.core.exceptions import ConditionNotMatchedError


class DummyWebElement:
    def __init__(
        self,
        *,
        displayed=True,
        enabled=True,
        selected=False,
        text='hello world',
        attrs=None,
        css=None,
        js=None,
    ):
        self._displayed = displayed
        self._enabled = enabled
        self._selected = selected
        self.text = text
        self._attrs = attrs or {}
        self._css = css or {}
        self._js = js or {}

    def is_displayed(self):
        return self._displayed

    def is_enabled(self):
        return self._enabled

    def is_selected(self):
        return self._selected

    def get_attribute(self, name):
        return self._attrs.get(name)

    def value_of_css_property(self, name):
        return self._css.get(name)

    def get_property(self, name):
        return self._js.get(name)


class DummyElement:
    def __init__(self, webelement, driver=None):
        self._webelement = webelement
        self.config = types.SimpleNamespace(driver=driver)

    def __call__(self):
        return self._webelement


class DummyCollection:
    def __init__(self, webelements):
        self._items = webelements

    def __call__(self):
        return self._items


class DummyBrowser:
    def __init__(self, *, url='https://example.test', title='Example', tabs=None):
        tabs = tabs or ['a', 'b']
        self.driver = types.SimpleNamespace(
            current_url=url,
            title=title,
            window_handles=tabs,
            execute_script=lambda script, *args: {'script': script, 'args': args},
        )


def test_element_visibility_enabled_clickable_and_presence_conditions():
    visible_enabled = DummyElement(DummyWebElement(displayed=True, enabled=True))
    hidden = DummyElement(DummyWebElement(displayed=False, enabled=True))

    match.element_is_visible.call(visible_enabled)
    match.element_is_enabled.call(visible_enabled)
    match.element_is_clickable.call(visible_enabled)
    match.element_is_present.call(visible_enabled)
    match.element_is_hidden.call(hidden)
    match.element_is_absent.call(DummyElement(None))

    with pytest.raises(ConditionNotMatchedError):
        match.element_is_hidden.call(visible_enabled)


def test_element_focused_and_selected_conditions():
    focused_we = DummyWebElement(selected=True)
    not_focused_we = DummyWebElement(selected=False)
    driver = types.SimpleNamespace(execute_script=lambda script: focused_we)

    match.element_is_focused.call(DummyElement(focused_we, driver=driver))
    match.element_is_selected.call(DummyElement(focused_we))

    with pytest.raises(ConditionNotMatchedError):
        match.element_is_focused.call(DummyElement(not_focused_we, driver=driver))


def test_element_text_and_exact_text_conditions():
    element = DummyElement(DummyWebElement(text='hello world'))

    match.element_has_text('hello').call(element)
    match.element_has_exact_text('hello world').call(element)

    with pytest.raises(AssertionError, match='actual text: hello world'):
        match.element_has_exact_text('HELLO').call(element)


def test_element_js_property_condition_and_collection_variants():
    element = DummyElement(DummyWebElement(js={'checked': 'yes'}))
    collection = DummyCollection(
        [
            DummyWebElement(js={'checked': 'yes'}),
            DummyWebElement(js={'checked': 'yesterday'}),
        ]
    )

    cond = match.element_has_js_property('checked')
    cond.call(element)
    cond.value('yes').call(element)
    cond.value_containing('ye').call(element)
    cond.values('yes', 'yesterday').call(collection)
    cond.values_containing('ye', 'day').call(collection)


def test_element_css_property_condition_and_collection_variants():
    element = DummyElement(DummyWebElement(css={'display': 'inline-block'}))
    collection = DummyCollection(
        [
            DummyWebElement(css={'display': 'inline-block'}),
            DummyWebElement(css={'display': 'block'}),
        ]
    )

    cond = match.element_has_css_property('display')
    cond.call(element)
    cond.value('inline-block').call(element)
    cond.value_containing('inline').call(element)
    cond.values('inline-block', 'block').call(collection)
    cond.values_containing('inline', 'lock').call(collection)


def test_element_attribute_related_conditions_and_ignore_case_warning():
    element = DummyElement(DummyWebElement(attrs={'role': 'Button', 'value': 'ABC', 'class': 'btn btn-primary'}))
    collection = DummyCollection(
        [
            DummyWebElement(attrs={'role': 'Button', 'value': 'ABC'}),
            DummyWebElement(attrs={'role': 'Link', 'value': 'ABCD'}),
        ]
    )

    cond = match.element_has_attribute('role')
    cond.call(element)
    cond.value('Button').call(element)
    cond.value_containing('utto').call(element)
    cond.values('Button', 'Link').call(collection)
    cond.values_containing('utt', 'ink').call(collection)

    with pytest.warns(FutureWarning):
        cond.value('button', ignore_case=True).call(element)
    with pytest.warns(FutureWarning):
        cond.value_containing('but', ignore_case=True).call(element)

    match.element_has_value('ABC').call(element)
    match.element_has_value_containing('BC').call(element)
    match.collection_has_values('ABC', 'ABCD').call(collection)
    match.collection_has_values_containing('AB', 'BCD').call(collection)
    match.element_has_css_class('btn').call(element)


def test_element_blank_and_tag_conditions():
    blank = DummyElement(DummyWebElement(text='', attrs={'value': ''},))
    tagged = DummyElement(DummyWebElement())
    tagged._webelement.tag_name = 'section'

    match.element_is_blank.call(blank)
    match.element_has_tag('section').call(tagged)
    match.element_has_tag_containing('ect').call(tagged)


def test_collection_empty_and_size_conditions_with_deprecation_warning():
    empty = DummyCollection([])
    filled = DummyCollection([DummyWebElement(), DummyWebElement(), DummyWebElement()])

    with pytest.warns(DeprecationWarning):
        match.collection_is_empty.call(empty)

    match.collection_has_size(3).call(filled)
    match.collection_has_size_greater_than(2).call(filled)
    match.collection_has_size_greater_than_or_equal(3).call(filled)
    match.collection_has_size_less_than(4).call(filled)
    match.collection_has_size_less_than_or_equal(3).call(filled)


def test_collection_texts_and_exact_texts_consider_only_visible():
    items = DummyCollection(
        [
            DummyWebElement(displayed=True, text='one'),
            DummyWebElement(displayed=False, text='hidden'),
            DummyWebElement(displayed=True, text='two'),
        ]
    )

    match.collection_has_texts('on', 'tw').call(items)
    match.collection_has_exact_texts('one', 'two').call(items)


def test_browser_url_title_tabs_and_script_conditions():
    browser = DummyBrowser(url='https://host/path', title='Page title', tabs=['t1', 't2', 't3'])

    match.browser_has_url('https://host/path').call(browser)
    match.browser_has_url_containing('host').call(browser)
    match.browser_has_title('Page title').call(browser)
    match.browser_has_title_containing('title').call(browser)

    match.browser_has_tabs_number(3).call(browser)
    match.browser_has_tabs_number_greater_than(2).call(browser)
    match.browser_has_tabs_number_greater_than_or_equal(3).call(browser)
    match.browser_has_tabs_number_less_than(4).call(browser)
    match.browser_has_tabs_number_less_than_or_equal(3).call(browser)

    with pytest.raises(AssertionError, match=r"actual script_result: {'script': 'return 1', 'args': \(\)}"):
        match.browser_has_script_returned(1, 'return 1').call(browser)


def test_browser_has_js_returned_is_deprecated_alias():
    browser = DummyBrowser()

    with pytest.warns(DeprecationWarning):
        with pytest.raises(AssertionError):
            match.browser_has_js_returned('expected', 'return 1').call(browser)
