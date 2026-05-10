import types

from selene.core import _actions as actions_module


class DummyDevice:
    def __init__(self, actions):
        self._actions = actions

    def encode(self):
        return {'actions': self._actions}


class FakeActionChains:
    last = None

    def __init__(self, _driver, _duration, _devices):
        self.calls = []
        self.performed = 0
        self.w3c_actions = types.SimpleNamespace(
            devices=[
                DummyDevice([{'type': 'pointerMove'}]),
                DummyDevice([]),
                DummyDevice([{'type': 'pause'}]),
            ]
        )
        FakeActionChains.last = self

    def _remember(self, name, *args):
        self.calls.append((name, *args))
        return self

    def perform(self):
        self.performed += 1
        return self

    def click(self, element=None):
        return self._remember('click', element)

    def click_and_hold(self, element=None):
        return self._remember('click_and_hold', element)

    def context_click(self, element=None):
        return self._remember('context_click', element)

    def double_click(self, element=None):
        return self._remember('double_click', element)

    def drag_and_drop(self, source, target):
        return self._remember('drag_and_drop', source, target)

    def drag_and_drop_by_offset(self, source, x, y):
        return self._remember('drag_and_drop_by_offset', source, x, y)

    def key_down(self, value, element=None):
        return self._remember('key_down', value, element)

    def key_up(self, value, element=None):
        return self._remember('key_up', value, element)

    def move_by_offset(self, x, y):
        return self._remember('move_by_offset', x, y)

    def move_to_element(self, element):
        return self._remember('move_to_element', element)

    def move_to_element_with_offset(self, element, x, y):
        return self._remember('move_to_element_with_offset', element, x, y)

    def pause(self, seconds):
        return self._remember('pause', seconds)

    def release(self, element=None):
        return self._remember('release', element)

    def send_keys(self, *keys):
        return self._remember('send_keys', keys)

    def scroll_to_element(self, element):
        return self._remember('scroll_to_element', element)

    def scroll_by_amount(self, x, y):
        return self._remember('scroll_by_amount', x, y)

    def scroll_from_origin(self, origin, x, y):
        return self._remember('scroll_from_origin', origin, x, y)


class DummyWait:
    def __init__(self, entity):
        self.entity = entity

    def for_(self, command):
        return command(self.entity)


class DummyConfig:
    def __init__(self):
        self.driver = object()

    def wait(self, entity):
        return DummyWait(entity)


def test_ensure_located_for_element_and_passthrough(monkeypatch):
    class FakeElement:
        def __init__(self):
            self.located = object()

        def locate(self):
            return self.located

        def get(self, query):
            return query(self)

    monkeypatch.setattr(actions_module, 'Element', FakeElement)

    element = FakeElement()
    raw = object()

    assert actions_module._ensure_located(element) is element.located
    assert actions_module._ensure_located(raw) is raw
    assert actions_module._ensure_located(None) is None


def test_perform_executes_chain_and_encodes_actions(monkeypatch):
    monkeypatch.setattr(actions_module, 'ActionChains', FakeActionChains)
    actions = actions_module._Actions(DummyConfig())

    actions.perform()

    assert FakeActionChains.last.performed == 1


def test_actions_methods_and_aliases_call_underlying_chain(monkeypatch):
    monkeypatch.setattr(actions_module, 'ActionChains', FakeActionChains)
    actions = actions_module._Actions(DummyConfig())

    source = object()
    target = object()

    actions.click(target).click_and_hold(target).context_click(target).double_click(target)
    actions.drag_and_drop(source, target).drag_and_drop_by_offset(source, 1, 2)
    actions.key_down('CTRL', target).key_up('CTRL', target).move_by_offset(3, 4)
    actions.move_to_element(target).move_to(target).move_to_element_with_offset(target, 5, 6)
    actions.move_with_offset_to(target, 7, 8).pause(0.1).release(target)
    actions.send_keys('a', 'b').send_keys_to_element(target, 'x').send_keys_to(
        target, 'y'
    )
    actions.scroll_to_element(target).scroll_to(target).scroll_by_amount(9, 10).scroll_by(
        11, 12
    )
    actions.scroll_from_origin('origin', 13, 14)

    calls = FakeActionChains.last.calls
    names = [call[0] for call in calls]

    assert 'drag_and_drop' in names
    assert 'drag_and_drop_by_offset' in names
    assert names.count('move_to_element') >= 2  # direct call + alias
    assert names.count('move_to_element_with_offset') >= 2  # direct + alias
    assert names.count('send_keys') >= 3  # direct + two send_keys_to* calls
    assert names.count('scroll_to_element') >= 2  # direct + alias
    assert names.count('scroll_by_amount') >= 2  # direct + alias
