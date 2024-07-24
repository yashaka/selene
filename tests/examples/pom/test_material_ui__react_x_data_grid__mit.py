import re
import logging

import pytest

import selene
from selene import have, be, command, query, support
from selene.support._pom import element, all_
from selene.common.helpers import _HTML_TAGS


class DataGridMIT:
    grid = element('role=grid')

    header = grid.element('.MuiDataGrid-columnHeaders')
    toggle_all_checkbox = header.element('.PrivateSwitchBase-input')
    '''
    # todo: support also the following:
    toggle_all = headers.ElementBy(have.attribute('data-field').value('__check__'))
    toggle_all_checkbox = toggle_all.Element('[type=checkbox]')
    '''
    column_headers = grid.all('role=columnheader')

    footer = element('.MuiDataGrid-footerContainer')
    selected_rows_count = footer.element('.MuiDataGrid-selectedRowCount')
    pagination = footer.element('.MuiTablePagination-root')
    pagination_rows_displayed = pagination.element('.MuiTablePagination-displayedRows')
    page_to_right = pagination.element('KeyboardArrowRightIcon')
    page_to_left = pagination.element('KeyboardArrowLeftIcon')

    content = grid.element('role=rowgroup')
    rows = content.all('role=row')
    _cells_selector = 'role=gridcell'
    cells = content.all(_cells_selector)
    editing_cell_input = content.element('.MuiDataGrid-cell--editing').element('input')

    def __init__(self, context: selene.Element):
        self.context = context

    # @all_  # todo: make it or @all_.by or etc. work (maybe @all_.named)
    def cells_of_row(self, number, /):
        return self.rows[number - 1].all(self._cells_selector)

    # todo: support int for column
    # @element  # todo: make it or @element.by or etc. work (maybe @element.named)
    def cell(self, *, row, column_data_field=None, column=None):
        if column:
            column_data_field = self.column_headers.element_by(
                have.exact_text(column)
            ).get(query.attribute('data-field'))

        return self.cells_of_row(row).element_by(
            have.attribute('data-field').value(column_data_field)
        )

    # @step  # todo make it work
    def set_cell(self, *, row, column_data_field=None, column=None, to_text):
        self.cell(
            row=row, column_data_field=column_data_field, column=column
        ).double_click()
        self.editing_cell_input.perform(command.select_all).type(to_text).press_enter()


class StringHandler(logging.Handler):
    terminator = '\n'

    def __init__(self):
        logging.Handler.__init__(self)
        self.stream = ''

    def emit(self, record):
        try:
            msg = self.format(record)
            # issue 35046: merged two stream.writes into one.
            self.stream += msg + self.terminator
        except Exception:
            self.handleError(record)


log = logging.getLogger(__file__)
log.setLevel(20)
handler = StringHandler()
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)


class LogToStringStreamContext:
    def __init__(self, title, params):
        self.title = title
        self.params = params

    def __enter__(self):
        log.info('%s', self.title)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # log.info('%s: PASSED', self.title)
            pass
        else:
            log.info('\n\n%s\n%s', exc_type, exc_val)


@pytest.fixture(scope='function')
def browser():
    selene.browser.driver.refresh()

    yield selene.browser.with_(
        timeout=2.0,
        _wait_decorator=support._logging.wait_with(
            context=LogToStringStreamContext,  # noqa
            # in real life could be:
            # context=allure_commons._allure.StepContext
        ),
        selector_to_by_strategy=lambda selector: (
            # wrap into default strategy
            selene.browser.config.selector_to_by_strategy(
                # detected testid
                f'[data-testid={selector}]'
                if re.match(
                    # word_with_dashes_underscores_or_numbers
                    r'^[a-zA-Z_\d\-]+$',
                    selector,
                )
                and selector not in _HTML_TAGS
                else (
                    # detected attribute=value
                    f'[{match.group(1)}="{match.group(2)}"]'
                    if (
                        match := re.match(
                            # word_with_dashes_underscores_or_numbers=*
                            r'^([a-zA-Z_\d\-]+)=(.*)$',
                            selector,
                        )
                    )
                    else selector
                )
            )
        ),
    )


