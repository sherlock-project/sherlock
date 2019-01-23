class SLException(Exception):
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

    def get_message(self):
        """
        The exception message associated with the SLException object

        Parameters
        ----------
        return : str, return
            The message of the SLException object.
        """
        return self.message