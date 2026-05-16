from selene.core.locator import Locator


def test_locator_call_returns_located_value():
    calls = {'count': 0}

    def locate():
        calls['count'] += 1
        return {'id': 10}

    locator = Locator('user card', locate)

    assert locator() == {'id': 10}
    assert locator() == {'id': 10}
    assert calls['count'] == 2


def test_locator_str_returns_description():
    locator = Locator('submit button', lambda: object())

    assert str(locator) == 'submit button'
