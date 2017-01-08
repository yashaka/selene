from selenium.common.exceptions import WebDriverException


class ConditionMismatch(WebDriverException):
    """
    """
    def __str__(self):
        return 'Condition Mismatch'
