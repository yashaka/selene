from selene import have
from selene.support.shared import browser
from tests import resources


def test_complete_task():
    browser.open(resources.TODOMVC_URL)

    browser.element('#new-todo').type('a').press_enter()
    browser.element('#new-todo').type('b').press_enter()
    browser.element('#new-todo').type('c').press_enter()
    browser.all('#todo-list>li').should(have.exact_texts('a', 'b', 'c'))

    browser.all('#todo-list>li').element_by(have.exact_text('b')).element(
        '.toggle'
    ).click()
    browser.all('#todo-list>li').by(have.css_class('completed')).should(
        have.exact_texts('b')
    )
    browser.all('#todo-list>li').by(have.no.css_class('completed')).should(
        have.exact_texts('a', 'c')
    )
