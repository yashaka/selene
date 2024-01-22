from selenium.webdriver import Keys

from selene import have, be
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


log = logging.getLogger(__file__)
log.setLevel(20)
handler = StringHandler()
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)


class LogToStringStreamContext:
    def __init__(self, title, params):
        self.title = title
        self.params = params

    def __enter__(self):
        log.info('%s: STARTED', self.title)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            log.info('%s: PASSED', self.title)
        else:
            log.info('%s: FAILED:\n\n%s\n%s', self.title, exc_type, exc_val)


def test_logging_via__wait_decorator(quit_shared_browser_afterwards):
    from selene import support

    browser = selene.browser.with_(
        _wait_decorator=support._logging.wait_with(context=LogToStringStreamContext),
        timeout=0.3,
    )

    browser.open(resources.TODOMVC_URL)

    (browser.element('#new-todo').should(be.enabled.and_(be.visible)).should(be.blank))
    browser.element('#new-todo').type('a').press_enter()
    (
        browser.element('#new-todo')
        .type('b')
        .press_tab()
        .should(be.not_.blank.and_(have.value('b')))
    )
    browser.element('#new-todo').press(Keys.BACKSPACE).type('c').press_enter()

    try:
        browser.all('#todo-list>li').should(have.texts('a', 'b', 'c'))
    except AssertionError:
        assert (
            '''
element('#new-todo'): should be enabled and be visible: STARTED
element('#new-todo'): should be enabled and be visible: PASSED
element('#new-todo'): should have exact text  and have attribute 'value' with value '': STARTED
element('#new-todo'): should have exact text  and have attribute 'value' with value '': PASSED
element('#new-todo'): type: a: STARTED
element('#new-todo'): type: a: PASSED
element('#new-todo'): press keys: ENTER: STARTED
element('#new-todo'): press keys: ENTER: PASSED
element('#new-todo'): type: b: STARTED
element('#new-todo'): type: b: PASSED
element('#new-todo'): press keys: TAB: STARTED
element('#new-todo'): press keys: TAB: PASSED
element('#new-todo'): should have no (exact text  and have attribute 'value' with value '') and have attribute 'value' with value 'b': STARTED
element('#new-todo'): should have no (exact text  and have attribute 'value' with value '') and have attribute 'value' with value 'b': PASSED
element('#new-todo'): press keys: BACKSPACE: STARTED
element('#new-todo'): press keys: BACKSPACE: PASSED
element('#new-todo'): type: c: STARTED
element('#new-todo'): type: c: PASSED
element('#new-todo'): press keys: ENTER: STARTED
element('#new-todo'): press keys: ENTER: PASSED
all('#todo-list>li'): should have texts ('a', 'b', 'c'): STARTED
all('#todo-list>li'): should have texts ('a', 'b', 'c'): FAILED:

<class 'selene.core.exceptions.TimeoutException'>
Message:\u0020

Timed out after 0.3s, while waiting for:
browser.all(('css selector', '#todo-list>li')).has texts ('a', 'b', 'c')

Reason: AssertionError: actual visible_texts: ['a', 'c']
            '''.strip()
            in handler.stream
        )
