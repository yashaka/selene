import os

from selene import config
from selene.conditions import exact_url
from selene.tools import visit
from selene.tools import wait_to



def setup_module(m):
    config.browser_name = "chrome"

def test_can_wait_for_exact_url():
    start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'

    visit(start_page)
    wait_to(exact_url(start_page))
