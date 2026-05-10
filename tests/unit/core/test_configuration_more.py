from pathlib import Path

import pytest

from selene.core import configuration as configuration_module
from selene.core.exceptions import TimeoutException


def test_with_adds_driver_reset_when_driver_like_option_overridden(monkeypatch):
    config = configuration_module.Config()
    config._override_driver_with_all_driver_like_options = True
    captured = {}

    def fake_replace(instance, **options):
        captured['instance'] = instance
        captured['options'] = options
        return 'replaced'

    monkeypatch.setattr(configuration_module.persistent, 'replace', fake_replace)

    result = config.with_(driver_name='firefox')

    assert result == 'replaced'
    assert captured['instance'] is config
    assert captured['options']['driver'] is ...
    assert captured['options']['driver_name'] == 'firefox'


def test_with_does_not_add_driver_for_non_driver_options(monkeypatch):
    config = configuration_module.Config()
    captured = {}
    monkeypatch.setattr(
        configuration_module.persistent,
        'replace',
        lambda instance, **options: captured.setdefault('options', options) or instance,
    )

    config.with_(timeout=1.5)

    assert captured['options'] == {'timeout': 1.5}


def test_browser_name_and_hold_browser_open_are_deprecated_aliases():
    config = configuration_module.Config()
    config.driver_name = 'chrome'

    with pytest.warns(DeprecationWarning):
        assert config.hold_browser_open is False
    with pytest.warns(DeprecationWarning):
        config.hold_browser_open = True
    assert config.hold_driver_at_exit is True

    assert config.browser_name == 'chrome'
    config.browser_name = 'firefox'
    assert config.driver_name == 'firefox'


def test_executor_delegates_calls_to_config_strategies():
    config = configuration_module.Config()
    setattr(
        config,
        configuration_module.persistent.Field.box_mask('driver'),
        configuration_module.persistent.Box('alive-driver'),
    )
    calls = []
    config._driver_get_url_strategy = lambda _config: lambda url: calls.append(
        ('get_url', url)
    )
    config._save_screenshot_strategy = lambda _config, path: ('screenshot', path)
    config._save_page_source_strategy = lambda _config, path: ('page_source', path)
    config._is_driver_set_strategy = lambda value: value == 'alive-driver'
    config._is_driver_alive_strategy = lambda value: value == 'alive-driver'
    config._teardown_driver_strategy = lambda _config: lambda _driver: None
    config._schedule_driver_teardown_strategy = (
        lambda _config, get_driver: calls.append(('schedule', get_driver()))
    )
    config.build_driver_strategy = lambda _config: 'built-driver'

    executor = configuration_module._DriverStrategiesExecutor(config)

    assert executor.driver_instance == 'alive-driver'
    assert executor.is_driver_managed is True
    assert executor.is_driver_set is True
    assert executor.is_driver_alive is True
    assert executor.build_driver() == 'built-driver'
    assert callable(executor.teardown)

    executor.schedule_teardown(lambda: 'to-close')
    executor.get_url('/path')
    assert executor.save_screenshot('a.png') == ('screenshot', 'a.png')
    assert executor.save_page_source('a.html') == ('page_source', 'a.html')
    assert calls == [('schedule', 'to-close'), ('get_url', '/path')]


def test_format_uri_and_generate_filename(tmp_path):
    config = configuration_module.Config()
    config.reports_folder = str(tmp_path / 'reports')
    config._counter = iter([7])

    generated = config._generate_filename(prefix='shot-', suffix='.png')

    assert generated.endswith('shot-7.png')
    assert Path(generated).parent.exists()
    assert config._format_path_as_uri('/tmp/a.txt') == 'file:///tmp/a.txt'


def test_inject_screenshot_and_page_source_hooks():
    config = configuration_module.Config()
    config.save_screenshot_on_failure = True
    config.save_page_source_on_failure = True
    config.last_screenshot = 'report.png'
    config._save_screenshot_strategy = lambda _config: '/tmp/report.png'
    config._save_page_source_strategy = lambda _config, filename: f'/tmp/{filename}'

    hook = config._inject_screenshot_and_page_source_pre_hooks(lambda error: error)
    error = hook(TimeoutException('boom'))

    assert 'Screenshot: file:///tmp/report.png' in error.msg
    assert 'PageSource: file:///tmp/report.html' in error.msg


