from examples.custom_condition_be_visible_in_view_port.framework.extensions.selene import (
    be,
)
from selene import Browser, Config


def test_tables():
    browser = Browser(
        Config(
            window_width=1000,
            window_height=600,
        )
    )
    browser.open('https://the-internet.herokuapp.com/tables')
    browser.element('#table1').should(be.visible)
    browser.element('#table1').should(be.visible_in_viewport)
    browser.element('#table2').should(be.visible)
    browser.element('#table2').should(be.not_visible_in_viewport)

    try:
        browser.element('#table2').with_(timeout=0.1).should(be.visible_in_viewport)
    except Exception as e:
        assert '''Timed out after 0.1s, while waiting for:
browser.element(('css selector', '#table2')).is visible in view port

Reason: ConditionNotMatchedError: condition not matched''' in str(
            e
        )
