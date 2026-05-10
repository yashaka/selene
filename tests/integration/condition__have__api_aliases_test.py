import pytest

from selene import have
from tests.integration.helpers.givenpage import GivenPage


def test_have_attribute_css_property_and_js_property_with_deprecated_second_arg(
    session_browser,
):
    page = GivenPage(session_browser.driver)
    page.opened_with_body("""
        <div id="hero"
             data-kind="card"
             style="display:block">Hero</div>
        """)

    hero = session_browser.element('#hero')

    with pytest.warns(DeprecationWarning):
        hero.should(have.attribute('data-kind', 'card'))

    with pytest.warns(DeprecationWarning):
        hero.should(have.css_property('display', 'block'))

    with pytest.warns(DeprecationWarning):
        hero.should(have.js_property('textContent', 'Hero'))


def test_have_size_at_least_pending_deprecation_and_size_aliases(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body("""
        <ul>
          <li class="row">A</li>
          <li class="row">B</li>
          <li class="row">C</li>
        </ul>
        """)

    rows = session_browser.all('.row')
    rows.should(have.size(3))
    rows.should(have.size_less_than(4))
    rows.should(have.size_less_than_or_equal(3))
    rows.should(have.size_greater_than(2))
    rows.should(have.size_greater_than_or_equal(3))

    with pytest.warns(PendingDeprecationWarning):
        rows.should(have.size_at_least(3))


def test_have_js_returned_aliases_warn_and_work(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body("<div>js</div>")

    with pytest.warns(DeprecationWarning):
        session_browser.should(have.js_returned_true('return true'))

    with pytest.warns(DeprecationWarning):
        session_browser.should(have.js_returned(2, 'return arguments[0] + 1', 1))

    session_browser.should(have.script_returned('ok', 'return "ok"'))
