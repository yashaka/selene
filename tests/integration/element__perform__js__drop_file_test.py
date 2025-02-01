from selene import command, have
from tests import resources
from tests.integration.helpers.givenpage import GivenPage


def x_test_drops_file_to_self(session_browser):
    browser = session_browser.with_(timeout=2)
    page = GivenPage(browser.driver)
    page.opened_empty()
    page.add_style_to_head(
        """
        TODO: implement this
        """
    )
    page.add_script_to_head(
        """
        TODO: implement this
        """
    )
    page.load_body(
        '''
        TODO: implement this
        '''
    )

    # TODO: implement


# todo: find an alternative web page to test this
def x_test_drops_file_to_self_in_react_mui(session_browser):
    browser = session_browser
    browser.open('https://app.qa.guru/automation-practice-form/')
    browser.element('[data-testid=ClearIcon]').click()
    browser.element('[role=presentation]').perform(command.js.scroll_into_view)

    browser.element('[role=presentation]').drop_file(resources.path('selenite.png'))

    browser.element('[role=presentation]+*').all('.MuiTypography-body1').should(
        have.exact_texts('selenite.png')
    )
