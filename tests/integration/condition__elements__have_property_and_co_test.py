from selene import have
from tests.integration.helpers.givenpage import GivenPage


def test_have_no_js_property_and_css_property_descriptor_methods_work(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)

    GivenPage(browser.driver).opened_with_body(
        '''
        <input id="field" value="John">
        <div id="box" style="display: block">Box</div>
        '''
    )

    browser.element('#field').should(
        have.no.js_property('value').value_containing('Doe')
    )

    browser.element('#box').should(
        have.no.css_property('display').value_containing('none')
    )