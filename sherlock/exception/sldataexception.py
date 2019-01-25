from sherlock.exception import SLException
class SLDataException(SLException):
    def __init__(self, message):
        """
        Exception that occured within class sherlock.core.Data

        Parameters
        ----------
        message : str
            The SLDataException message.

        """
        super(SLDataException).__init__(message)