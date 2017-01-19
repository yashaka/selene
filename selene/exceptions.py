class ConditionMismatchException(Exception):
    """
    """

    def __init__(self, message='condition did not match', expected=None, actual=None):
        super(ConditionMismatchException, self).__init__()
        self.message = message
        if expected is not None:
            self.message += '''
            \texpected: {}'''.format(expected)
        if actual is not None:
            self.message += '''
            \t  actual: {}'''.format(actual)
