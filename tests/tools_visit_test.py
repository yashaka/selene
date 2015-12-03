from selene import config
from selene.tools import set_driver, get_driver, visit

HOST = 'selene.com'


class Driver:
    def get(self, url):
        return url

    def quit(self):
        pass


def setup_module():
    set_driver(Driver())
    config.app_host = HOST


def teardown_module(m):
    get_driver().quit()
    config.app_host = ''


def test_visit_without_params():
    assert visit() == HOST


def test_visit_with_relative_url_without_slash_at_the_beginning():
    assert visit("order") == HOST + "/order"


def test_visit_with_relative_url_with_slash_at_the_beginning():
    assert visit("/order") == HOST + "/order"


def test_visit_with_absolute_url():
    url = "absolute.com"
    assert visit(url, False) == url
