
class SLException (Exception):
    """
        SherlockException, to alert the user of any issues.
    """

    def __init__(self, message):
        """
        Initialises a new SherlockException

        Parameters
        ----------
        message : str
            The error message
        """
        self._message = message

    @property
    def message(self):
        return self._message


class SLUnsupportedTypeException (SLException):
    """
        SLUnsupportedTypeException, a type format wasn't supported
    """

    def __init__(self, message):
        super(SLUnsupportedTypeException).__init__(message)
