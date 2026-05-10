import pytest

from selene.common.none_object import _NoneObject


def test_none_object_is_falsy_and_has_descriptive_attribute_error():
    missing = _NoneObject('driver')

    assert bool(missing) is False
    with pytest.raises(AttributeError, match="for «'driver'» has no attribute 'foo'"):
        _ = missing.foo
