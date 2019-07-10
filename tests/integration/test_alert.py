import os

from selene import config
from selene.browser import open_url, driver
from selene.browsers import BrowserName
from selene.support.jquery_style_selectors import s

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


# todo: ensure works and enabled
def x_test_can_accept_alert():
    open_url(start_page)
    s("#alert_btn").click()
    driver().switch_to.alert.accept()


def x_test_can_dismiss_confirm_dialog():
    open_url(start_page)
    s("#alert_btn").click()
    driver().switch_to.alert.dismiss()
