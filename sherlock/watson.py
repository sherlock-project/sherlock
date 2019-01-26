#! /usr/bin/env python3

"""
Sherlock: Find Usernames Across Social Networks Module

This module contains helper methods for Sherlock.
"""

# ==================== Imports ==================== #
import requests
import itertools
import threading
import time
import sys
from colorama import Fore, Style
from requests_futures.sessions import FuturesSession


# ==================== Main ==================== #
class ElapsedFuturesSession(FuturesSession):
    """
    Extends FutureSession to add a response time metric to each request.

    This is taken (almost) directly from here: https://github.com/ross/requests-futures#working-in-the-background
    """

    def request(self, method, url, hooks={}, *args, **kwargs):
        start = time.time()

        def timing(r, *args, **kwargs):
            elapsed_sec = time.time() - start
            r.elapsed = round(elapsed_sec * 1000)

        try:
            if isinstance(hooks['response'], (list, tuple)):
                # needs to be first so we don't time other hooks execution
                hooks['response'].insert(0, timing)
            else:
                hooks['response'] = [timing, hooks['response']]
        except KeyError:
            hooks['response'] = timing

        return super(ElapsedFuturesSession, self).request(method, url, hooks=hooks, *args, **kwargs)


def open_file(fname):
    return open(fname, "a")


def write_to_file(url, f):
    f.write(url + "\n")


def print_error(err, errstr, var, verbose=False):
    global error_buf
    try:
        error_buf
    except NameError as e:
        error_buf = ''
    error_buf += Style.BRIGHT + Fore.WHITE + "[" + \
          Fore.RED + "-" + \
          Fore.WHITE + "]" + \
          Fore.RED + f" {errstr}" + \
          Fore.YELLOW + f" {err if verbose else var}" + '\n'


def dump_errors():
    global error_buf
    try:
        print(error_buf)
    except NameError as e:
        pass


def format_response_time(response_time, verbose):
    return " [{} ms]".format(response_time) if verbose else ""


def print_found(social_network, url, response_time, verbose=False):
    print((Style.BRIGHT + Fore.WHITE + "[" +
           Fore.GREEN + "+" +
           Fore.WHITE + "]" +
           format_response_time(response_time, verbose) +
           Fore.GREEN + " {}:").format(social_network), url)


def print_not_found(social_network, response_time, verbose=False):
    print((Style.BRIGHT + Fore.WHITE + "[" +
           Fore.RED + "-" +
           Fore.WHITE + "]" +
           format_response_time(response_time, verbose) +
           Fore.GREEN + " {}:" +
           Fore.YELLOW + " Not Found!").format(social_network))


def get_response(request_future, error_type, social_network, verbose=False):
    try:
        rsp = request_future.result()
        if rsp.status_code:
            return rsp, error_type, rsp.elapsed
    except requests.exceptions.HTTPError as errh:
        print_error(errh, "HTTP Error:", social_network, verbose)
    except requests.exceptions.ConnectionError as errc:
        print_error(errc, "Error Connecting:", social_network, verbose)
    except requests.exceptions.Timeout as errt:
        print_error(errt, "Timeout Error:", social_network, verbose)
    except requests.exceptions.RequestException as err:
        print_error(err, "Unknown error:", social_network, verbose)
    return None, "", -1


class Loader:
    def __init__(self):
        self.done = False

    def animate_loader(self):
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if self.done:
                break
            sys.stdout.write('\rloading ' + c)
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\rDone!     \n')


    def start_loader(self):
        self.thread = threading.Thread(target=Loader.animate_loader, args=(self,))
        self.thread.start()
        return self

    def stop_loader(self):
        self.done = True
        self.thread.join()
        return self

