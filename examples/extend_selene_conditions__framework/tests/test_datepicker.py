import datetime
from examples.extend_selene_conditions__framework.demoqa_tests.extensions.selene import (
    have,
)
from selene.support.shared import browser


def test_date_and_time_control():
    browser.open('/date-picker')

    browser.element('#dateAndTimePickerInput').should(
        have.date(datetime.datetime.now())
    )
