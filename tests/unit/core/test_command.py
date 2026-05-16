import types
from typing import cast

import pytest

from selene.core import command
from selene.core.entity import Element
from selene.core.exceptions import _SeleneError


class DummyTempInput:
    def __init__(self):
        self.sent = []

    def send_keys(self, path):
        self.sent.append(path)


class DummyDriver:
    def __init__(self):
        self.scripts = []
        self.switch_to = types.SimpleNamespace()
        self.temp_input = DummyTempInput()

    def execute_script(self, script, *args):
        self.scripts.append((script, args))
        if 'return input' in script:
            return self.temp_input
        return None


class DummyConfig:
    def __init__(self, driver):
        self.driver = driver
        self.saved_screenshots = []
        self.saved_pages = []

    def _save_screenshot_strategy(self, _config, path):
        self.saved_screenshots.append(path)
        return path

    def _save_page_source_strategy(self, _config, path):
        self.saved_pages.append(path)
        return path


class DummyWebElement:
    def __init__(self, location=None):
        self.location = location or {'x': 0, 'y': 0}


class DummyElement:
    def __init__(self, driver=None, location=None):
        self.driver = driver or DummyDriver()
        self.config = DummyConfig(self.driver)
        self._located = DummyWebElement(location=location)
        self.executed = []

    def locate(self):
        return self._located

    def execute_script(self, script, *args):
        self.executed.append((script, args))
        return None

    def __str__(self):
        return 'dummy-element'


class DummyCollection:
    def __init__(self, items):
        self._items = items

    def __iter__(self):
        return iter(self._items)


class DummyBrowser:
    def __init__(self, driver=None):
        self.driver = driver or DummyDriver()
        self.config = DummyConfig(self.driver)


class FakeActionChains:
    last = None

    def __init__(self, driver):
        self.driver = driver
        self.calls = []
        self.w3c_actions = types.SimpleNamespace(
            pointer_action=types.SimpleNamespace(
                move_to=lambda _el: self,
                pointer_down=lambda: self,
                pause=lambda _d: self,
                release=lambda: self,
            )
        )
        FakeActionChains.last = self

    def key_down(self, key):
        self.calls.append(('key_down', key))
        return self

    def send_keys_to_element(self, element, text):
        self.calls.append(('send_keys_to_element', element, text))
        return self

    def send_keys(self, text):
        self.calls.append(('send_keys', text))
        return self

    def key_up(self, key):
        self.calls.append(('key_up', key))
        return self

    def drag_and_drop(self, source, target):
        self.calls.append(('drag_and_drop', source, target))
        return self

    def drag_and_drop_by_offset(self, source, x, y):
        self.calls.append(('drag_and_drop_by_offset', source, x, y))
        return self

    def perform(self):
        self.calls.append(('perform',))
        return self


class FakeActionBuilder:
    def __init__(self, driver, mouse):
        self.driver = driver
        self.mouse = mouse

        class PointerAction:
            def move_to(self, _el):
                return self

            def pointer_down(self):
                return self

            def pause(self, _d):
                return self

            def release(self):
                return self

        self.pointer_action = PointerAction()


class FakePointerInput:
    def __init__(self, kind, name):
        self.kind = kind
        self.name = name


def test_save_artifact_commands_and_shortcut_style(monkeypatch):
    monkeypatch.setattr(command, 'Browser', DummyBrowser)

    browser = DummyBrowser()

    command.save_screenshot('a.png')(browser)
    command.save_page_source('a.html')(browser)
    assert browser.config.saved_screenshots == ['a.png']
    assert browser.config.saved_pages == ['a.html']

    # shortcut style: command.save_screenshot(browser)
    command.save_screenshot(browser)
    command.save_page_source(browser)
    assert browser.config.saved_screenshots[-1] is browser
    assert browser.config.saved_pages[-1] is browser


def test_select_all_for_element_and_browser(monkeypatch):
    monkeypatch.setattr(command, 'ActionChains', FakeActionChains)
    monkeypatch.setattr(command, 'Element', DummyElement)

    element = DummyElement()
    command.select_all(element)
    assert any(c[0] == 'send_keys_to_element' for c in FakeActionChains.last.calls)

    browser = DummyBrowser()
    command.select_all(browser)
    assert any(c[0] == 'send_keys' for c in FakeActionChains.last.calls)


