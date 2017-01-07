from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


def get_test_driver():
    binary = FirefoxBinary("/home/sergey/Downloads/firefox/firefox")
    return webdriver.Firefox(firefox_binary=binary)
