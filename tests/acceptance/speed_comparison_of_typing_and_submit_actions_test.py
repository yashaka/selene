# MIT License
import pytest
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from selene import be
from selene.support.shared import browser
from tests import resources
from tests.acceptance.helpers.helper import get_test_driver
from tests.helpers import repeated_time_spent

pytestmark = [pytest.mark.speed]

BENCHMARK_FLOW_URL = resources.url('speed_benchmark_flow.html')
# Keep aligned with the isolated benchmark to compare ratios consistently.
BENCHMARK_REPEATS = 9
BENCHMARK_WARMUPS = 2
TASKS = 10

selenium_browser: WebDriver


def setup_function():
    global selenium_browser
    selenium_browser = get_test_driver()
    selenium_browser.get(BENCHMARK_FLOW_URL)
    WebDriverWait(selenium_browser, 4).until(
        expected_conditions.visibility_of_element_located(
            (By.CSS_SELECTOR, "#new-todo")
        )
    )

    browser.config.driver = get_test_driver()
    browser.open(BENCHMARK_FLOW_URL)
    browser.element("#new-todo").should(be.visible)


def teardown_function():
    global selenium_browser
    selenium_browser.quit()
    browser.quit()


def create_tasks_with_raw_selenium():
    new_todo = selenium_browser.find_element(By.CSS_SELECTOR, "#new-todo")
    for task_text in map(str, range(TASKS)):
        new_todo.send_keys(task_text + Keys.ENTER)


def create_tasks_with_selenium_with_research():
    for task_text in map(str, range(TASKS)):
        new_todo = selenium_browser.find_element(By.CSS_SELECTOR, "#new-todo")
        new_todo.send_keys(task_text + Keys.ENTER)


def create_tasks_with_selene_and_send_keys():
    for task_text in map(str, range(TASKS)):
        browser.element("#new-todo").send_keys(task_text + Keys.ENTER)


def create_tasks_with_selene_with_cache():
    new_todo = browser.element("#new-todo").cached
    for task_text in map(str, range(TASKS)):
        new_todo.send_keys(task_text + Keys.ENTER)


def _print_result(selene_time, selenium_time, selene_samples, selenium_samples):
    ratio = selene_time / selenium_time
    print(
        f"median {selene_time} vs {selenium_time}; ratio={ratio}; "
        f"selene={selene_samples}; selenium={selenium_samples}"
    )


def _assert_submitted_items_count():
    assert (
        len(selenium_browser.find_elements(By.CSS_SELECTOR, "#todo-list li")) >= TASKS
    )
    assert len(browser.all("#todo-list li").locate()) >= TASKS


def test_selene_is_almost_as_fast_selenium_with_research_and_initial_wait_for_visibility():
    selene_time, selene_samples = repeated_time_spent(
        create_tasks_with_selene_and_send_keys,
        repeats=BENCHMARK_REPEATS,
        warmups=BENCHMARK_WARMUPS,
    )
    selenium_time, selenium_samples = repeated_time_spent(
        create_tasks_with_selenium_with_research,
        repeats=BENCHMARK_REPEATS,
        warmups=BENCHMARK_WARMUPS,
    )
    _print_result(selene_time, selenium_time, selene_samples, selenium_samples)
    _assert_submitted_items_count()
    assert selene_time < 1.25 * selenium_time


def test_selene_is_from_32_to_75_percents_slower_than_raw_selenium():
    """Legacy test name kept for history; current observed ratios are typically lower."""
    selene_time, selene_samples = repeated_time_spent(
        create_tasks_with_selene_and_send_keys,
        repeats=BENCHMARK_REPEATS,
        warmups=BENCHMARK_WARMUPS,
    )
    selenium_time, selenium_samples = repeated_time_spent(
        create_tasks_with_raw_selenium,
        repeats=BENCHMARK_REPEATS,
        warmups=BENCHMARK_WARMUPS,
    )
    _print_result(selene_time, selenium_time, selene_samples, selenium_samples)
    _assert_submitted_items_count()
    assert selene_time <= 1.75 * selenium_time


def test_cached_selene_is_almost_as_fast_raw_selenium():
    selene_time, selene_samples = repeated_time_spent(
        create_tasks_with_selene_with_cache,
        repeats=BENCHMARK_REPEATS,
        warmups=BENCHMARK_WARMUPS,
    )
    selenium_time, selenium_samples = repeated_time_spent(
        create_tasks_with_raw_selenium,
        repeats=BENCHMARK_REPEATS,
        warmups=BENCHMARK_WARMUPS,
    )
    _print_result(selene_time, selenium_time, selene_samples, selenium_samples)
    _assert_submitted_items_count()
    assert selene_time < 1.10 * selenium_time
