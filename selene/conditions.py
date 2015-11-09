# todo: consider using hamcrest matchers instead or even better - in addition to...

# todo: provide convenient function's docs


def visible(it):
    """visible"""
    return it.is_displayed()


def hidden(it):
    return not visible(it)


def absent(it):
    from selene.waits import DummyResult
    return isinstance(it, DummyResult)


def present(it):
    return not absent(it)


# todo: think on: is it worthy?
def equal(to_smth, mapped=None):
    def new_condition(it):
        mapped_it = [getattr(its_element, mapped) for its_element in it] if mapped else it
        return mapped_it == to_smth
    return new_condition

eq = equal


def not_empty(it):
    """not empty"""
    return len(it) > 0


def empty(it):
    return size(0)(it)


def text(expected_containable_text):
    expected_containable_text = str(expected_containable_text)
    def new_condition(it):
        return expected_containable_text in it.text
    new_condition.__name__ = 'contains text: %s' % expected_containable_text
    return new_condition


def texts(*expected_containable_texts):
    from operator import contains

    def new_condition(it):
        actual_texts = [item.text for item in it]
        return len(it) == len(expected_containable_texts) and \
               all(map(contains, actual_texts, expected_containable_texts))

    new_condition.__name__ = 'is of containable texts: %s' % list(expected_containable_texts)
    return new_condition


def size(length):
    def new_condition(it):
        return len(it) == length
    new_condition.__name__ = 'size: %s' % length
    return new_condition


def css_class(cssclass):
    def new_condition(it):
        return cssclass in it.get_attribute('class')
    new_condition.__name__ = 'has css class: %s' % cssclass
    return new_condition


def has_text(it):
    return len(it.text) > 0
