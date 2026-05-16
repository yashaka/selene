from pathlib import Path

from selene.common import fp


def test_identity_returns_same_object():
    payload = {'a': 1}
    assert fp.identity(payload) is payload


def test_pipe_composes_in_declared_order_and_skips_none():
    plus_one = lambda x: x + 1
    times_two = lambda x: x * 2

    piped = fp.pipe(plus_one, None, times_two)
    assert piped(3) == 8


def test_pipe_without_functions_returns_none():
    assert fp.pipe() is None


def test_thread_applies_functions_to_argument():
    result = fp.thread(' selene ', str.strip, str.upper, lambda x: f'[{x}]')
    assert result == '[SELENE]'


def test_do_executes_side_effect_and_returns_original_argument():
    seen = []
    wrapped = fp.do(lambda x: seen.append(x * 2))

    value = wrapped(5)

    assert value == 5
    assert seen == [10]


def test_write_silently_writes_file_and_returns_tuple(tmp_path):
    path = tmp_path / 'note.txt'

    result = fp.write_silently(str(path), 'hello')

    assert result == (str(path), 'hello')
    assert path.read_text(encoding='utf-8') == 'hello'


def test_write_silently_returns_none_on_os_error(monkeypatch):
    monkeypatch.setattr(
        'builtins.open', lambda *args, **kwargs: (_ for _ in ()).throw(OSError('disk'))
    )

    assert fp.write_silently('/nowhere/file.txt', 'x') is None
