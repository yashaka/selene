import importlib

import pytest


def test_api_modules_import_and_expose_expected_symbols():
    api = importlib.import_module('selene.api')
    base = importlib.import_module('selene.api.base')
    shared = importlib.import_module('selene.api.shared')

    assert hasattr(api, 'Browser')
    assert hasattr(api, 'Config')
    assert hasattr(api, 'browser')
    assert hasattr(api, 's')
    assert hasattr(base, 'Browser')
    assert hasattr(base, 'Config')
    assert hasattr(shared, 'browser')
    assert hasattr(shared, 'config')
    assert hasattr(shared, 'jquery_style')


def test_support_shared_deprecated_classes_warn_on_import():
    with pytest.warns(DeprecationWarning, match='SharedBrowser is deprecated'):
        module_browser = importlib.import_module('selene.support.shared.browser')
        importlib.reload(module_browser)

    with pytest.warns(DeprecationWarning, match='SharedConfig is deprecated'):
        module_config = importlib.import_module('selene.support.shared.config')
        importlib.reload(module_config)
