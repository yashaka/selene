import datetime
import sys

from selene import have
from selene.support.conditions.have import *  # noqa


def date(value: datetime.date):  # noqa
    """
    match date according to the project specific format
    """
    month_full_name = '%B'
    year_full = '%Y'

    is_unix_like = sys.platform in ('linux', 'linux2', 'darwin')
    day_without_leading_zero = '%-d' if is_unix_like else '%#d'
    hours_without_leading_zero = '%-I' if is_unix_like else '%#I'

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


'''
# Just another versions of implementation...


def date(value: datetime.date):  # noqa
    """
    match date according to the project specific format
    """
    month_full_name = '%B'
    year_full = '%Y'
    day_01_31 = '%d'
    hours_00_59 = '%I'
    minutes_00_59 = '%M'
    am_or_pm = '%p'

    return have.value(
        value.strftime(
            f'{month_full_name} '
            f'{day_01_31}, '
            f'{year_full} '
            f'{hours_00_59}:'
            f'{minutes_00_59} '
            f'{am_or_pm}'
        ).replace(' 0', ' ')
    )


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
'''
