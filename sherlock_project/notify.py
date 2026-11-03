"""Sherlock Notify Module

This module defines the objects for notifying the caller about the
results of queries.
"""
from sherlock_project.result import QueryStatus
from colorama import Fore, Style
import webbrowser

# Global variable to count the number of results.
globvar = 0


class QueryNotify:
    """Query Notify Object.

    Base class that describes methods available to notify the results of
    a query.
    It is intended that other classes inherit from this base class and
    override the methods to implement specific functionality.
    """

    def __init__(self, result=None):
        """Create Query Notify Object.

        Contains information about a specific method of notifying the results
        of a query.

        Keyword Arguments:
        self                   -- This object.
        result                 -- Object of type QueryResult() containing
                                  results for this query.

        Return Value:
        Nothing.
        """

        self.result = result


    def start(self, message=None):
        """Notify Start.

        Notify method for start of query.  This method will be called before
        any queries are performed.  This method will typically be
        overridden by higher level classes that will inherit from it.

        Keyword Arguments:
        self                   -- This object.
        message                -- Object that is used to give context to start
                                  of query.
                                  Default is None.

        Return Value:
        Nothing.
        """


    def update(self, result):
        """Notify Update.

        Notify method for query result.  This method will typically be
        overridden by higher level classes that will inherit from it.

        Keyword Arguments:
        self                   -- This object.
        result                 -- Object of type QueryResult() containing
                                  results for this query.

        Return Value:
        Nothing.
        """

        self.result = result


    def finish(self, message=None):
        """Notify Finish.

        Notify method for finish of query.  This method will be called after
        all queries have been performed.  This method will typically be
        overridden by higher level classes that will inherit from it.

        Keyword Arguments:
        self                   -- This object.
        message                -- Object that is used to give context to start
                                  of query.
                                  Default is None.

        Return Value:
        Nothing.
        """


    def __str__(self):
        """Convert Object To String.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nicely formatted string to get information about this object.
        """
        return str(self.result)


class QueryNotifyPrint(QueryNotify):
    """Query Notify Print Object.

    Query notify class that prints results.
    """

    def __init__(self, result=None, verbose=False, print_all=False, browse=False, include_nsfw=False):
        """Create Query Notify Print Object.

        Contains information about a specific method of notifying the results
        of a query.

        Keyword Arguments:
        self                   -- This object.
        result                 -- Object of type QueryResult() containing
                                  results for this query.
        verbose                -- Boolean indicating whether to give verbose output.
        print_all              -- Boolean indicating whether to only print all sites, including not found.
        browse                 -- Boolean indicating whether to open found sites in a web browser.
        include_nsfw           -- Boolean indicating whether NSFW sites are included.

        Return Value:
        Nothing.
        """

        super().__init__(result)
        self.verbose = verbose
        self.print_all = print_all
        self.browse = browse
        self.include_nsfw = include_nsfw
        self.regular_count = 0
        self.nsfw_count = 0


    def start(self, message):
        """Notify Start.

        Will print the title to the standard output.

        Keyword Arguments:
        self                   -- This object.
        message                -- String containing username that the series
                                  of queries are about.

        Return Value:
        Nothing.
        """

        mode_str = "NSFW Included" if self.include_nsfw else "Standard Search"

        print(Style.BRIGHT + Fore.CYAN + "+-----------------------------------------------------------+")
        print(Style.BRIGHT + Fore.CYAN + f"| Sherlock OSINT Search for: {Fore.YELLOW}{message:<30}{Fore.CYAN} |")
        print(Style.BRIGHT + Fore.CYAN + f"| Mode: {Fore.GREEN}{mode_str:<51}{Fore.CYAN} |")
        print(Style.BRIGHT + Fore.CYAN + "+-----------------------------------------------------------+\n")


    def countResults(self):
        """This function counts the number of results. Every time the function is called,
        the number of results is increasing.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        The number of results by the time we call the function.
        """
        global globvar
        globvar += 1
        return globvar

    def update(self, result):
        """Notify Update.

        Will print the query result to the standard output.

        Keyword Arguments:
        self                   -- This object.
        result                 -- Object of type QueryResult() containing
                                  results for this query.

        Return Value:
        Nothing.
        """
        self.result = result

        response_time_text = ""
        if self.result.query_time is not None and self.verbose is True:
            response_time_text = f" [{round(self.result.query_time * 1000)}ms]"

        # Output to the terminal is desired.
        if result.status == QueryStatus.CLAIMED:
            self.countResults()
            is_nsfw = getattr(self.result, "is_nsfw", False)
            if is_nsfw:
                self.nsfw_count += 1
                prefix = f"  |- {Fore.MAGENTA}[NSFW 18+]{Fore.GREEN}"
            else:
                self.regular_count += 1
                prefix = f"  |- {Fore.GREEN}[+]"

            print(Style.BRIGHT + prefix + response_time_text +
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
            # It should be impossible to ever get here...
            raise ValueError(
                f"Unknown Query Status '{result.status}' for site '{self.result.site_name}'"
            )


    def finish(self, message="The processing has been finished."):
        """Notify Finish.
        Will print the last line to the standard output.
        Keyword Arguments:
        self                   -- This object.
        message                -- The 2 last phrases.
        Return Value:
        Nothing.
        """
        total_found = self.regular_count + self.nsfw_count

        print(Style.BRIGHT + Fore.CYAN + "\n===========================================================")
        print(Style.BRIGHT + Fore.CYAN + "SUMMARY REPORT:")
        print(Style.BRIGHT + Fore.WHITE + f"   * Total Accounts Found : {total_found} ({self.regular_count} Regular | {self.nsfw_count} NSFW)")
        print(Style.BRIGHT + Fore.CYAN + "===========================================================" + Style.RESET_ALL)

        print("\nGo deeper than a username. Explore public profiles and export your findings.")
        print("Try OSINTSearch: \033]8;;https://osintsearch.org/go/sherlock\033\\https://osintsearch.org\033]8;;\033\\")

    def __str__(self):
        """Convert Object To String.

        Keyword Arguments:
        self                   -- This object.

        Return Value:
        Nicely formatted string to get information about this object.
        """
        return str(self.result)
