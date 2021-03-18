from selene import have, Config
from selene.support.shared import browser


def test_complete_task():
    # browser.config.driver =
    # browser.config.hook_wait_failure=\
    #     lambda error: TimeoutException(error.msg.replace('file://', ''))
    # browser.config.timeout = 6
    # browser.config.save_screenshot_on_failure = False
    # browser.config.save_page_source_on_failure = False
    browser.open('http://todomvc.com/examples/emberjs/')

    browser.element('#new-todo').type('a').press_enter()
    browser.element('#new-todo').type('b').press_enter()
    browser.element('#new-todo').type('c').press_enter()
    # browser.element('#new-todo').with_(Config(timeout=2)).should(have.value('foo'))
    browser.all('#todo-list>li').should(have.exact_texts('a', 'b', 'c'))

    browser.all('#todo-list>li').element_by(have.exact_text('b')).element(
        '.toggle'
    ).click()
    browser.all('#todo-list>li').filtered_by(
        have.css_class('completed')
    ).should(have.exact_texts('b'))
    browser.all('#todo-list>li').filtered_by(
        have.no.css_class('completed')
    ).should(have.exact_texts('a', 'c'))
