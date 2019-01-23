from sherlock.exception.slexception import SLException


class SLUnsupportedTypeException(SLException):
    """
        SLUnsupportedTypeException, a type format wasn't supported
    """

    def __init__(self, message):
        """
        The exception message associated with the SLException object

        Parameters
        ----------
        return : str, return
            The message of the SLException object.
        """
        super(SLUnsupportedTypeException).__init__(message)