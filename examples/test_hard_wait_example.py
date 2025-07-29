import time
from selene.support.shared import browser
from selene import have

def test_example_with_hard_wait():
    browser.open('https://example.com')
    time.sleep(3)  # ⏱ Hard wait before command
    browser.element('h1').should(have.text('Example Domain'))
