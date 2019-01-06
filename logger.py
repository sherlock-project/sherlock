from colorama import Back, Fore, Style, init


class Logger:
    def __init__(self, debug=False):
        init(autoreset=True)
        self.debug = debug

    def info(self, text, additional=""):
        if self.debug:
            print((Style.BRIGHT + Fore.GREEN + "[" +
                   Fore.YELLOW + "*" +
                   Fore.GREEN + f"] {text}:" +
                   Fore.WHITE + f" {additional}"))

    def fine(self, text, additional=""):
        print((Style.BRIGHT + Fore.WHITE + "[" +
               Fore.GREEN + "+" +
               Fore.WHITE + "]" +
               Fore.GREEN + f" {text}: {additional}"))

    def warn(self, text, additional=""):
        print((Style.BRIGHT + Fore.WHITE + "[" +
               Fore.RED + "!" +
               Fore.WHITE + "]" +
               Fore.GREEN + f" {text}:" +
               Fore.YELLOW + f" {additional}"))

    def error(self, text, exception=""):
        print(Style.BRIGHT + Fore.WHITE + "[" +
              Fore.RED + "-" +
              Fore.WHITE + "]" +
              Fore.RED + f" {text}" +
              Fore.YELLOW + f" {exception}")
