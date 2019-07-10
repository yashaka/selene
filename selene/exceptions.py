class ConditionMismatchException(Exception):
    """
    """

    def __init__(self, message='condition did not match', expected=None, actual=None):
        msg = message
        if expected is not None:
            msg += '''
            \texpected: {}'''.format(expected)
        if actual is not None:
            msg += '''
            \t  actual: {}'''.format(actual)
        super(ConditionMismatchException, self).__init__(msg)
