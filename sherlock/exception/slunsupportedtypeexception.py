from sherlock.exception.slexception import SLException


class SLUnsupportedTypeException(SLException):
    """
        SLUnsupportedTypeException, a type format wasn't supported
    """

    def __init__(self, message):
        super(SLUnsupportedTypeException).__init__(message)