from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession
import json
import os

raw = open("data.json", "r")
data = json.load(raw)

# Allow 1 thread for each external service, so `len(data)` threads total
session = FuturesSession(executor=ThreadPoolExecutor(max_workers=len(data)))


def write_to_file(url, fname):
    with open(fname, "a") as f:
        f.write(url + "\n")


def main():
    # Not sure why, but the banner messes up if i put into one print function
    print("                                              .\"\"\"-.")
    print("                                             /      \\")
    print("\033[37;1m ____  _               _            _        |  _..--'-.")
    print("\033[37;1m/ ___|| |__   ___ _ __| | ___   ___| |__    >.`__.-\"\"\;\"`")
    print("\033[37;1m\___ \| '_ \ / _ \ '__| |/ _ \ / __| |/ /   / /(     ^\\")
    print("\033[37;1m ___) | | | |  __/ |  | | (_) | (__|   <    '-`)     =|-.")
    print("\033[37;1m|____/|_| |_|\___|_|  |_|\___/ \___|_|\_\    /`--.'--'   \ .-.")
    print("\033[37;1m                                           .'`-._ `.\    | J /")
    print("\033[37;1m                                          /      `--.|   \__/\033[0m")

    username = input("\033[92;1m[\033[37;1m?\033[92;1m]\033[92;1m Input Username: \033[0m")
    print()

    fname = username + ".txt"

    if os.path.isfile(fname):
        os.remove(fname)
        print(
            "\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Removing previous file:\033[1;37m {}\033[0m".format(fname))

    print(
        "\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Checking username\033[0m\033[1;37m {}\033[0m\033[1;92m on: "
        "\033[0m".format(
            username))

    # User agent is needed because some sites does not 
    # return the correct information because it thinks that
    # we are bot
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0'
    }

    # Create futures for all requests
    for social_network in data:
        url = data[social_network]['url'].format(username)

        # This future starts running the request in a new thread, doesn't block the main thread
        future = session.get(url=url, headers=headers)

        # Store future in data for access later
        data[social_network]['request'] = future

    # Print results
    for social_network in data:

        url = data[social_network]['url'].format(username)
        error_type = data[social_network]['errorType']

        # Retrieve future and ensure it has finished
        future = data[social_network]['request']
        response = future.result()

        # Print result
        if error_type == "message":
            error = data[social_network]['errorMsg']

            if not error in response.text:
                print("\033[37;1m[\033[92;1m+\033[37;1m]\033[92;1m {}:\033[0m".format(social_network), url)
                write_to_file(url, fname)

            else:
                print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Not Found!".format(social_network))

        elif error_type == "status_code":

            if not response.status_code == 404:
                print("\033[37;1m[\033[92;1m+\033[37;1m]\033[92;1m {}:\033[0m".format(social_network), url)
                write_to_file(url, fname)

            else:
                print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Not Found!".format(social_network))

        elif error_type == "response_url":
            error = data.get(social_network).get("errorMsgInUrl")

            if not error in response.url:
                print("\033[37;1m[\033[92;1m+\033[37;1m]\033[92;1m {}:\033[0m".format(social_network), url)
                write_to_file(url, fname)
            else:
                print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Not Found!".format(social_network))

    print("\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Saved: \033[37;1m{}\033[0m".format(username + ".txt"))


main()
