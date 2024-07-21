import pytest

from selene import browser, have, be
from selene.support._pom import Element, All


class DataGridMIT:
    grid = Element('[role=grid]')
    headers = grid.All('[role=columnheader]')
    header = grid.Element('.MuiDataGrid-columnHeaders')
    toggle_all_checkbox = header.Element('.PrivateSwitchBase-input')
    '''
    # todo: support also the following:
    toggle_all = headers.ElementBy(have.attribute('data-field').value('__check__'))
    toggle_all_checkbox = toggle_all.Element('[type=checkbox]')
    '''

    footer = Element('.MuiDataGrid-footerContainer')
    selected_rows_count = footer.Element('.MuiDataGrid-selectedRowCount')
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
    characters.headers.should(have.size(6))
    characters.headers.should(
        have._exact_texts_like(
            {...}, 'ID', 'First name', 'Last name', 'Age', 'Full name'
        )
    )
    characters.pagination_rows_displayed.should(have.exact_text('1–5 of 9'))
    characters.page_to_right.click()
    characters.pagination_rows_displayed.should(have.exact_text('6–9 of 9'))
    characters.page_to_left.click()
    characters.pagination_rows_displayed.should(have.exact_text('1–5 of 9'))

    characters.selected_rows_count.should(be.not_.visible)
    characters.toggle_all_checkbox.should(be.not_.checked)
    characters.toggle_all_checkbox.click()
    characters.toggle_all_checkbox.should(be.checked)
    characters.selected_rows_count.should(have.exact_text('9 rows selected'))
    characters.toggle_all_checkbox.click()
    characters.toggle_all_checkbox.should(be.not_.checked)
    characters.selected_rows_count.should(be.not_.visible)
