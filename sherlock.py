import requests
import json
import os

def write_to_file(url, fname):
	with open(fname, "a") as f:
		f.write(url+"\n")


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
    

        r = requests.get(url, headers=headers)
    
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

    print("\033[1;92m[\033[0m\033[1;77m*\033[0m\033[1;92m] Saved: \033[37;1m{}\033[0m".format(username+".txt"))
        	
main()