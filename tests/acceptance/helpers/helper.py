from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager


def get_test_driver():
    return webdriver.Firefox()
