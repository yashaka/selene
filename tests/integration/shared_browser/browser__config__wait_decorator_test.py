from selene import have
from selene.core.wait import Wait
import selene
import logging

from tests import resources


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
    def decorator_factory(wait: Wait):
        def decorator(for_):
            def decorated(fn):
                entity = wait.entity
                log.info('%sstep: %s > %s: STARTED', prefix, entity, fn)
                try:
                    res = for_(fn)
                    log.info('%sstep: %s > %s: ENDED', prefix, entity, fn)
                    return res
                except Exception as error:
                    log.info(
                        '%sstep: %s > %s: FAILED: %s',
                        prefix,
                        entity,
                        fn,
                        error,
                    )
                    raise error

            return decorated

        return decorator

    return decorator_factory


def test_logging_via__wait_decorator(quit_shared_browser_afterwards):
    browser = selene.browser.with_(_wait_decorator=log_on_wait('[1] - '), timeout=0.3)

    browser.open(resources.TODOMVC_URL)

    browser.element('#new-todo').type('a').press_enter()
    browser.with_(_wait_decorator=log_on_wait('[2] - ')).element('#new-todo').type(
        'b'
    ).press_enter()
    browser.config._wait_decorator = log_on_wait('[4] - ')
    browser.element('#new-todo').with_(_wait_decorator=log_on_wait('[3] - ')).type(
        'c'
    ).press_enter()

    try:
        browser.all('#todo-list>li').should(have.texts('ab', 'b', 'c', 'd'))
    except AssertionError:
        assert (
            r'''
[SE] - [1] - step: browser.element(('css selector', '#new-todo')) > type: a: STARTED
[SE] - [1] - step: browser.element(('css selector', '#new-todo')) > type: a: ENDED
[SE] - [1] - step: browser.element(('css selector', '#new-todo')) > press keys: ('\ue007',): STARTED
[SE] - [1] - step: browser.element(('css selector', '#new-todo')) > press keys: ('\ue007',): ENDED
[SE] - [2] - step: browser.element(('css selector', '#new-todo')) > type: b: STARTED
[SE] - [2] - step: browser.element(('css selector', '#new-todo')) > type: b: ENDED
[SE] - [2] - step: browser.element(('css selector', '#new-todo')) > press keys: ('\ue007',): STARTED
[SE] - [2] - step: browser.element(('css selector', '#new-todo')) > press keys: ('\ue007',): ENDED
[SE] - [3] - step: browser.element(('css selector', '#new-todo')) > type: c: STARTED
[SE] - [3] - step: browser.element(('css selector', '#new-todo')) > type: c: ENDED
[SE] - [3] - step: browser.element(('css selector', '#new-todo')) > press keys: ('\ue007',): STARTED
[SE] - [3] - step: browser.element(('css selector', '#new-todo')) > press keys: ('\ue007',): ENDED
[SE] - [4] - step: browser.all(('css selector', '#todo-list>li')) > has texts ('ab', 'b', 'c', 'd'): STARTED
[SE] - [4] - step: browser.all(('css selector', '#todo-list>li')) > has texts ('ab', 'b', 'c', 'd'): FAILED: Message:
            '''.strip()
            in handler.stream
        )
