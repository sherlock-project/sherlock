import requests
import json
import os
import sys
import re
import argparse

DEBUG = False

# TODO: fix tumblr

def write_to_file(url, fname):
	with open(fname, "a") as f:
		f.write(url+"\n")

def print_error(err, errstr, var, debug = False):
    if debug:
        print (f"\033[37;1m[\033[91;1m-\033[37;1m]\033[91;1m {errstr}\033[93;1m {err}")
    else:
        print (f"\033[37;1m[\033[91;1m-\033[37;1m]\033[91;1m {errstr}\033[93;1m {var}")

def make_request(url, headers, error_type, social_network):
    try:
        r = requests.get(url, headers=headers)
        if r.status_code:
            return r, error_type
    except requests.exceptions.HTTPError as errh:
        print_error(errh, "HTTP Error:", social_network, DEBUG)
    except requests.exceptions.ConnectionError as errc:
        print_error(errc, "Error Connecting:", social_network, DEBUG)
    except requests.exceptions.Timeout as errt:
        print_error(errt, "Timeout Error:", social_network, DEBUG)
    except requests.exceptions.RequestException as err:
        print_error(err, "Unknown error:", social_network, DEBUG)
    return None, ""
    
def sherlock(username):
    # Not sure why, but the banner messes up if i put into one print function
    print("\033[37;1m                                              .\"\"\"-.")
    print("\033[37;1m                                             /      \\")
    print("\033[37;1m ____  _               _            _        |  _..--'-.")
    print("\033[37;1m/ ___|| |__   ___ _ __| | ___   ___| |__    >.`__.-\"\"\;\"`")
    print("\033[37;1m\___ \| '_ \ / _ \ '__| |/ _ \ / __| |/ /   / /(     ^\\")
    print("\033[37;1m ___) | | | |  __/ |  | | (_) | (__|   <    '-`)     =|-.")
    print("\033[37;1m|____/|_| |_|\___|_|  |_|\___/ \___|_|\_\    /`--.'--'   \ .-.")
    print("\033[37;1m                                           .'`-._ `.\    | J /")
    print("\033[37;1m                                          /      `--.|   \__/\033[0m")

    print()

    fname = username+".txt"

    if os.path.isfile(fname):
    	os.remove(fname)
    	print("\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Removing previous file:\033[1;37m {}\033[0m".format(fname))

    print("\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Checking username\033[0m\033[1;37m {}\033[0m\033[1;92m on: \033[0m".format(username))
    raw = open("data.json", "r", encoding="utf-8")
    data = json.load(raw)

    # User agent is needed because some sites does not 
    # return the correct information because it thinks that
    # we are bot
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0'
    }

    for social_network in data:
        url = data.get(social_network).get("url").format(username)
        error_type = data.get(social_network).get("errorType")
        regex_check = data.get(social_network).get("regexCheck")

        if regex_check is None:
            #Use default regular expression check for user names.
            regex_check = "^[a-zA-Z][a-zA-Z0-9._-]*$"

        if re.search(regex_check, username) is None:
            #No need to do the check at the site: this user name is not allowed.
            print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Illegal User Name Format For This Site!".format(social_network))
            continue

        r, error_type = make_request(url=url, headers=headers, error_type=error_type, social_network=social_network)
        
        if error_type == "message":
            error = data.get(social_network).get("errorMsg")
            # Checks if the error message is in the HTML
            if not error in r.text:
                print("\033[37;1m[\033[92;1m+\033[37;1m]\033[92;1m {}:\033[0m".format(social_network), url)
                write_to_file(url, fname)                	
            
            else:
            	print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Not Found!".format(social_network))
            
        elif error_type == "status_code":
            # Checks if the status code of the repsonse is 404
            if not r.status_code == 404:
                print("\033[37;1m[\033[92;1m+\033[37;1m]\033[92;1m {}:\033[0m".format(social_network), url)
                write_to_file(url, fname)
            
            else:
            	print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Not Found!".format(social_network))

        elif error_type == "response_url":
            error = data.get(social_network).get("errorUrl")
            # Checks if the redirect url is the same as the one defined in data.json
            if not error in r.url:
                print("\033[37;1m[\033[92;1m+\033[37;1m]\033[92;1m {}:\033[0m".format(social_network), url)
                write_to_file(url, fname)
            else:
            	print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Not Found!".format(social_network))

        elif error_type == "":
            print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Error!".format(social_network))

    print("\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Saved: \033[37;1m{}\033[0m".format(username+".txt"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('username', help='check services with given username')
    parser.add_argument("-d", '--debug', help="enable debug mode", action="store_true")

    args = parser.parse_args()
    
    if args.debug:
        DEBUG = True

    if args.username:
        sherlock(args.username)