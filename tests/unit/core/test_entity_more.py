import types

import pytest

from selene.core.condition import Condition
from selene.core.exceptions import TimeoutException, _SeleneError
from selene.core.entity import Collection, Element
from selene.core.locator import Locator


class DummyWait:
    def __init__(self, entity):
        self.entity = entity
        self.hook_failure = lambda e: e

    def for_(self, fn):
        return fn(self.entity)

    def until(self, condition):
        try:
            condition(self.entity)
            return True
        except Exception:
            return False

    def command(self, _description, fn):
        return fn(self.entity)

    def or_fail_with(self, hook):
        clone = DummyWait(self.entity)
        clone.hook_failure = hook
        return clone


class DummyConfig:
    def __init__(self):
        self.driver = types.SimpleNamespace(
            execute_script=lambda script, *args: ('executed', script, args)
        )
        self.log_outer_html_on_failure = False
        self.wait_for_no_overlap_found_by_js = False
        self.set_value_by_js = False
        self.type_by_js = False
        self.click_by_js = False

    def wait(self, entity):
        return DummyWait(entity)

    def with_(self, **_kwargs):
        return self


class DummyWebElement:
    def __init__(self, text='', with_defaults=True):
        self.text = text
        self.sent = []
        self.cleared = 0
        self.submitted = 0
        self.children = {}
        self.children_many = {}
        if with_defaults:
            self.children = {
                ('css selector', '.child'): DummyWebElement(
                    'child', with_defaults=False
                ),
            }
            self.children_many = {
                ('css selector', '.item'): [
                    DummyWebElement('a', with_defaults=False),
                    DummyWebElement('b', with_defaults=False),
                ],
            }

    def find_element(self, *by):
        return self.children[by]

    def find_elements(self, *by):
        return self.children_many.get(by, [])

    def clear(self):
        self.cleared += 1

    def click(self):
        self.sent.append('clicked')

    def send_keys(self, *value):
        self.sent.extend(value)

    def submit(self):
        self.submitted += 1

    def get_attribute(self, name):
        return f'attr:{name}'


def test_waiting_entity_core_methods_work_via_element():
    config = DummyConfig()
    element = Element(Locator('root', lambda: DummyWebElement('root')), config)
    condition = Condition('always', lambda e: e())

    assert element.perform(lambda e: e()) is element
    assert element.get(lambda e: e().text) == 'root'
    assert element.should(condition) is element
    assert element.wait_until(condition) is True
    assert element.matching(condition) is True


def test_element_with_locate_raw_call_cached_and_relatives():
    config = DummyConfig()
    root_we = DummyWebElement('root')
    element = Element(Locator('root', lambda: root_we), config)

    assert str(element) == 'root'
    assert element.locate() is root_we
    assert element.__raw__ is root_we
    assert element() is root_we
    assert element.with_() is not element

    cached = element.cached
    assert cached() is root_we

    child = element.element('.child')
    assert child().text == 'child'
    assert element.s('.child')().text == 'child'

    many = element.all('.item')
    assert [it.text for it in many()] == ['a', 'b']
    assert [it.text for it in element.ss('.item')()] == ['a', 'b']


def test_element_cached_preserves_error_when_initial_lookup_fails():
    config = DummyConfig()
    failing = Element(
        Locator('bad', lambda: (_ for _ in ()).throw(RuntimeError('x'))), config
    )

    cached = failing.cached
    with pytest.raises(RuntimeError, match='x'):
        cached()


def test_element_script_helpers_and_input_commands():
    config = DummyConfig()
    root_we = DummyWebElement('root')
    element = Element(Locator('root', lambda: root_we), config)

    result = element.execute_script('return 1', 2, 3)
    assert result[0] == 'executed'
    assert 'return 1' in result[1]

    with pytest.warns(DeprecationWarning):
        deprecated = element._execute_script('return args[0]', 1)
    assert deprecated[0] == 'executed'

    element.send_keys('a', 'b').press('c').press_enter().press_escape().press_tab()
    element.clear().submit()

    assert root_we.sent[:2] == ['a', 'b']
    assert root_we.cleared == 1
    assert root_we.submitted == 1


