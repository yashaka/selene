from functools import wraps
import time

import pytest

from selene import have, browser
from selene.core.wait import Wait
from tests import resources


def pre_pause_in_wait(pause_duration: float = 0.5):
    """
    Decorator to add a hard-wait (sleep) before any Selene waiting command.
    
    This example demonstrates how to use `config._wait_decorator` to add
    a sleep/pause before executing wait commands. This can be useful for
    debugging or when dealing with applications that need extra time
    before polling conditions.
    
    Args:
        pause_duration: Time in seconds to pause before each wait command
    """
    def pre_pause_decorator(for_):
        @wraps(for_)
        def decorated(fn):
            # Add hard-wait (sleep) before executing the wait command
            time.sleep(pause_duration)
            # Execute the original wait command
            return for_(fn)
        return decorated
    return pre_pause_decorator


@pytest.fixture(scope='function', autouse=True)
def browser_management():
    """
    Configure browser to use pre_pause_in_wait decorator.
    
    This will add a 0.3 second pause before each Selene wait command,
    slowing down test execution but allowing better observation of
    what's happening during automation.
    """
    # Set the wait decorator to add pause before each wait
    browser.config._wait_decorator = pre_pause_in_wait(pause_duration=0.3)
    
    yield
    
    # Reset browser after test
    browser.quit()


def test_pre_pause_in_wait():
    """
    Test demonstrating the pre_pause_in_wait decorator.
    
    Each command that involves waiting (type, press_enter, should) will:
    1. First pause for 0.3 seconds (hard-wait/sleep)
    2. Then execute the actual wait command
    
    This makes test execution slower but more observable.
    Notice how there's a deliberate pause before each action.
    """
    browser.open(resources.TODOMVC_URL)
    
    # Each of these commands will pause 0.3s before executing
    browser.element('#new-todo').type('First task').press_enter()
    browser.element('#new-todo').type('Second task').press_enter()
    browser.element('#new-todo').type('Third task').press_enter()
    
    # This assertion will also pause before checking the condition
    browser.all('#todo-list>li').should(have.texts('First task', 'Second task', 'Third task'))
