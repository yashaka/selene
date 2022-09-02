import pytest
import logging

from examples.log_all_selene_commands_with_wait__framework.framework import (
    assist,
)
from examples.log_all_selene_commands_with_wait__framework.framework.assist.selene.extensions import (
    log_with,
)
from selene.support.shared import browser


log = logging.getLogger('SE')
log.setLevel(20)

on_wait_report_to_log = assist.selene.extensions.log_with(
    logger=log,
    added_handler_translations=[
        ('browser.element', 'element'),
        ('browser.all', 'all'),
        ("'css selector', ", ""),
        (r"('\ue007',)", "Enter"),
        ('((', '('),
        ('))', ')'),
        (': has ', ': have '),
        (': have ', ': should have '),
        (': is ', ': should be'),
    ],
)


@pytest.fixture(scope='session', autouse=True)
def browser_management():
    browser.config._wait_decorator = on_wait_report_to_log

    yield
