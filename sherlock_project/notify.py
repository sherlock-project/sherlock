from sherlock_project.result import QueryStatus
from colorama import Fore, Style
import webbrowser

class QueryNotify:
    def __init__(self, result=None):
        self.result = result

    def start(self, message=None):
        pass

    def update(self, result):
        self.result = result

    def finish(self, message=None):
        pass

    def __str__(self):
        return str(self.result)


class QueryNotifyPrint(QueryNotify):
    def __init__(self, result=None, verbose=False, print_all=False, browse=False):
        super().__init__(result)
        self.verbose = verbose
        self.print_all = print_all
        self.browse = browse
        self.found_count = 0 

    def start(self, message):
        title = "Checking username"
        print(Style.BRIGHT + Fore.GREEN + "[" +
              Fore.YELLOW + "*" +
              Fore.GREEN + f"] {title}" +
              Fore.WHITE + f" {message}" +
              Fore.GREEN + " on:")
        print('\r')

    def update(self, result):
        self.result = result
        response_time_text = ""
        if self.result.query_time is not None and self.verbose is True:
            response_time_text = f" [{round(self.result.query_time * 1000)}ms]"

        if result.status == QueryStatus.CLAIMED:
            self.found_count += 1
            print(Style.BRIGHT + Fore.WHITE + "[" +
                  Fore.GREEN + "+" +
                  Fore.WHITE + "]" +
                  response_time_text +
                  Fore.GREEN +
                  f" {self.result.site_name}: " +
                  Style.RESET_ALL +
                  f"{self.result.site_url_user}")
            if self.browse:
                webbrowser.open(self.result.site_url_user, 2)

        elif result.status == QueryStatus.AVAILABLE:
            if self.print_all:
                print(Style.BRIGHT + Fore.WHITE + "[" +
                      Fore.RED + "-" +
                      Fore.WHITE + "]" +
                      response_time_text +
                      Fore.GREEN + f" {self.result.site_name}:" +
                      Fore.YELLOW + " Not Found!")

        elif result.status == QueryStatus.UNKNOWN:
            if self.print_all:
                print(Style.BRIGHT + Fore.WHITE + "[" +
                      Fore.RED + "-" +
                      Fore.WHITE + "]" +
                      Fore.GREEN + f" {self.result.site_name}:" +
                      Fore.RED + f" {self.result.context}" +
                      Fore.YELLOW + " ")

        elif result.status == QueryStatus.ILLEGAL:
            if self.print_all:
                msg = "Illegal Username Format For This Site!"
                print(Style.BRIGHT + Fore.WHITE + "[" +
                      Fore.RED + "-" +
                      Fore.WHITE + "]" +
                      Fore.GREEN + f" {self.result.site_name}:" +
                      Fore.YELLOW + f" {msg}")
                
        elif result.status == QueryStatus.WAF:
            if self.print_all:
                print(Style.BRIGHT + Fore.WHITE + "[" +
                      Fore.RED + "-" +
                      Fore.WHITE + "]" +
                      Fore.GREEN + f" {self.result.site_name}:" +
                      Fore.RED + " Blocked by bot detection" +
                      Fore.YELLOW + " (proxy may help)")
        else:
            raise ValueError(
                f"Unknown Query Status '{result.status}' for site '{self.result.site_name}'"
            )

    def finish(self, message=None):
        print(Style.BRIGHT + Fore.GREEN + "[" +
              Fore.YELLOW + "*" +
              Fore.GREEN + "] Search completed with" +
              Fore.WHITE + f" {self.found_count} " +
              Fore.GREEN + "results" + Style.RESET_ALL
              )

    def __str__(self):
        return str(self.result)
