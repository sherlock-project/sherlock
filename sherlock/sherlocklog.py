from colorama import Back, Fore, Style, init

class SherlockLog:
    def __init__(self,
        debug=False):
        self.locked = False

    @staticmethod
    def getLogger():
        """
            Get a SherlockLog object instance.
            Return: (SherlockLog); SherlockLog instance.
        """
        return SherlockLog()

    def lock(self):
        while self.locked:
            pass
        self.locked = True

    def unlock(self):
        self.locked = False

    def eprint(self, 
        status: str,
        message:str,
        status_color: Fore=Fore.WHITE,
        status_frame: Fore=Fore.WHITE,
        message_color: Fore=Fore.WHITE,
        style: Style =Style.BRIGHT):
        
        """
            Prints a message to the screen using colorama,
            
            Required Parameters:
                status: (str);  The status of the message.
                message: (str); The actual description of the error
            
            
        """
        
        print(  (style + 
                status_frame + "[" +
                status_color + "%s" +
                status_frame + "] "+
                message_color +"%s.") % (status, message))
    
    def log(self,
        message: str):
        """
            General logging with no errors.
            Required Parameters:
                message: (str);  The log message.
        """
        self.eprint(
            "*", 
            message,
            status_color=Fore.WHITE,
            status_frame=Fore.GREEN,
            message_color=Fore.WHITE)
          
    def error(self,
        message: str):
        """
            Error logging.
            Required Parameters:
                message: (str);  The error message.
        """
        self.eprint(
            "-", 
            message,
            status_color=Fore.RED,
            status_frame=Fore.WHITE,
            message_color=Fore.WHITE)

    def info(self,
        message: str):
        
        """
            Info logging.
            Required Parameters:
                message: (str);  The info message.
        """
        
        self.eprint(
            "+", 
            message,
            status_color=Fore.GREEN,
            status_frame=Fore.WHITE,
            message_color=Fore.WHITE)

