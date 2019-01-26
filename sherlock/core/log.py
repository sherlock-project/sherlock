import os, tempfile
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style


class Log:
    def __init__(self, filename="log.txt", verbose=False, warninglevel=0):  #
        """
        A logger object.  This logs occupancies during the execution.

        Parameters
        ----------
        filename : str, option, default = "log"
            The filename of the log.

        verbose : boolean, option, default = False
            Is the log visible

        warninglevel : int option, default = 0
            What levels of messages are stored.
            level = 0 -> log, info, error.
            level = 1 -> info, error.
            level = 2 -> error.

        """
        self._loglevel = warninglevel
        self._filename = filename
        self._verbose = verbose
        self.locked = False

    @staticmethod
    def getLogger(name="log", verbose=True, replaced=True, warninglevel=0):
        """
        Get a SherlockLog object instance.

        Parameters
        ----------

        name : str, option, default = "log"
            The log to get

        verbose : boolean, option, default = False
            Is the log visible

        warninglevel : int option, default = 0
            What levels of messages are stored.
            level = 0 -> log, info, error.
            level = 1 -> info, error.
            level = 2 -> error.

        return : Sherlock.Log, return
            logger instance.
        """

        tmppath = "%s/%s%s" % (tempfile.gettempdir(), name, ".txt")
        if os.path.exists(tmppath) and replaced:
            with open(tmppath, "w") as w:
                w.write("### LOG %s SHERLOCK ###" % name)
                w.write("Time and Date Created: %s\n" % datetime.now())

        return Log(filename=tmppath, verbose=verbose, warninglevel=warninglevel)

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

    def eprint(
        self,
        status: str,
        message: str,
        store: bool = False,
        status_color: Fore = Fore.WHITE,
        status_frame: Fore = Fore.WHITE,
        message_color: Fore = Fore.WHITE,
        style: Style = Style.BRIGHT,
    ):
        """
        Prints a message to the screen using colorama,

        Parameters
        ----------
        status : str
            The status of the message.

        message : str
            The actual description of the message

        store : bool, option, default = False
            Should the message be logged.

        status_color : Fore, option, default = Fore.WHITE
            The color of the status.

        status_frame : Fore, option, default  = Fore.WHITE
            The color of the brackets that surround the status.

        message_color : Fore, option, default  = Fore.WHITE
            The message color.

        style : Style, option, default = Style.BRIGHT
            The brightness style of the whole message.


        """

        if self._verbose:
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
                    + "%s.\n"
                )
                % (status, message)
            )

        if store:
            with open(self._filename, "w") as f:
                f.write(
                    (+"%s [" + "%s" + "] " + "%s.") % (datetime.now(), status, message)
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
            store=self._loglevel >= 0,
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
            store=self._loglevel >= 2,
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
            store=self._loglevel >= 1,
            status_color=Fore.GREEN,
            status_frame=Fore.WHITE,
            message_color=Fore.WHITE,
        )
