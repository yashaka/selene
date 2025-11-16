from selene import have, be
import selene


def test_remove_row_v1():
    """
    use collection.element_by(condition)
    to filter proper row to find action element inside
    """
    # Arrange - Setup
    browser = selene.browser.with_(window_width=1400)
    browser.open('https://demoqa.com/webtables')
    fired_employee_email = 'alden@example.com'
    rows = browser.all('.rt-tbody [role=row]').by(have.no.exact_text(''))
    rows.should(have.size(3))
    
    # Act - Delete the row with specified employee
    rows.element_by(have.text(fired_employee_email)).element(
        '[id^=delete-record]'
    ).click()
    
    # Assert - Verify row is removed
    rows.should(have.size(2))
    rows.should(have.no.text(fired_employee_email).each)


def test_remove_row_v2():
    """
    use collection.element_by(more_precise_lambda_condition)
    to filter proper row to find action element inside
    """
    # Arrange - Setup
    browser = selene.browser.with_(window_width=1400)
    browser.open('https://demoqa.com/webtables')
    fired_employee_email = 'alden@example.com'
    rows = browser.all('.rt-tbody [role=row]').by(have.no.exact_text(''))
    rows.should(have.size(3))
    
    # Act - Delete the row using lambda condition for precise matching
    rows.element_by(
        lambda its: have.exact_text(fired_employee_email)(
            its.element('[role=gridcell]:nth-of-type(4)')
        )
    ).element('[id^=delete-record]').click()
    
    # Assert - Verify row is removed
    rows.should(have.size(2))
    rows.should(have.no.text(fired_employee_email).each)


def test_remove_row_v3():
    """
    use collection.element_by_its(selector, more_precise_condition)
    to filter proper row to find action element inside

    element_by_its is a shortcut to same receipt from v2
    """
    # Arrange - Setup
    browser = selene.browser.with_(window_width=1400)
    browser.open('https://demoqa.com/webtables')
    fired_employee_email = 'alden@example.com'
    rows = browser.all('.rt-tbody [role=row]').by(have.no.exact_text(''))
    rows.should(have.size(3))
    
    # Act - Delete the row using element_by_its shortcut
    rows.element_by_its(
        '[role=gridcell]:nth-of-type(4)', have.exact_text(fired_employee_email)
    ).element('[id^=delete-record]').click()
    
    # Assert - Verify row is removed
    rows.should(have.size(2))
    rows.should(have.no.text(fired_employee_email).each)
