import pytest

from selene import browser, have
from selene.support._pom import Element, All


class DataGridMIT:
    grid = Element('[role=grid]')

    footer = Element('.MuiDataGrid-footerContainer')
    pagination = footer.Element('.MuiTablePagination-root')
    pagination_rows_displayed = pagination.Element('.MuiTablePagination-displayedRows')
    page_to_right = pagination.Element('[data-testid=KeyboardArrowRightIcon]')
    page_to_left = pagination.Element('[data-testid=KeyboardArrowLeftIcon]')

    def __init__(self, context):
        self.context = context


@pytest.mark.parametrize(
    'characters',
    [
        DataGridMIT(browser.element('#DataGridDemo+* .MuiDataGrid-root')),
        # DataGridMIT.by_id('demo-simple-select'),
    ],
)
def test_material_ui__react_x_data_grid_mit(characters):
    browser.driver.refresh()

    # WHEN
    browser.open('https://mui.com/x/react-data-grid/#DataGridDemo')

    # THEN
    characters.pagination_rows_displayed.should(have.exact_text('1–5 of 9'))
    characters.page_to_right.click()
    characters.pagination_rows_displayed.should(have.exact_text('6–9 of 9'))
    characters.page_to_left.click()
    characters.pagination_rows_displayed.should(have.exact_text('1–5 of 9'))
    characters.footer.should(have.text('1–5 of 9'))
