import os
import json
import requests

# TODO: fix tumblr

def print_banner():
    print("                                              .\"\"\"-.")
    print("                                             /      \\")
    print("\033[37;1m ____  _               _            _        |  _..--'-.")
    print("\033[37;1m/ ___|| |__   ___ _ __| | ___   ___| |__    >.`__.-\"\"\;\"`")
    print("\033[37;1m\___ \| '_ \ / _ \ '__| |/ _ \ / __| |/ /   / /(     ^\\")
    print("\033[37;1m ___) | | | |  __/ |  | | (_) | (__|   <    '-`)     =|-.")
    print("\033[37;1m|____/|_| |_|\___|_|  |_|\___/ \___|_|\_\    /`--.'--'   \ .-.")
    print("\033[37;1m                                           .'`-._ `.\    | J /")
    print("\033[37;1m                                          /      `--.|   \__/\033[0m")

def search_accounts(username, social_networks_params):
    existing_accounts = list()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0'
    }

    for social_network in social_networks_params:
        url = social_networks_params.get(social_network).get("url").format(username)
        error_type = social_networks_params.get(social_network).get("errorType")
        try:
            response = requests.get(url, headers=headers)
        except Exception as e:
            print(f"error connecting to {url}: {e}")
            continue

        if error_type == "message":
            error = social_networks_params.get(social_network).get("errorMsg")
            if error in response.text:
                print(f"\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {social_network}:\033[93;1m Not Found!")
                continue

        elif error_type == "status_code":
            if response.status_code == 404:
                print(f"\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {social_network}:\033[93;1m Not Found!")
                continue

        elif error_type == "response_url":
            error = social_networks_params.get(social_network).get("errorUrl")
            if error in response.url:
                print(f"\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {social_network}:\033[93;1m Not Found!")
                continue

        print(f"\033[37;1m[\033[92;1m+\033[37;1m]\033[92;1m {social_network}:\033[0m", url)
        existing_accounts.append(url)

    return existing_accounts

def save_account_urls(account_urls, filename):
    with open(filename, "a") as file:
        file.writelines(account_urls)

def remove_old_file(filename):
    if os.path.isfile(filename):
        os.remove(filename)
        print(f"\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Removing previous file:\033[1;37m {filename}\033[0m")

def get_social_networks_params():
    with open("data.json", "r") as file:
        social_networks_params = json.load(file)
    return social_networks_params

def main():
    print_banner()
    username = input("\033[92;1m[\033[37;1m?\033[92;1m]\033[92;1m Input Username: \033[0m")
    print()

    filename = f"{username}.txt"
    remove_old_file(filename)

    social_networks_params = get_social_networks_params()
    if social_networks_params is None:
        print("Error loading social networks parameters. Exiting.")
        return

    print(f"\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Checking username\033[0m\033[1;37m {username}\033[0m\033[1;92m on: \033[0m")

    existing_accounts = search_accounts(username, social_networks_params)
    if len(existing_accounts) == 0:
        print("No accounts found. Exiting without saving.")
        return

    save_account_urls(existing_accounts, filename)
    print(f"\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Saved: \033[37;1m{filename}\033[0m")

if '__main__' in __name__:
    main()