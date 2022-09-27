import datetime

from selene import have
from selene.support.conditions.have import *  # noqa


def date(value: datetime.date):  # noqa
    """
    match date according to the project specific format
    """
    month_full_name = '%B'
    year_full = '%Y'
    day_without_leading_zero = str(int(value.strftime('%d')))
    hours_without_leading_zero = str(int(value.strftime('%I')))
    minutes_00_59 = '%M'
    am_or_pm = '%p'

    return have.value(
        value.strftime(
            f'{month_full_name} '
            f'{day_without_leading_zero}, '
            f'{year_full} '
            f'{hours_without_leading_zero}:'
            f'{minutes_00_59} '
            f'{am_or_pm}'
        )
    )
