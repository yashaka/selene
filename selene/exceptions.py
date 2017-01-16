class ConditionMismatchException(Exception):
    """
    """

    def __init__(self, message='condition did not match', expected='', actual=''):
        super(ConditionMismatchException, self).__init__()
        self.message = message
        if expected:
            self.message += '''
            \texpected: {}'''.format(expected)
        if actual:
            self.message += '''
            \t  actual: {}'''.format(actual)
