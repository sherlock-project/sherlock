import requests
import json
import os
import sys
import argparse

DEBUG = False

def write_to_file(url, fname):
	with open(fname, "a") as f:
		f.write(url+"\n")

def make_request(url, headers, error_type, social_network):
    try:
        r = requests.get(url, headers=headers)
        if r.status_code:
            return r, error_type
    except requests.exceptions.HTTPError as errh:
        if DEBUG:
            print ("\033[37;1m[\033[91;1m-\033[37;1m]\033[91;1m HTTP Error:\033[93;1m", errh)
        else:
            print ("\033[37;1m[\033[91;1m-\033[37;1m]\033[91;1m HTTP Error:\033[93;1m", social_network)
    except requests.exceptions.ConnectionError as errc:
        if DEBUG:
            print ("\033[37;1m[\033[91;1m-\033[37;1m]\033[91;1m Error Connecting:\033[93;1m", errc)
        else:
            print ("\033[37;1m[\033[91;1m-\033[37;1m]\033[91;1m Error Connecting:\033[93;1m", social_network)
    except requests.exceptions.Timeout as errt:
        if DEBUG:
            print ("\033[37;1m[\033[91;1m-\033[37;1m]\033[91;1m Timeout Error:\033[93;1m", errt)
        else:
            print ("\033[37;1m[\033[91;1m-\033[37;1m]\033[91;1m Timeout Error:\033[93;1m", social_network)
    except requests.exceptions.RequestException as err:
        if DEBUG:
            print ("\033[37;1m[\033[91;1m-\033[37;1m]\033[91;1m Unknown error:\033[93;1m", err)
        else:
            print ("\033[37;1m[\033[91;1m-\033[37;1m]\033[91;1m Unknown error:\033[93;1m", social_network)
    return None, ""
    
def sherlock(username):
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

    print()

    fname = username+".txt"

    if os.path.isfile(fname):
    	os.remove(fname)
    	print("\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Removing previous file:\033[1;37m {}\033[0m".format(fname))

    print("\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Checking username\033[0m\033[1;37m {}\033[0m\033[1;92m on: \033[0m".format(username))
    raw = open("data.json", "r")
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

        r, error_type = make_request(url=url, headers=headers, error_type=error_type, social_network=social_network)
        
        if error_type == "message":
            error = data.get(social_network).get("errorMsg")
            
            if not error in r.text:
                print("\033[37;1m[\033[92;1m+\033[37;1m]\033[92;1m {}:\033[0m".format(social_network), url)
                write_to_file(url, fname)                	
            
            else:
            	print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Not Found!".format(social_network))
            
        elif error_type == "status_code":
            
            if not r.status_code == 404:
                print("\033[37;1m[\033[92;1m+\033[37;1m]\033[92;1m {}:\033[0m".format(social_network), url)
                write_to_file(url, fname)
            
            else:
            	print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Not Found!".format(social_network))

        elif error_type == "response_url":
            error = data.get(social_network).get("errorMsgInUrl")
            
            if not error in r.url:
                print("\033[37;1m[\033[92;1m+\033[37;1m]\033[92;1m {}:\033[0m".format(social_network), url)
                write_to_file(url, fname)
            else:
            	print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Not Found!".format(social_network))

        elif error_type == "":
            print("\033[37;1m[\033[91;1m-\033[37;1m]\033[92;1m {}:\033[93;1m Error!".format(social_network))

    print("\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Saved: \033[37;1m{}\033[0m".format(username+".txt"))


class ArgumentParserError(Exception): pass

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print("                                              .\"\"\"-.")
        print("                                             /      \\")
        print("\033[37;1m ____  _               _            _        |  _..--'-.")
        print("\033[37;1m/ ___|| |__   ___ _ __| | ___   ___| |__    >.`__.-\"\"\;\"`")
        print("\033[37;1m\___ \| '_ \ / _ \ '__| |/ _ \ / __| |/ /   / /(     ^\\")
        print("\033[37;1m ___) | | | |  __/ |  | | (_) | (__|   <    '-`)     =|-.")
        print("\033[37;1m|____/|_| |_|\___|_|  |_|\___/ \___|_|\_\    /`--.'--'   \ .-.")
        print("\033[37;1m                                           .'`-._ `.\    | J /")
        print("\033[37;1m                                          /      `--.|   \__/\033[0m")
        self.print_usage(sys.stderr)

parser = ArgumentParser()
parser.add_argument('username', help='check services with given username')
parser.add_argument("-d", '--debug', help="enable debug mode", action="store_true")

args = parser.parse_args()
if args.debug:
    DEBUG = True
if args.username:
    sherlock(args.username)