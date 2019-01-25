from colorama import Fore, Style


class Log:
    def __init__(self, debug=False):  #
        """
        A logger object

        Parameters
        ----------
        debug, boolean, option, default = Flase
            Is the logger debugging the application.
        """
        self._debugging = debug
        self.locked = False

    @staticmethod
    def getLogger():
        """
        Get a SherlockLog object instance.

        Parameters
        ----------
        return : Sherlock.Log, return
            logger instance.
        """
        return Log()

    def lock(self):
        """
        Locks the logger to a single thread, use to lock the logger if using some particular data on a thread.
        Please ensure once your complete, call the unlock method.
        """
        while self.locked:
            pass
        self.locked = True

    def unlock(self):
        """
        Unlocks the logger, relinquishes resources to all threads.
        """
        self.locked = False

    def eprint(self, status: str, message: str, status_color: Fore = Fore.WHITE, status_frame: Fore = Fore.WHITE, message_color: Fore = Fore.WHITE, style: Style = Style.BRIGHT):
        """
        Prints a message to the screen using colorama,

        Parameters
        ----------
        status : str, option
            The status of the message.

        message : str, option
            The actual description of the error

        status_color : Fore, option, default = Fore.WHITE
            The color of the status.

        status_frame : Fore, option, default  = Fore.WHITE
            The color of the brackets that surround the status.

        message_color : Fore, option, default  = Fore.WHITE
            The message color.

        style : Style, option, default = Style.BRIGHT
            The brightness style of the whole message.


        """

        print(
            (
                style
                + status_frame
                + "["
                + status_color
                + "%s"
                + status_frame
                + "] "
                + message_color
                + "%s."
            )
            % (status, message)
        )

    def log(self, message: str):
        """
        General logging with no errors.

        Parameters
        ----------
        message : str
            The log message.
        """
        self.eprint(
            "*",
            message,
            status_color=Fore.WHITE,
            status_frame=Fore.GREEN,
            message_color=Fore.WHITE,
        )

    def error(self, message: str):
        """
        Error logging.

        Parameters
        ----------
        message : str
            The error message.
        """
        self.eprint(
            "-",
            message,
            status_color=Fore.RED,
            status_frame=Fore.WHITE,
            message_color=Fore.WHITE,
        )

    def info(self, message: str):
        """
        Info logging.

        Parameters
        ----------
        message : str
            The info message.
        """

        self.eprint(
            "+",
            message,
            status_color=Fore.GREEN,
            status_frame=Fore.WHITE,
            message_color=Fore.WHITE,
        )
