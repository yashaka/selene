from functools import reduce
from typing import Tuple
import pytest
from selene import have, browser
from selene.core.wait import Wait
import logging
from tests import resources

class SeleneFormatter(logging.Formatter):
    translations = (
        ('browser.element', 'element'),
        ('browser.all', 'all'),
    )

    def formatMessage(self, record: logging.LogRecord) -> str:
        original = super().formatMessage(record)

        def translate(initial: str, item: Tuple[str, str]):
            old, new = item
            return initial.replace(old, new)

        return reduce(
            translate,
            self.translations,
            original,
        )

log = logging.getLogger('SE')
log.setLevel(20)
handler = logging.StreamHandler()
formatter = SeleneFormatter("[%(name)s] - %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

def log_on_wait(wait: Wait):
    def log_on_wait_decorator(for_):
        def decorated(fn):
            entity = wait.entity
            log.info('step: %s > %s: STARTED', entity, fn)
            try:
                res = for_(fn)
                log.info('step: %s > %s: ENDED', entity, fn)
                return res
            except Exception as error:
                log.info('step: %s > %s: FAILED: %s', entity, fn, error)
                raise error

        return decorated

    return log_on_wait_decorator

@pytest.fixture(scope='function', autouse=True)
def browser_management():
    SeleneFormatter.translations = (
        ('browser.element', 'element'),
        ('browser.all', 'all'),
        ("'css selector', ", ""),
        (r"('\ue007',)", "Enter"),
        ('((', '('),
        ('))', ')'),
        (': has ', ': have '),
        (': have ', ': should have '),
        (': is ', ': should be'),
    )
    browser.config._wait_decorator = log_on_wait
    yield

def test_logging_via__wait_decorator():
    """
    should log something like:

    [SE] - step: element('#new-todo') > type: a: STARTED
    [SE] - step: element('#new-todo') > type: a: ENDED
    ...
    Timed out after 4s, while waiting for:
    all('#todo-list>li').has texts ('ab', 'b', 'c', 'd')
    """

    # Arrange – Setup browser and open page
    browser.open(resources.TODOMVC_URL)

    # Act – Add todos via UI
    browser.element('#new-todo').type('a').press_enter()
    browser.element('#new-todo').type('b').press_enter()
    browser.element('#new-todo').type('c').press_enter()

    # Assert – Verify todos are present and correct
    browser.all('#todo-list>li').should(have.texts('ab', 'b', 'c', 'd'))
