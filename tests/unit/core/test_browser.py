import types

import pytest

from selene.core import _browser as browser_module


class DummySwitchTo:
    def __init__(self):
        self.windows = []

    def window(self, name):
        self.windows.append(name)


class DummyDriver:
    def __init__(self):
        self.switch_to = DummySwitchTo()
        self.closed = 0
        self.quit_called = 0
        self.scripts = []

    def close(self):
        self.closed += 1

    def quit(self):
        self.quit_called += 1

    def execute_script(self, script, *args):
        self.scripts.append((script, args))
        return 'script-result'


class DummyExecutor:
    def __init__(self):
        self.urls = []

    def get_url(self, url):
        self.urls.append(url)


class DummyConfig:
    def __init__(self):
        self.driver = DummyDriver()
        self._executor = DummyExecutor()
        self.last_screenshot = 'last-shot.png'
        self.last_page_source = 'last-source.html'
        self.with_calls = []

    def with_(self, **kwargs):
        self.with_calls.append(kwargs)
        return self

    def _generate_filename(self, suffix):
        return f'generated{suffix}'


class FakeLocator:
    def __init__(self, description, fn=None):
        self.description = description
        self.fn = fn

    def __call__(self):
        return self.fn() if self.fn else None


class FakeElement:
    def __init__(self, locator, config):
        self.locator = locator
        self.config = config


class FakeCollection:
    def __init__(self, locator, config):
        self.locator = locator
        self.config = config


def test_with_returns_browser_with_passed_config_or_kwargs_config():
    config = DummyConfig()
    browser = browser_module.Browser(config)

    explicit = browser.with_(DummyConfig())
    implicit = browser.with_(timeout=0.1)

    assert isinstance(explicit, browser_module.Browser)
    assert isinstance(implicit, browser_module.Browser)
    assert config.with_calls == [{'timeout': 0.1}]


def test_driver_and_raw_shortcuts():
    config = DummyConfig()
    browser = browser_module.Browser(config)

    assert browser.driver is config.driver
    assert browser.__raw__ is config.driver
    assert str(browser) == 'browser'


def test_element_and_all_build_entities_from_locator_and_by(monkeypatch):
    config = DummyConfig()
    browser = browser_module.Browser(config)
    raw_locator = FakeLocator('raw')

    monkeypatch.setattr(browser_module, 'Locator', FakeLocator)
    monkeypatch.setattr(browser_module, 'Element', FakeElement)
    monkeypatch.setattr(browser_module, 'Collection', FakeCollection)

    from_locator = browser.element(raw_locator)
    by_css = browser.element('#name')
    many_css = browser.all('#name')

    assert from_locator.locator is raw_locator
    assert by_css.locator.description == "browser.element(('css selector', '#name'))"
    assert many_css.locator.description == "browser.all(('css selector', '#name'))"


def test_open_and_switch_tab_commands(monkeypatch):
    config = DummyConfig()
    browser = browser_module.Browser(config)

    from selene.core import query

    monkeypatch.setattr(query, 'next_tab', lambda _browser: 'tab-next')
    monkeypatch.setattr(query, 'previous_tab', lambda _browser: 'tab-prev')
    monkeypatch.setattr(query, 'tab', lambda index: (lambda _browser: f'tab-{index}'))

    assert browser.open('/path') is browser
    assert config._executor.urls == ['/path']

    browser.switch_to_next_tab().switch_to_previous_tab()
    browser.switch_to_tab(2).switch_to_tab('named-tab')

    assert config.driver.switch_to.windows == [
        'tab-next',
        'tab-prev',
        'tab-2',
        'named-tab',
    ]
    assert browser.switch_to is config.driver.switch_to


def test_quit_close_and_close_current_tab():
    config = DummyConfig()
    browser = browser_module.Browser(config)

    browser.quit()
    assert config.driver.quit_called == 1

    assert browser.close() is browser
    assert config.driver.closed == 1

    with pytest.warns(DeprecationWarning):
        assert browser.close_current_tab() is browser
    assert config.driver.closed == 2


def test_execute_script_and_last_properties_are_deprecated():
    config = DummyConfig()
    browser = browser_module.Browser(config)

    with pytest.warns(PendingDeprecationWarning):
        assert browser.execute_script('return 1', 2) == 'script-result'

    with pytest.warns(DeprecationWarning):
        assert browser.last_screenshot == 'last-shot.png'

    with pytest.warns(DeprecationWarning):
        assert browser.last_page_source == 'last-source.html'


def test_save_screenshot_and_page_source_deprecations(monkeypatch):
    config = DummyConfig()
    browser = browser_module.Browser(config)

    monkeypatch.setattr(browser, 'get', lambda _query: 'saved-shot.png')

    with pytest.warns(DeprecationWarning):
        assert browser.save_screenshot() == 'saved-shot.png'

    helper_calls = []

    class FakeWebHelper:
        def __init__(self, _driver):
            pass

        def save_page_source(self, file):
            helper_calls.append(file)
            return f'saved:{file}'

    monkeypatch.setattr(browser_module, 'WebHelper', FakeWebHelper)

    with pytest.warns(DeprecationWarning):
        auto_name = browser.save_page_source()
    with pytest.warns(DeprecationWarning):
        custom_name = browser.save_page_source('manual.html')

    assert auto_name == 'saved:generated.html'
    assert custom_name == 'saved:manual.html'
    assert helper_calls == ['generated.html', 'manual.html']
    assert config.last_page_source == 'saved:manual.html'


def test_clear_storage_shortcuts_call_perform(monkeypatch):
    config = DummyConfig()
    browser = browser_module.Browser(config)
    performed = []

    monkeypatch.setattr(browser, 'perform', lambda cmd: performed.append(cmd))

    with pytest.warns(DeprecationWarning):
        assert browser.clear_local_storage() is browser
    with pytest.warns(DeprecationWarning):
        assert browser.clear_session_storage() is browser

    assert len(performed) == 2
