from selene import have
from selene.support.shared import browser as selene_browser
import logging


class StringHandler(logging.Handler):
    terminator = '\n'

    def __init__(self):
        logging.Handler.__init__(self)
        self.stream = ''

    def emit(self, record):
        try:
            msg = self.format(record)
            # issue 35046: merged two stream.writes into one.
            self.stream += msg + self.terminator
        except Exception:
            self.handleError(record)


log = logging.getLogger('SE')
log.setLevel(20)
handler = StringHandler()
formatter = logging.Formatter("[%(name)s] - %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)


def log_on_wait(prefix):
    def decorator(for_):
        def decorated(fn):
            log.info('%sstep: %s: STARTED', prefix, fn)
            try:
                res = for_(fn)
                log.info('%sstep: %s: ENDED', prefix, fn)
                return res
            except Exception as error:
                log.info('%sstep: %s: FAILED: %s', prefix, fn, error)
                raise error

        return decorated

    return decorator


def test_logging_via__wait_decorator():
    browser = selene_browser.with_(_wait_decorator=log_on_wait('[1] - '))

    browser.open('http://todomvc.com/examples/emberjs/')

    browser.element('#new-todo').type('a').press_enter()
    browser.with_(_wait_decorator=log_on_wait('[2] - ')).element(
        '#new-todo'
    ).type('b').press_enter()
    browser.config._wait_decorator = log_on_wait('[4] - ')
    browser.element('#new-todo').with_(
        _wait_decorator=log_on_wait('[3] - ')
    ).type('c').press_enter()

    try:
        browser.all('#todo-list>li').with_(timeout=0.3).should(
            have.texts('ab', 'b', 'c', 'd')
        )
    except AssertionError:
        assert (
            r'''
[SE] - [1] - step: type: a: STARTED
[SE] - [1] - step: type: a: ENDED
[SE] - [1] - step: press keys: ('\ue007',): STARTED
[SE] - [1] - step: press keys: ('\ue007',): ENDED
[SE] - [2] - step: type: b: STARTED
[SE] - [2] - step: type: b: ENDED
[SE] - [2] - step: press keys: ('\ue007',): STARTED
[SE] - [2] - step: press keys: ('\ue007',): ENDED
[SE] - [3] - step: type: c: STARTED
[SE] - [3] - step: type: c: ENDED
[SE] - [3] - step: press keys: ('\ue007',): STARTED
[SE] - [3] - step: press keys: ('\ue007',): ENDED
[SE] - [4] - step: has texts ('ab', 'b', 'c', 'd'): STARTED
[SE] - [4] - step: has texts ('ab', 'b', 'c', 'd'): FAILED: Message:
            '''.strip()
            in handler.stream
        )
