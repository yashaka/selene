from functools import reduce
from typing import Tuple

import pytest

from examples.log_all_selene_commands_with_wait__framework.framework.extensions.python.logging import (
    TranslatingFormatter,
)
from selene import browser, have
from selene.core.wait import Wait
import logging


def test_add_todos():
    """
        should log something like:

    [SE] - step: element('#new-todo') > type: a: STARTED
    [SE] - step: element('#new-todo') > type: a: ENDED
    [SE] - step: element('#new-todo') > press keys: Enter: STARTED
    [SE] - step: element('#new-todo') > press keys: Enter: ENDED
    [SE] - step: element('#new-todo') > type: b: STARTED
    [SE] - step: element('#new-todo') > type: b: ENDED
    [SE] - step: element('#new-todo') > press keys: Enter: STARTED
    [SE] - step: element('#new-todo') > press keys: Enter: ENDED
    [SE] - step: element('#new-todo') > type: c: STARTED
    [SE] - step: element('#new-todo') > type: c: ENDED
    [SE] - step: element('#new-todo') > press keys: Enter: STARTED
    [SE] - step: element('#new-todo') > press keys: Enter: ENDED
    [SE] - step: all('#todo-list>li') > has texts ('ab', 'b', 'c', 'd'): STARTED
    [SE] - step: all('#todo-list>li') > has texts ('ab', 'b', 'c', 'd'): FAILED: Message:

    Timed out after 4s, while waiting for:
    all('#todo-list>li').has texts ('ab', 'b', 'c', 'd')


    """

    browser.open('http://todomvc.com/examples/emberjs/')

    browser.element('#new-todo').type('a').press_enter()
    browser.element('#new-todo').type('b').press_enter()
    browser.element('#new-todo').type('c').press_enter()

    browser.all('#todo-list>li').should(have.texts('ab', 'b', 'c', 'd'))
