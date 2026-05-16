import pytest
from selenium.common.exceptions import WebDriverException

from selene import command, have
from tests import resources
from tests.integration.helpers.givenpage import GivenPage


def test_drops_file_to_self_when_input_type_file_inside_target(session_browser):
    browser = session_browser
    page = GivenPage(browser.driver)
    page.opened_empty()
    page.load_body(
        """
        <div id="dropzone">
          <input id="file-input" type="file" style="display:none" />
          <span id="result"></span>
        </div>
        """
    )
    page.execute_script(
        """
        document.getElementById('file-input').addEventListener('change', function () {
          var value = this.value || '';
          var fileName = value.split('\\\\').pop();
          document.getElementById('result').textContent = fileName;
        });
        """
    )

    browser.element('#dropzone').perform(command.js.drop_file(resources.path('selenite.png')))

    browser.element('#result').should(have.exact_text('selenite.png'))


def test_element_drop_file_shortcut(session_browser):
    browser = session_browser
    page = GivenPage(browser.driver)
    page.opened_with_body(
        """
        <div id="dropzone">
          <input id="file-input" type="file" style="display:none" />
          <span id="result"></span>
        </div>
        """
    )
    page.execute_script(
        """
        document.getElementById('file-input').addEventListener('change', function () {
          var value = this.value || '';
          var fileName = value.split('\\\\').pop();
          document.getElementById('result').textContent = fileName;
        });
        """
    )

    browser.element('#dropzone').drop_file(resources.path('selenite.png'))

    browser.element('#result').should(have.exact_text('selenite.png'))


def test_drops_file_to_self_in_react_mui(session_browser):
    browser = session_browser
    try:
        browser.open('https://app.qa.guru/automation-practice-form/')
    except WebDriverException as error:
        if 'ERR_CONNECTION_CLOSED' in str(error):
            pytest.skip('External demo site is temporarily unavailable')
        raise
    browser.element('[data-testid=ClearIcon]').click()
    browser.element('[role=presentation]').perform(command.js.scroll_into_view)

    browser.element('[role=presentation]').perform(
        command.js.drop_file(resources.path('selenite.png'))
    )

    browser.element('[role=presentation]+*').all('.MuiTypography-body1').should(
        have.exact_texts('selenite.png')
    )
