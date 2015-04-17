# todo: consider using hamcrest matchers instead or even better - in addition to...

# todo: provide convenient function's docs


def visible(it):
    """visible"""
    return it.is_displayed()

def absent(it):
    return not visible(it)

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
    return of_size(0)(it)


def of_size(size):
    def new_condition(it):
        return len(it) == size
    new_condition.__name__ = 'of_size_%s' % size
    new_condition.__doc__ = 'of_size_%s' % size
    return new_condition