def test_collection_core_navigation_and_slicing():
    config = DummyConfig()
    items = [
        DummyWebElement('1'),
        DummyWebElement('2'),
        DummyWebElement('3'),
        DummyWebElement('4'),
    ]
    collection = Collection(Locator('items', lambda: items), config)

    assert str(collection) == 'items'
    assert collection.__raw__ == items
    assert collection() == items
    assert collection.with_() is not collection

    assert collection.first().text == '1'
    assert collection.second().text == '2'
    assert [el().text for el in collection.even] == ['2', '4']
    assert [el().text for el in collection.odd] == ['1', '3']
    assert [el().text for el in collection.from_(2)] == ['3', '4']
    assert [el().text for el in collection.to(2)] == ['1', '2']

    assert [el().text for el in collection[1:3]] == ['2', '3']
    assert collection[0]().text == '1'

    with pytest.raises(AssertionError, match='Cannot get element with index 9'):
        collection.element(9)()


def test_collection_by_filtered_and_element_by_paths(monkeypatch):
    config = DummyConfig()
    items = [DummyWebElement('one'), DummyWebElement('two')]
    collection = Collection(Locator('items', lambda: items), config)

    cond = Condition(
        'has o',
        lambda e: (
            None if 'o' in e().text else (_ for _ in ()).throw(AssertionError('no'))
        ),
    )

    filtered = collection.by(cond)
    assert [el.text for el in filtered()] == ['one', 'two']

    with pytest.warns(DeprecationWarning):
        filtered_legacy = collection.filtered_by(cond)
    assert [el.text for el in filtered_legacy()] == ['one', 'two']

    picked = collection.element_by(cond)
    assert picked().text == 'one'

    config.log_outer_html_on_failure = True
    monkeypatch.setattr(
        'selene.core.query.outer_html', lambda element: f'<li>{element().text}</li>'
    )
    no_match = Condition(
        'never', lambda _e: (_ for _ in ()).throw(AssertionError('no'))
    )
    with pytest.raises(AssertionError, match='Actual webelements collection'):
        collection.element_by(no_match)()


def test_collection_by_their_collected_all_and_all_first():
    config = DummyConfig()
    parent1 = DummyWebElement('p1')
    parent2 = DummyWebElement('p2')
    parent1.children_many[('css selector', '.cell')] = [
        DummyWebElement('A1'),
        DummyWebElement('A2'),
    ]
    parent2.children_many[('css selector', '.cell')] = [
        DummyWebElement('B1'),
        DummyWebElement('B2'),
    ]
    parent1.children[('css selector', '.first')] = DummyWebElement('F1')
    parent2.children[('css selector', '.first')] = DummyWebElement('F2')

    collection = Collection(Locator('rows', lambda: [parent1, parent2]), config)

    cond = Condition(
        'title has p',
        lambda e: (
            None
            if e().text.startswith('p')
            else (_ for _ in ()).throw(AssertionError('bad'))
        ),
    )
    assert [el.text for el in collection.by_their(lambda it: it, cond)()] == [
        'p1',
        'p2',
    ]

    collected = collection.collected(lambda it: it.all('.cell'))
    assert [el.text for el in collected()] == ['A1', 'A2', 'B1', 'B2']

    all_cells = collection.all('.cell')
    assert [el.text for el in all_cells()] == ['A1', 'A2', 'B1', 'B2']

    all_first = collection.all_first('.first')
    assert [el.text for el in all_first()] == ['F1', 'F2']


def test_element_wait_hook_and_overlap_related_behaviors(monkeypatch):
    config = DummyConfig()
    root_we = DummyWebElement('root')
    cover_we = DummyWebElement('cover', with_defaults=False)
    element = Element(Locator('root', lambda: root_we), config)

    monkeypatch.setattr(
        Element,
        '_actual_visible_webelement_and_maybe_its_cover',
        lambda self, center_x_offset=0, center_y_offset=0: (root_we, cover_we),
    )

    with pytest.raises(_SeleneError, match='is overlapped by'):
        _ = element._actual_not_overlapped_webelement

    class CachedPresent:
        @staticmethod
        def matching(_condition):
            return True

    class CachedAbsent:
        @staticmethod
        def matching(_condition):
            return False

    class HookTarget:
        def __init__(self, cached):
            self.cached = cached

    monkeypatch.setattr(
        'selene.core.query.outer_html', lambda _element: '<div>html</div>'
    )

    hook = Element._log_webelement_outer_html_for(HookTarget(CachedPresent()))
    enriched = hook(TimeoutException('boom'))
    assert 'Actual webelement: <div>html</div>' in str(enriched)

    plain = Element._log_webelement_outer_html_for(HookTarget(CachedAbsent()))(
        TimeoutException('boom')
    )
    assert str(plain) == 'Message: boom\n'


