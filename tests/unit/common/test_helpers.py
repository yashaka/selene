import pytest
from selenium.webdriver.common.by import By

from selene.common import helpers


class Dummy:
    def __init__(self):
        self.visible = 1
        self.empty = None
        self._private = 'x'


def test_as_dict_with_and_without_skip_empty():
    obj = Dummy()
    assert helpers.as_dict(obj) == {'visible': 1}
    assert helpers.as_dict(obj, skip_empty=False) == {'visible': 1, 'empty': None}
    assert helpers.as_dict(None) == {}


def test_to_by_for_tuple_css_xpath_and_invalid_type():
    assert helpers.to_by((By.ID, 'name')) == (By.ID, 'name')
    assert helpers.to_by('.item') == (By.CSS_SELECTOR, '.item')
    assert helpers.to_by('/html/body') == (By.XPATH, '/html/body')
    assert helpers.to_by('./child') == (By.XPATH, './child')
    assert helpers.to_by('..') == (By.XPATH, '..')
    assert helpers.to_by('(//div)[1]') == (By.XPATH, '(//div)[1]')

    with pytest.raises(TypeError, match='selector_or_by should be str'):
        helpers.to_by(123)  # type: ignore[arg-type]


def test_flatten_dissoc_on_error_return_false_and_absolute_url():
    assert helpers.flatten([1, [2, 3], 'ab']) == (1, 2, 3, 'ab')
    assert helpers.dissoc({'a': 1, 'b': 2}, 'a') == {'b': 2}
    assert helpers.on_error_return_false(lambda: 3 > 1) is True
    assert helpers.on_error_return_false(lambda: (_ for _ in ()).throw(RuntimeError())) is False

    assert helpers.is_absolute_url('HTTP://site') is True
    assert helpers.is_absolute_url('https://site') is True
    assert helpers.is_absolute_url('file:///tmp') is True
    assert helpers.is_absolute_url('about:blank') is True
    assert helpers.is_absolute_url('data:text/plain,ok') is True
    assert helpers.is_absolute_url('/relative') is False