def test_material_ui__react_x_data_grid_mit(browser):
    # WHEN
    browser.open('https://mui.com/x/react-data-grid/#DataGridDemo')
    characters = DataGridMIT(browser.element('#DataGridDemo+* .MuiDataGrid-root'))

    # THEN
    # - check headers
    characters.column_headers.should(have.size(6))
    characters.column_headers.should(
        have._exact_texts_like(
            {...}, 'ID', 'First name', 'Last name', 'Age', 'Full name'
        )
    )

    # - pagination works
    characters.pagination_rows_displayed.should(have.exact_text('1–5 of 9'))
    characters.page_to_right.click()
    characters.pagination_rows_displayed.should(have.exact_text('6–9 of 9'))
    characters.page_to_left.click()
    characters.pagination_rows_displayed.should(have.exact_text('1–5 of 9'))

    # - toggle all works to select all rows
    characters.selected_rows_count.should(be.not_.visible)
    characters.toggle_all_checkbox.should(be.not_.checked)
    characters.toggle_all_checkbox.click()
    characters.toggle_all_checkbox.should(be.checked)
    characters.selected_rows_count.should(have.exact_text('9 rows selected'))
    characters.toggle_all_checkbox.click()
    characters.toggle_all_checkbox.should(be.not_.checked)
    characters.selected_rows_count.should(be.not_.visible)

    # - check rows
    characters.rows.should(have.size(5))
    characters.cells_of_row(1).should(
        have._exact_texts_like({...}, {...}, 'Jon', 'Snow', '14', 'Jon Snow')
    )

    # - sorting works
    # TODO: implement

    # - filtering works
    # TODO: implement

    # - hiding works
    # TODO: implement

    # - a cell can be edited
    characters.set_cell(row=1, column_data_field='firstName', to_text='John')
    characters.cells_of_row(1).should(
        have._exact_texts_like({...}, {...}, 'John', 'Snow', '14', 'John Snow')
    )
    characters.set_cell(row=1, column='First name', to_text='Jon')
    characters.cells_of_row(1).should(
        have._exact_texts_like({...}, {...}, 'Jon', 'Snow', '14', 'Jon Snow')
    )

    # - check logging on failed
    try:
        characters.cells_of_row(1).with_(timeout=0.1).should(
            have._exact_texts_like({...}, {...}, 'John', 'Snow', '14', 'John Snow')
        )
        pytest.fail('should have failed on texts mismatch')
    except AssertionError:
        # THEN everything is logged:
        assert (
            'column_headers: should have size 6\n'
            'column_headers: should have exact texts like:\n'
            '    {...}, ID, First name, Last name, Age, Full name\n'
            "pagination_rows_displayed: should have exact text '1–5 of 9'\n"
            'page_to_right: click\n'
            "pagination_rows_displayed: should have exact text '6–9 of 9'\n"
            'page_to_left: click\n'
            "pagination_rows_displayed: should have exact text '1–5 of 9'\n"
            'selected_rows_count: should be not (visible)\n'
            "toggle_all_checkbox: should have no (native property 'checked' with value "
            "'True')\n"
            'toggle_all_checkbox: click\n'
            "toggle_all_checkbox: should have native property 'checked' with value "
            "'True'\n"
            "selected_rows_count: should have exact text '9 rows selected'\n"
            'toggle_all_checkbox: click\n'
            "toggle_all_checkbox: should have no (native property 'checked' with value "
            "'True')\n"
            'selected_rows_count: should be not (visible)\n'
            'rows: should have size 5\n'
            ''
            'element(\'#DataGridDemo+* .MuiDataGrid-root\').element(\'[role="grid"]\')'
            '.element(\'[role="rowgroup"]\').all(\'[role="row"]\')[0].all(\'[role="gridcell"]\'): '
            'should have exact texts like:\n'
            '    {...}, {...}, Jon, Snow, 14, Jon Snow\n'
            ''
            'element(\'#DataGridDemo+* .MuiDataGrid-root\').element(\'[role="grid"]\')'
            '.element(\'[role="rowgroup"]\').all(\'[role="row"]\')[0].all(\'[role="gridcell"]\').element_by(has '
            "attribute 'data-field' with value 'firstName'): double click\n"
            ''
            'editing_cell_input: send «select all» keys shortcut as ctrl+a or cmd+a for '
            'mac\n'
            'editing_cell_input: type: John\n'
            'editing_cell_input: press keys: ENTER\n'
            ''
            'element(\'#DataGridDemo+* .MuiDataGrid-root\').element(\'[role="grid"]\')'
            '.element(\'[role="rowgroup"]\').all(\'[role="row"]\')[0].all(\'[role="gridcell"]\'): '
            'should have exact texts like:\n'
            '    {...}, {...}, John, Snow, 14, John Snow\n'
            ''
            'element(\'#DataGridDemo+* .MuiDataGrid-root\').element(\'[role="grid"]\')'
            '.element(\'[role="rowgroup"]\').all(\'[role="row"]\')[0].all(\'[role="gridcell"]\').element_by(has '
            "attribute 'data-field' with value 'firstName'): double click\n"
            ''
            'editing_cell_input: send «select all» keys shortcut as ctrl+a or cmd+a for '
            'mac\n'
            'editing_cell_input: type: Jon\n'
            'editing_cell_input: press keys: ENTER\n'
            ''
            'element(\'#DataGridDemo+* .MuiDataGrid-root\').element(\'[role="grid"]\')'
            '.element(\'[role="rowgroup"]\').all(\'[role="row"]\')[0].all(\'[role="gridcell"]\'): '
            'should have exact texts like:\n'
            '    {...}, {...}, Jon, Snow, 14, Jon Snow\n'
            ''
            'element(\'#DataGridDemo+* .MuiDataGrid-root\').element(\'[role="grid"]\')'
            '.element(\'[role="rowgroup"]\').all(\'[role="row"]\')[0].all(\'[role="gridcell"]\'): '
            'should have exact texts like:\n'
            '    {...}, {...}, John, Snow, 14, John Snow\n'
            '\n'
            '\n'
            "<class 'selene.core.exceptions.TimeoutException'>\n"
            'Message: \n'
            '\n'
            'Timed out after 0.1s, while waiting for:\n'
            "browser.element(('css selector', '#DataGridDemo+* "
            ".MuiDataGrid-root')).element(('css selector', "
            '\'[role="grid"]\')).element((\'css selector\', '
            '\'[role="rowgroup"]\')).all((\'css selector\', '
            '\'[role="row"]\'))[0].all((\'css selector\', \'[role="gridcell"]\')).have '
            'exact texts like:\n'
            '    {...}, {...}, John, Snow, 14, John Snow\n'
            '\n'
            'Reason: AssertionError: actual visible texts:\n'
            '    , 1, Jon, Snow, 14, Jon Snow\n'
            '\n'
            'Pattern used for matching:\n'
            '    ^[^‚]+‚[^‚]+‚John‚Snow‚14‚John\\ Snow‚$\n'
            'Actual text used to match:\n'
            '    ‹EMTPY_STRING›‚1‚Jon‚Snow‚14‚Jon Snow‚\n'
            'Screenshot: '
            # 'file:///Users/yashaka/.selene/screenshots/1721780210612/1721780210612.png\n'
            # 'PageSource: '
            # 'file:///Users/yashaka/.selene/screenshots/1721780210612/1721780210612.html\n'
            # '\n'
        ) in handler.stream
