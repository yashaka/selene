# MIT License
#
# Copyright (c) 2015-2022 Iakiv Kramarenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from selene import browser, Browser, Element, have
from selene.core.condition import Condition
from selene.core.conditions import ElementCondition, BrowserCondition
from tests import resources

def have_produced_todos(number: int) -> Condition[Element]:
    def fn(entity: Element) -> None:
        size = len(browser.all("#todo-list>li"))
        produced_enough = size >= number
        if not produced_enough:
            entity.type('one more').press_enter()
            raise AssertionError(f'actual produced todos were: {size}')
    return Condition(f'have produced {number} todos', fn)

def test_wait_for_produced_todos_v1():
    # Arrange – Setup
    browser.open(resources.TODOMVC_URL)
    # Act – None for this style, the custom condition triggers
    # Assert – Verify todos created
    browser.element('#new-todo').should(have_produced_todos(3))

def produced_todos(number: int) -> Condition[Browser]:
    def fn(entity: Browser) -> None:
        size = len(browser.all("#todo-list>li"))
        produced_enough = size >= number
        if not produced_enough:
            entity.element('#new-todo').type('one more').press_enter()
            raise AssertionError(f'actual produced todos were: {size}')
    return Condition(f'have produced {number} todos', fn)

def test_wait_for_produced_todos_v2():
    # Arrange – Setup
    browser.open('http://todomvc.com/examples/emberjs/')
    # Act – None
    # Assert
    browser.wait.for_(produced_todos(3))

def test_wait_for_notification_after_reload_v1():
    # Arrange – Setup
    browser.open('https://the-internet.herokuapp.com/notification_message_rendered')
    # Act – Action in the custom wait function
    def assert_action_successful_on_reload(entity):
        browser.element('[href*=notification_message]').click()
        # Assert – Verify notification text
        if not browser.element('#flash').matching(
            have.exact_text('Action successful\n×')
        ):
            raise AssertionError('wrong message received')
    # Assert
    browser.wait.for_(assert_action_successful_on_reload)

def test_wait_for_notification_after_reload_v2():
    """
    more descriptive implementation
    with custom rendering of error message on failure
    """
    # Arrange – Setup
    browser.open('https://the-internet.herokuapp.com/notification_message_rendered')
    # Act
    def assert_action_successful_on_reload(entity):
        browser.element('[href*=notification_message]').click()
        notification = browser.element('#flash')
        webelement = notification()
        actual = webelement.text
        expected = 'Action successful\n×'
        # Assert
        if actual != expected:
            raise AssertionError(
                f'notification message was wrong:'
                f'\texpected: {expected}'
                f'\t  actual: {actual}'
            )
    browser.wait.for_(assert_action_successful_on_reload)

def test_wait_for_notification_after_reload_v3():
    # Arrange – Setup
    browser.open('https://the-internet.herokuapp.com/notification_message_rendered')
    # Act & Assert are in the custom condition
    def notification_on_reload(message: str) -> Condition[Browser]:
        def fn(entity: Browser):
            entity.element('[href*=notification_message]').click()
            notification = entity.element('#flash')
            webelement = notification()
            actual = webelement.text
            expected = message
            # Assert
            if actual != expected:
                raise AssertionError(
                    f'notification message was wrong:'
                    f'\texpected: {expected}'
                    f'\t  actual: {actual}'
                )
        return Condition(
            f'received message {message} on reload',
            fn,
        )
    browser.wait.for_(
        notification_on_reload('Action successful\n×').or_(
            notification_on_reload('Action unsuccesful, please try again\n×')
        )
    )

def test_wait_for_notification_after_reload_v4():
    # Arrange – Setup
    browser.open('https://the-internet.herokuapp.com/notification_message_rendered')
    # Act in custom wait function
    def assert_action_successful_on_reload(entity):
        browser.element('[href*=notification_message]').click()
        # Assert
        have.exact_text('Action successful\n×')(browser.element('#flash'))
    browser.wait.for_(assert_action_successful_on_reload)

def test_wait_for_notification_after_reload_v5():
    # Arrange – Setup
    browser.open('https://the-internet.herokuapp.com/notification_message_rendered')
    # Act & Assert in lambda
    browser.wait.for_(
        lambda _: (
            browser.element('[href*=notification_message]').click(),
            have.exact_text('Action successful\n×')(browser.element('#flash')),
        )
    )

def test_wait_for_notification_after_reload_v6():
    # Arrange – Setup
    browser.open('https://the-internet.herokuapp.com/notification_message_rendered')
    # Act & Assert in lambda, with optimized click
    browser.wait.for_(
        lambda _: (
            browser.element('[href*=notification_message]')().click(),
            have.exact_text('Action successful\n×')(browser.element('#flash')),
        )
    )
    '''
    notice how we called `().click()` instead of `.click()` on notification element
    extra parenthesis allows to get actual webelement
    that has not implicit waiting for click to be passed
    by this - we ensure that there will be no nested waiting
    in addition to "outher" `browser.wait.for`
    '''
