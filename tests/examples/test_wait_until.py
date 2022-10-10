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
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

from selene import Browser, Config
from selene.support.conditions import be


@pytest.fixture(scope='function')
def browser():
    browser = Browser(
        Config(
            driver=webdriver.Chrome(
                service=Service(
                    ChromeDriverManager(
                        chrome_type=ChromeType.GOOGLE
                    ).install()
                )
            )
        )
    )
    yield browser
    browser.quit()


def test_progress_bar_disappears_in_time(browser):
    """Test for page with progress bar that appears each time after click on a button.

    Test should use wait_until for progress bar to disappear
        if disappeared:
            pass the test
        else
            fail the test
    """
    show_dialog_btn = browser.element('.btn-primary')
    dialog = browser.element('.modal-backdrop.fade.in')
    browser.open(
        'https://demo.seleniumeasy.com/bootstrap-progress-bar-dialog-demo.html'
    )

    show_dialog_btn.click()
    dialog.should(be.visible)
    disappeared = dialog.wait_until(be.not_.present)

    assert disappeared is True


def test_progress_bar_does_not_disappear_in_time(browser):
    """Test for page with progress bar that appears each time after click on a button.

    Test should use wait_until for progress bar to not disappear in timeout
        if not disappeared:
            pass the test
        else
            fail the test
    """
    show_dialog_btn = browser.element('.btn-primary')
    dialog = browser.element('.modal-backdrop.fade.in')
    browser.open(
        'https://demo.seleniumeasy.com/bootstrap-progress-bar-dialog-demo.html'
    )

    show_dialog_btn.click()
    dialog.should(be.visible)
    disappeared = dialog.with_(timeout=1).wait_until(be.not_.present)

    assert disappeared is False
