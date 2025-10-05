
"""
This example demonstrates how to add a "hard wait" (a sleep) before
Selene's waiting mechanism kicks in. This can be useful in scenarios
where you know a certain amount of time needs to pass before a condition
can be met, and you want to avoid unnecessary polling.

The key is to use a custom context manager that performs the sleep,
and then apply it as a wait decorator to the browser configuration.
"""
import time
from contextlib import contextmanager

from selene import browser, have
from selene.support._wait import with_


@contextmanager
def sleeping_before(period: float):
    """
    A context manager that sleeps for a given period before yielding.
    """
    print(f'-- hard waiting for {period}s --')
    time.sleep(period)
    yield
    print('-- hard wait finished --')


def test_hard_wait_decorator():
    """
    This test demonstrates the use of the sleeping_before context manager
    as a wait decorator.
    """
    # We configure the browser to use our custom wait decorator.
    # The decorator is created by passing an instance of our context manager
    # to the with_ function from selene.support._wait.
    # Now, before any waiting action in Selene, it will sleep for 2 seconds.
    browser.config._wait_decorator = with_(context=sleeping_before(2.0))

    # We open a page that has a heading that changes after a delay.
    # The initial heading is "Initial Heading"
    browser.open(
        'data:text/html,'
        '<h1 id="heading">Initial Heading</h1>'
        '<script>'
        'setTimeout(() => {'
        'document.getElementById("heading").innerHTML = "Final Heading";'
        '}, 1000)'
        '</script>'
    )

    # We assert that the heading has the final text.
    # Selene's `should` command will wait for the condition to be true.
    # Because of our decorator, it will first sleep for 2 seconds,
    # and then start polling. By the time it starts polling, the
    # heading will have changed, so the assertion will pass immediately.
    browser.element('#heading').should(have.text('Final Heading'))

    # We can also see the hard wait in action when a command fails.
    try:
        browser.element('#heading').should(have.text('Non-existent text'))
    except Exception as e:
        print(f'-- Selene command failed as expected: {e} --')

    # Reset the decorator to not interfere with other tests
    browser.config._wait_decorator = None


if __name__ == '__main__':
    test_hard_wait_decorator()
