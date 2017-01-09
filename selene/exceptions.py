from selenium.common.exceptions import WebDriverException


class ConditionMismatchException(Exception):
    """
    """

    def __init__(self, message='condition did not match'):
        super(ConditionMismatchException, self).__init__()
        self.message = message