def test_long_press_default_and_shortcut_style(monkeypatch):
    monkeypatch.setattr(command, 'ActionChains', FakeActionChains)
    monkeypatch.setattr(command, 'ActionBuilder', FakeActionBuilder)
    monkeypatch.setattr(command, 'PointerInput', FakePointerInput)
    monkeypatch.setattr(
        command, 'interaction', types.SimpleNamespace(POINTER_TOUCH='touch')
    )
    monkeypatch.setattr(command, 'Element', DummyElement)

    element = DummyElement()
    command._long_press(0.2)(element)
    assert ('perform',) in FakeActionChains.last.calls

    # shortcut style command._long_press(element)
    command._long_press(element)


def test_drag_and_drop_commands(monkeypatch):
    monkeypatch.setattr(command, 'ActionChains', FakeActionChains)

    source = DummyElement(location={'x': 1, 'y': 1})
    target = DummyElement()

    command.drag_and_drop_to(target)(source)
    assert any(c[0] == 'drag_and_drop' for c in FakeActionChains.last.calls)

    command.drag_and_drop_by_offset(10, 20)(source)
    assert any(c[0] == 'drag_and_drop_by_offset' for c in FakeActionChains.last.calls)


def test_drag_and_drop_to_can_assert_location_changed(monkeypatch):
    monkeypatch.setattr(command, 'ActionChains', FakeActionChains)

    source = DummyElement(location={'x': 1, 'y': 1})
    target = DummyElement()

    raised = False
    try:
        command.drag_and_drop_to(target, _assert_location_changed=True)(source)
    except Exception as e:
        raised = 'not dragged' in str(e)

    assert raised is True


def test_js_set_value_type_scroll_click_and_storage_clear():
    element = DummyElement()
    browser = DummyBrowser(driver=element.driver)

    command.js.set_value('abc')(element)
    command.js.type('x')(element)
    command.js.scroll_into_view(element)

    command.js.click(element)
    click_default = command.js.click()
    click_default(element)
    click_with_offsets = command.js.click(xoffset=3, yoffset=4)
    click_with_offsets(element)

    command.js.clear_local_storage(browser)
    command.js.clear_session_storage(browser)

    assert len(element.executed) >= 4
    assert any('scrollIntoView' in script for script, _ in element.executed)
    assert any(
        'window.localStorage.clear()' in script for script, _ in browser.driver.scripts
    )
    assert any(
        'window.sessionStorage.clear()' in script
        for script, _ in browser.driver.scripts
    )


def test_js_remove_and_set_style_commands_for_element_and_collection():
    one = DummyElement()
    two = DummyElement()
    collection = DummyCollection([one, two])

    command.js.remove(one)
    command.js.remove(collection)

    command.js.set_style_property('color', 'red')(one)
    command.js.set_style_property('color', 'blue')(collection)

    command.js.set_style_display_to_none(one)
    command.js.set_style_display_to_none(collection)
    command.js.set_style_display_to_block(one)
    command.js.set_style_display_to_block(collection)
    command.js.set_style_visibility_to_hidden(one)
    command.js.set_style_visibility_to_hidden(collection)
    command.js.set_style_visibility_to_visible(one)
    command.js.set_style_visibility_to_visible(collection)

    assert any('element.remove()' in script for script, _ in one.executed)
    assert any('element.style.color="red"' in script for script, _ in one.executed)


def test_js_drag_and_drop_to_executes_script_with_source_and_target():
    driver = DummyDriver()
    source = DummyElement(driver=driver)
    target = DummyElement(driver=driver)

    command.js.drag_and_drop_to(target)(source)

    assert driver.scripts
    assert source.locate() in driver.scripts[-1][1]
    assert target.locate() in driver.scripts[-1][1]


def test_js_drop_file_uses_temp_input_and_wait(monkeypatch):
    driver = DummyDriver()
    source = DummyElement(driver=driver)

    class FakeWait:
        def __init__(self, _driver, _timeout):
            self.called = False

        def until(self, condition):
            self.called = True
            condition
            return True

    monkeypatch.setattr(command, 'WebDriverWait', FakeWait)
    monkeypatch.setattr(
        command,
        'expected_conditions',
        types.SimpleNamespace(staleness_of=lambda element: ('stale', element)),
    )

    command.js.drop_file('/tmp/file.txt')(source)

    assert driver.temp_input.sent == ['/tmp/file.txt']


def test_js_drag_and_drop_to_can_assert_location_changed():
    driver = DummyDriver()
    source = cast(
        Element,
        DummyElement(driver=driver, location={'x': 1, 'y': 1}),
    )
    target = cast(Element, DummyElement(driver=driver))

    with pytest.raises(
        _SeleneError,
        match='Element was not dragged to the new place',
    ):
        command.js.drag_and_drop_to(
            target,
            _assert_location_changed=True,
        )(source)
