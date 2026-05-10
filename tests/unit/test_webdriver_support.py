import pytest

from selene.support.webdriver import WebHelper


class DummyDriver:
    def __init__(self):
        self.title = 'Selene'
        self.page_source = '<html>ok</html>'
        self.screenshot_ok = True
        self.screenshot_calls = []

    def get_screenshot_as_file(self, file):
        self.screenshot_calls.append(file)
        return self.screenshot_ok


def test_is_browser_still_alive_true_and_false():
    alive_driver = DummyDriver()
    helper = WebHelper(alive_driver)
    assert helper.is_browser_still_alive() is True

    dead_driver = DummyDriver()

    class Broken:
        @property
        def title(self):
            raise RuntimeError('driver dead')

    dead_driver.__class__ = type(
        'DeadDriver',
        (DummyDriver,),
        {'title': Broken.title},
    )
    helper = WebHelper(dead_driver)
    assert helper.is_browser_still_alive() is False


def test_save_page_source_success_and_warning_for_extension(tmp_path):
    driver = DummyDriver()
    helper = WebHelper(driver)
    file = tmp_path / 'page.txt'

    with pytest.warns(UserWarning):
        saved = helper.save_page_source(str(file))

    assert saved == str(file)
    assert file.read_text(encoding='utf-8') == driver.page_source


def test_save_page_source_returns_none_on_os_error(monkeypatch):
    driver = DummyDriver()
    helper = WebHelper(driver)
    monkeypatch.setattr(
        'builtins.open',
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError('no disk')),
    )

    assert helper.save_page_source('page.html') is None


def test_save_screenshot_success_warning_and_failure():
    driver = DummyDriver()
    helper = WebHelper(driver)

    with pytest.warns(UserWarning):
        assert helper.save_screenshot('shot.jpg') == 'shot.jpg'

    driver.screenshot_ok = False
    assert helper.save_screenshot('shot.png') is None
    assert driver.screenshot_calls == ['shot.jpg', 'shot.png']