def test_element_set_type_click_and_pointer_actions(monkeypatch):
    config = DummyConfig()
    root_we = DummyWebElement('root', with_defaults=False)
    overlap_we = DummyWebElement('overlap', with_defaults=False)
    element = Element(Locator('root', lambda: root_we), config)

    monkeypatch.setattr(
        Element,
        '_actual_visible_webelement_and_maybe_its_cover',
        lambda self, center_x_offset=0, center_y_offset=0: (overlap_we, None),
    )

    config.wait_for_no_overlap_found_by_js = True
    element.set_value('42').type('text').set('alias')

    assert overlap_we.cleared == 2
    assert overlap_we.sent == ['42', 'text', 'alias']

    calls = []

    class FakeActionChains:
        def __init__(self, _driver):
            pass

        def move_to_element_with_offset(self, webelement, xoffset, yoffset):
            calls.append(('move_to_element_with_offset', webelement, xoffset, yoffset))
            return self

        def click(self):
            calls.append(('click',))
            return self

        def perform(self):
            calls.append(('perform',))
            return self

        def double_click(self, webelement):
            calls.append(('double_click', webelement))
            return self

        def context_click(self, webelement):
            calls.append(('context_click', webelement))
            return self

        def move_to_element(self, webelement):
            calls.append(('move_to_element', webelement))
            return self

    monkeypatch.setattr('selene.core.entity.ActionChains', FakeActionChains)

    element.click(xoffset=5, yoffset=3).double_click().context_click().hover()
    assert ('move_to_element_with_offset', overlap_we, 5, 3) in calls
    assert ('double_click', overlap_we) in calls
    assert ('context_click', overlap_we) in calls
    assert ('move_to_element', overlap_we) in calls

    config.wait_for_no_overlap_found_by_js = False
    element.click()
    assert 'clicked' in root_we.sent


def test_element_click_set_and_type_js_branches(monkeypatch):
    config = DummyConfig()
    root_we = DummyWebElement('root', with_defaults=False)
    element = Element(Locator('root', lambda: root_we), config)
    js_calls = []

    from selene.core import command

    monkeypatch.setattr(
        command.js,
        'set_value',
        lambda value: (lambda _element: js_calls.append(('set', value))),
    )
    monkeypatch.setattr(
        command.js,
        'type',
        lambda text: (lambda _element: js_calls.append(('type', text))),
    )
    monkeypatch.setattr(
        command.js,
        'click',
        lambda xoffset=0, yoffset=0: (
            lambda _element: js_calls.append(('click', xoffset, yoffset))
        ),
    )

    config.set_value_by_js = True
    config.type_by_js = True
    config.click_by_js = True
    element.set_value(7).type('x').click(xoffset=9, yoffset=4)
    assert js_calls == [('set', 7), ('type', 'x'), ('click', 9, 4)]


def test_collection_len_and_selector_branches(monkeypatch):
    config = DummyConfig()
    parent = DummyWebElement('p')
    parent.children[('css selector', '.title')] = DummyWebElement('t')
    collection = Collection(Locator('rows', lambda: [parent]), config)

    monkeypatch.setattr('selene.core.query.size', lambda c: len(c()))
    assert len(collection) == 1

    cond = Condition('always', lambda _e: None)
    assert collection.by_their('.title', cond)[0]().text == 'p'
    assert collection.element_by_its('.title', cond)().text == 'p'

    failing = Condition('never', lambda _e: (_ for _ in ()).throw(AssertionError('x')))
    config.log_outer_html_on_failure = False
    with pytest.raises(AssertionError, match='Cannot find element by condition'):
        collection.element_by(failing)()


