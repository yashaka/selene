from selene.conditions import size
from selene.tools import visit, ss


def test_demo_3():
    visit("http://automation-remarks.com")
    ss(".post").should_have(size(9))


def test_demo_4():
    visit("http://automation-remarks.com")
    ss(".post").should_have(size(8))
