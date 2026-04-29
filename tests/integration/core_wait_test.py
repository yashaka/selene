import time

import pytest
from selenium.webdriver.common.by import By

from selene import be
from selene.core.exceptions import TimeoutException
from tests.integration.helpers.givenpage import GivenPage


def test_waits_for_visibility_minimum_needed_time(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        '''
        <a href="#second" style="display:none">go to Heading 2</a>
        <h2 id="second">Heading 2</h2>
        '''
    ).execute_script_with_timeout(
        'document.getElementsByTagName("a")[0].style = "display:block";', 1
    )
    stamp_before = time.time_ns()
    session_browser.element('a').wait.at_most(2).for_(be.visible)

    session_browser.driver.find_element(By.CSS_SELECTOR, 'a').click()

    stamp_after = time.time_ns()
    deviation_sec = 0.2
    assert stamp_after - stamp_before < (1 + deviation_sec) * pow(10, 9)
    assert "second" in session_browser.driver.current_url


def test_fails_on_timeout_during_waiting_for_visibility(
    session_browser,
):
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        '''
        <a href="#second" style="display:none">go to Heading 2</a>
        <h2 id="second">Heading 2</h2>
        '''
    ).execute_script_with_timeout(
        'document.getElementsByTagName("a")[0].style = "display:block";', 1.1
    )
    with pytest.raises(TimeoutException):
        session_browser.element('a').wait.at_most(1).for_(be.visible)