def test_element_with_explicit_config_and_actual_visible_webelement_probe():
    config = DummyConfig()
    root_we = DummyWebElement('root', with_defaults=False)
    cover_we = DummyWebElement('cover', with_defaults=False)
    calls = []

    def execute_script(script, webelement, arguments):
        calls.append((script, webelement, arguments))
        return [root_we, cover_we]

    config.driver = types.SimpleNamespace(execute_script=execute_script)

    element = Element(Locator('root', lambda: root_we), config)

    another_config = DummyConfig()
    assert element.with_(config=another_config).config is another_config

    actual, maybe_cover = element._actual_visible_webelement_and_maybe_its_cover(
        7,
        -3,
    )

    assert actual is root_we
    assert maybe_cover is cover_we
    assert calls[0][1] is root_we
    assert calls[0][2] == (7, -3)
    assert 'document.elementFromPoint' in calls[0][0]


def test_collection_with_explicit_config_and_by_element_by_callable_conditions():
    config = DummyConfig()
    items = [
        DummyWebElement('one', with_defaults=False),
        DummyWebElement('two', with_defaults=False),
        DummyWebElement('three', with_defaults=False),
    ]
    collection = Collection(Locator('items', lambda: items), config)

    another_config = DummyConfig()
    assert collection.with_(config=another_config).config is another_config

    def has_o(element):
        if 'o' not in element().text:
            raise AssertionError('no o')

    filtered = collection.by(has_o)
    assert [element.text for element in filtered()] == ['one', 'two']

    picked = collection.element_by(has_o)
    assert picked().text == 'one'


def test_collection_element_by_its_accepts_callable_selector():
    config = DummyConfig()

    parent = DummyWebElement('parent', with_defaults=False)
    parent.children[('css selector', '.title')] = DummyWebElement(
        'title',
        with_defaults=False,
    )

    collection = Collection(Locator('rows', lambda: [parent]), config)

    title_has_text = Condition(
        'title has text',
        lambda element: (
            None
            if element().text == 'title'
            else (_ for _ in ()).throw(AssertionError('wrong title'))
        ),
    )

    found = collection.element_by_its(lambda row: row.element('.title'), title_has_text)

    assert found().text == 'parent'


def test_collection_should_applies_element_condition_as_each_when_raw_collection_fails():
    names = []

    class RecordingWait(DummyWait):
        def for_(self, fn):
            names.append(str(fn))
            result = fn(self.entity)
            names.append(str(fn))
            return result

    class RecordingConfig(DummyConfig):
        def wait(self, entity):
            return RecordingWait(entity)

    config = RecordingConfig()
    items = [
        DummyWebElement('one', with_defaults=False),
        DummyWebElement('two', with_defaults=False),
    ]
    collection = Collection(Locator('items', lambda: items), config)

    has_o = Condition(
        'has o',
        lambda element: (
            None
            if 'o' in element().text
            else (_ for _ in ()).throw(AssertionError('no o'))
        ),
    )

    assert collection.should(has_o) is collection
    assert names == ['has o', ' each has o']


def test_collection_should_reports_each_element_failures_after_fallback():
    config = DummyConfig()
    items = [
        DummyWebElement('one', with_defaults=False),
        DummyWebElement('bad', with_defaults=False),
    ]
    collection = Collection(Locator('items', lambda: items), config)

    has_o = Condition(
        'has o',
        lambda element: (
            None
            if 'o' in element().text
            else (_ for _ in ()).throw(AssertionError('no o'))
        ),
    )

    with pytest.raises(AssertionError) as ex:
        collection.should(has_o)

    assert 'Not matched elements among all with indexes from 0 to 1' in str(ex.value)
    assert 'no o' in str(ex.value)


def test_collection_should_reraises_collection_condition_error_as_is():
    config = DummyConfig()
    collection = Collection(
        Locator('items', lambda: [DummyWebElement('one', with_defaults=False)]),
        config,
    )

    broken_collection_condition = Condition(
        'broken collection condition',
        lambda _collection: (_ for _ in ()).throw(
            AssertionError('actual collection mismatch')
        ),
    )

    with pytest.raises(AssertionError, match='actual collection mismatch'):
        collection.should(broken_collection_condition)
