import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import pytest

from selene import Config, browser


def safe_filename(value: str, max_length: int = 180) -> str:
    normalized = re.sub(r'[^\w.-]+', '_', value, flags=re.UNICODE).strip('_')
    return (normalized or 'test')[:max_length]


@pytest.fixture(scope='session', autouse=True)
def browser_management():
    browser.config.timeout = 0.5
    browser.config.reports_folder = str(Path(__file__).parent.parent / 'reports')

    yield

    browser.quit()


@pytest.fixture(autouse=True)
def name_selene_failure_screenshots_by_test(request):
    original_save_screenshot_strategy = browser.config._save_screenshot_strategy

    test_name = safe_filename(request.node.nodeid.replace('::', '__'))

    def save_screenshot_with_test_name(
        config: Config,
        path: Optional[str] = None,
    ) -> Optional[str]:
        if path is None:
            timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S_%f')
            reports_folder = config.reports_folder or '.'
            path = str(Path(reports_folder) / f'{test_name}-{timestamp}.png')

        Path(path).parent.mkdir(parents=True, exist_ok=True)

        saved = path if config.driver.get_screenshot_as_file(path) else None
        config.last_screenshot = saved

        return saved

    browser.config._save_screenshot_strategy = save_screenshot_with_test_name

    yield

    browser.config._save_screenshot_strategy = original_save_screenshot_strategy
