def test_thread_last__demo_with_re_sub_only():
    from selene.common.fp import thread_last
    import re

    result = thread_last(
        '_have_.special.NumberLike._attr_',
        (re.sub, r'([a-z0-9])([A-Z])', r'\1 \2'),
        (re.sub, r'(\w)\.(\w)', r'\1 \2'),
        (re.sub, r'(^_+|_+$)', ''),
        (re.sub, r'_+', ' '),
        (re.sub, r'(\s)+', r'\1'),
        str.lower,
    )

    assert result == 'have special number like attr'


def test_thread_last__demo_with_common_str_fns():
    from selene.common.fp import thread_last, map_with
    import re

    result = thread_last(
        ['_have.special_number_', 10],
        map_with(str),
        ''.join,
        (re.sub, r'(^_+|_+$)', ''),
        (re.sub, r'_+', ' '),
        (re.sub, r'(\w)\.(\w)', r'\1 \2'),
        str.split,
    )

    assert result == ['have', 'special', 'number', '10']


def test_thread_last__threads_in_first_to_last_order():
    from selene.common.fp import thread_last

    append = lambda the_item, to_acc: to_acc + the_item

    # WHEN
    result = thread_last(
        '',
        (append, 'a'),
        (append, 'b'),
        (append, 'c'),
    )

    assert 'abc' == result


def test_thread_first__threads_in_first_to_last_order():
    from selene.common.fp import thread_first

    append = lambda to_acc, the_item: to_acc + the_item

    # WHEN
    result = thread_first(
        '',
        (append, 'a'),
        (append, 'b'),
        (append, 'c'),
    )

    assert 'abc' == result


def test_thread__is_more_bulky__when_signatures_are_similar():
    from selene.common.fp import thread

    append = lambda to_acc, the_item: to_acc + the_item

    # WHEN
    result = thread(
        '',
        lambda acc: append(acc, 'a'),
        lambda acc: append(acc, 'b'),
        lambda acc: append(acc, 'c'),
    )

    assert 'abc' == result


def test_thread__is_handy__when_signatures_are_too_different():
    from selene.common.fp import thread

    suffix = lambda to_acc, the_item: to_acc + the_item
    prefix = lambda the_item, to_acc: the_item + to_acc

    # WHEN
    result = thread(
        'b',
        lambda acc: suffix(acc, 'c'),
        lambda acc: prefix('a', acc),
    )

    assert 'abc' == result