def test_wait_builds_wait_object_with_config_timeout():
    config = configuration_module.Config(timeout=3.5)
    wait = config.wait('entity')

    assert wait.entity == 'entity'
    assert wait._timeout == 3.5


def test_executor_is_driver_managed_false_for_callable_driver_storage():
    config = configuration_module.Config()
    setattr(
        config,
        configuration_module.persistent.Field.box_mask('driver'),
        configuration_module.persistent.Box(lambda: 'driver-from-callable'),
    )

    executor = configuration_module._DriverStrategiesExecutor(config)

    assert executor.driver_instance() == 'driver-from-callable'
    assert executor.is_driver_managed is False


def test_managed_driver_descriptor_builds_and_calls_callable_driver_and_rebuilds_not_alive():
    class BuiltDriver:
        def __init__(self, name='built'):
            self.name = name

    config = configuration_module.Config()
    built = []
    scheduled = []
    alive_flag = {'alive': False}

    config.build_driver_strategy = (
        lambda _config: built.append(BuiltDriver()) or built[-1]
    )
    config._schedule_driver_teardown_strategy = (
        lambda _config, get_driver: scheduled.append(get_driver())
    )
    config._is_driver_alive_strategy = lambda _driver: alive_flag['alive']

    # first access builds and schedules teardown
    first = config.driver
    assert isinstance(first, BuiltDriver)
    assert len(built) == 1
    assert len(scheduled) == 1

    # callable value should be invoked
    callable_driver = BuiltDriver('callable')
    config.driver = lambda: callable_driver
    assert config.driver is callable_driver

    # when dead and rebuild_not_alive_driver=True, should rebuild
    config.rebuild_not_alive_driver = True
    config.driver = BuiltDriver('dead')
    rebuilt = config.driver
    assert isinstance(rebuilt, BuiltDriver)
    assert rebuilt.name == 'built'
    assert len(built) >= 2


def test_managed_driver_descriptor_rejects_custom_descriptor_on_init():
    descriptor = configuration_module._ManagedDriverDescriptor(default=None)

    class DummyDescriptor:
        def __get__(self, instance, owner):
            return None

        def __set__(self, instance, value):
            return None

    class Holder:
        pass

    descriptor.__set_name__(Holder, 'driver')
    holder = Holder()
    holder._schedule_driver_teardown_strategy = lambda *_args: None

    with pytest.raises(TypeError, match='Providing custom descriptor objects on init'):
        descriptor.__set__(holder, DummyDescriptor())


def test_get_url_strategy_handles_reset_window_and_base_url_concat():
    class Driver:
        def __init__(self):
            self.got = []
            self.size = {'width': 900, 'height': 700}
            self.set_size_calls = []

        def get_window_size(self):
            return dict(self.size)

        def set_window_size(self, width, height):
            self.set_size_calls.append((width, height))

        def get(self, url):
            self.got.append(url)

    driver = Driver()
    config = configuration_module.Config()
    config.base_url = 'https://example.test'
    config.window_width = 1200
    config.window_height = None
    config._get_base_url_on_open_with_no_args = True
    config._reset_not_alive_driver_on_get_url = True
    config.driver = driver
    config._is_driver_set_strategy = lambda value: value is not None
    config._is_driver_alive_strategy = lambda _driver: False
    config._is_driver_set_strategy = lambda _value: True
    config.build_driver_strategy = lambda _config: driver

    get = (
        configuration_module._maybe_reset_driver_then_tune_window_and_get_with_base_url(
            config
        )
    )

    # no args -> opens base_url
    get()
    assert driver.got[-1] == 'https://example.test'
    assert driver.set_size_calls[-1] == (1200, 700)

    # relative url should be concatenated
    get('/path')
    assert driver.got[-1] == 'https://example.test/path'

    # absolute url should not be concatenated
    get('https://other.test/page')
    assert driver.got[-1] == 'https://other.test/page'
