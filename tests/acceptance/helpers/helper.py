from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver


def get_test_driver():
    return webdriver.Firefox(executable_path=GeckoDriverManager().install())
