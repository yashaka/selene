import types

from selene.core import query


class DummyWebElement:
    def __init__(self):
        self.size = {'width': 10, 'height': 5}
        self.tag_name = 'div'
        self.text = 'hello'
        self.location_once_scrolled_into_view = {'x': 1, 'y': 2}
        self.location = {'x': 3, 'y': 4}
        self.rect = {'x': 0, 'y': 0, 'width': 10, 'height': 5}
        self.screenshot_as_base64 = 'base64'
        self.screenshot_as_png = b'png'
        self.id = 'internal-id'

    def get_attribute(self, name):
        return f'attr:{name}'

    def screenshot(self, filename):
        return filename == 'ok.png'

    def value_of_css_property(self, name):
        return f'css:{name}'

    def get_property(self, name):
        return f'js:{name}'


class DummyElementEntity:
    def __init__(self, locator=None, config=None):
        self._locator = locator
        self.config = config
        self._webelement = DummyWebElement()

    def __call__(self):
        if self._locator:
            return self._locator()
        return self._webelement

    def locate(self):
        return 'frame-node'

    def perform(self, command):
        return command(self)

    def __str__(self):
        return 'dummy-container'


class DummyCollectionEntity:
    def __init__(self, locator=None, config=None):
        self._locator = locator
        self.config = config

    def __call__(self):
        if self._locator:
            return self._locator()
        return [1, 2, 3]


class DummyDriver:
    def __init__(self):
        self.frame_calls = []
        self.parent_calls = 0
        self.find_element_calls = []
        self.find_elements_calls = []
        self.window_handles = ['tab-1', 'tab-2', 'tab-3']
        self.current_window_handle = 'tab-2'
        self.current_url = 'https://example.test'
        self.title = 'Example'
        self.page_source = '<html></html>'
        self.switch_to = types.SimpleNamespace(
            frame=lambda node: self.frame_calls.append(node),
            parent_frame=lambda: setattr(self, 'parent_calls', self.parent_calls + 1),
        )

    def find_element(self, *by):
        self.find_element_calls.append(by)
        return ('one', by)

    def find_elements(self, *by):
        self.find_elements_calls.append(by)
        return [('many', by)]

    def get_window_size(self):
        return {'width': 100, 'height': 50}


class DummyConfig:
    def __init__(self, driver):
        self.driver = driver
        self._wait_decorator = lambda _wait: (lambda fn: fn)

    def with_(self, **kwargs):
        clone = DummyConfig(self.driver)
        clone._wait_decorator = kwargs.get('_wait_decorator', self._wait_decorator)
        return clone


class DummyBrowser:
    def __init__(self, driver):
        self.driver = driver
        self.config = types.SimpleNamespace(
            _save_screenshot_strategy=lambda _config, path: f'shot:{path}',
            _save_page_source_strategy=lambda _config, path: f'source:{path}',
        )


def test_query_builders_for_element_properties(monkeypatch):
    monkeypatch.setattr(query, 'Element', DummyElementEntity)

    entity = DummyElementEntity()

    assert query.attribute('role')(entity) == 'attr:role'
    assert query.screenshot('ok.png')(entity) is True
    assert query.css_property('display')(entity) == 'css:display'
    assert query.js_property('checked')(entity) == 'js:checked'


def test_size_query_for_element_collection_and_browser(monkeypatch):
    monkeypatch.setattr(query, 'Element', DummyElementEntity)
    monkeypatch.setattr(query, 'Collection', DummyCollectionEntity)
    monkeypatch.setattr(query, 'Browser', DummyBrowser)

    driver = DummyDriver()

    assert query.size(DummyElementEntity()) == {'width': 10, 'height': 5}
    assert query.size(DummyCollectionEntity()) == 3
    assert query.size(DummyBrowser(driver)) == {'width': 100, 'height': 50}


def test_frame_context_enter_exit_and_decorator(monkeypatch):
    monkeypatch.setattr(query, 'functools', __import__('functools'), raising=False)

    support_stub = types.SimpleNamespace(
        _wait=types.SimpleNamespace(
            with_=lambda context: (lambda _wait: (lambda fn: fn))
        )
    )
    monkeypatch.setattr(query, 'support', support_stub, raising=False)

    driver = DummyDriver()
    container = DummyElementEntity(config=DummyConfig(driver))
    context = query._frame_context(container)

    context.__enter__()
    assert driver.frame_calls == ['frame-node']

    context.__exit__(None, None, None)
    assert driver.parent_calls == 1

    called = {'value': False}

    @context.decorator
    def step():
        called['value'] = True
        return 42

    assert step() == 42
    assert called['value'] is True


def test_frame_context_element_and_all_build_lazy_entities(monkeypatch):
    monkeypatch.setattr(query, 'Element', DummyElementEntity)
    monkeypatch.setattr(query, 'Collection', DummyCollectionEntity)
    monkeypatch.setattr(query, 'functools', __import__('functools'), raising=False)
    support_stub = types.SimpleNamespace(
        _wait=types.SimpleNamespace(
            with_=lambda context: (lambda _wait: (lambda fn: fn))
        )
    )
    monkeypatch.setattr(query, 'support', support_stub, raising=False)

    driver = DummyDriver()
    container = DummyElementEntity(config=DummyConfig(driver))
    context = query._frame_context(container)

    element = context._element('#a')
    collection = context._all('#a')

    assert element() == ('one', ('css selector', '#a'))
    assert collection() == [('many', ('css selector', '#a'))]

    # also force evaluation of composed wait decorator internals
    decorated = element.config._wait_decorator(object())(lambda fn_arg: fn_arg + '-ok')
    assert decorated('x') == 'x-ok'


def test_tab_related_queries(monkeypatch):
    monkeypatch.setattr(query, 'Browser', DummyBrowser)

    driver = DummyDriver()
    browser = DummyBrowser(driver)

    assert query.tab(1)(browser) == 'tab-2'
    assert query.next_tab(browser) == 'tab-3'
    assert query.previous_tab(browser) == 'tab-1'

    driver.current_window_handle = 'tab-3'
    assert query.next_tab(browser) == 'tab-1'

    driver.current_window_handle = 'tab-1'
    assert query.previous_tab(browser) == 'tab-3'


def test_saved_screenshot_and_page_source_queries_and_browser_shortcut(monkeypatch):
    monkeypatch.setattr(query, 'Browser', DummyBrowser)

    driver = DummyDriver()
    browser = DummyBrowser(driver)

    assert query.screenshot_saved('a.png')(browser) == 'shot:a.png'
    assert query.page_source_saved('a.html')(browser) == 'source:a.html'

    # deprecated but still supported shortcut usage
    assert query.screenshot_saved(browser).startswith('shot:')
    assert query.page_source_saved(browser).startswith('source:')
