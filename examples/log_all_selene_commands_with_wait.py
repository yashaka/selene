from selene import have
from selene.support.shared import browser
import logging

log = logging.getLogger('SE')
log.setLevel(20)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(name)s] - %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)


def log_on_wait(for_):
    def decorated(fn):
        log.info('step: %s: STARTED', fn)
        try:
            res = for_(fn)
            log.info('step: %s: ENDED', fn)
            return res
        except Exception as error:
            log.info('step: %s: FAILED: %s', fn, error)
            raise error

    return decorated


def test_logging_via__wait_decorator():
    """
        should log something like:

    [SE] - step: type: a: STARTED
    [SE] - step: type: a: ENDED
    [SE] - step: press keys: ('\ue007',): STARTED
    [SE] - step: press keys: ('\ue007',): ENDED
    [SE] - step: type: b: STARTED
    [SE] - step: type: b: ENDED
    [SE] - step: press keys: ('\ue007',): STARTED
    [SE] - step: press keys: ('\ue007',): ENDED
    [SE] - step: type: c: STARTED
    [SE] - step: type: c: ENDED
    [SE] - step: press keys: ('\ue007',): STARTED
    [SE] - step: press keys: ('\ue007',): ENDED
    [SE] - step: has texts ('ab', 'b', 'c', 'd'): STARTED
    [SE] - step: has texts ('ab', 'b', 'c', 'd'): FAILED: Message:

    Timed out after 4s, while waiting for:browser.all(('css selector', '#todo-list>li')).has texts ('ab', 'b', 'c', 'd')
    Reason: AssertionError: actual visible_texts: ['a', 'b', 'c']

    """
    browser.config._wait_decorator = log_on_wait

    browser.open('http://todomvc.com/examples/emberjs/')

    browser.element('#new-todo').type('a').press_enter()
    browser.element('#new-todo').type('b').press_enter()
    browser.element('#new-todo').type('c').press_enter()

    browser.all('#todo-list>li').should(have.texts('ab', 'b', 'c', 'd'))
