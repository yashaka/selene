"""
Example: Hard Wait (sleep) before waiting command in Selene

WARNING: Using time.sleep() is generally discouraged. It can make tests flaky or unnecessarily slow. 
Use Selene's explicit waits whenever possible, and only use sleep for debugging or rare edge cases.

To run:
    python examples/waits/hard_wait_then_wait_example.py
Requires: selene, selenium, webdriver-manager
"""
import time
from selene.support.shared import browser
from selene import be
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

browser.config.driver_name = 'chrome'
browser.config.driver = Service(ChromeDriverManager().install())
browser.open('https://example.com')

time.sleep(2)
browser.element('h1').should(be.visible)

browser.element('h1').should(be.visible)

browser.quit()
