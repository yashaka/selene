from selene.conditions import size
from selene.tools import *


def test_demo():
    visit("http://automation-remarks.com")
    ss(".post").should_have(size(9))


def test_demo_2():
    visit("http://automation-remarks.com")
    ss(".post").should_have(size(8))
