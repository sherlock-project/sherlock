
""" 
{ 
    < Author : @Treveen Bastian >
    < Date   : 6/9/2023         >
    < Title  : InsightHunter    >
} 
"""

import time 
import requests
import json
import colorama
from colorama import Back, Fore, Style 
from prettytable import PrettyTable 
import sys
import subprocess 

def banner():
    print(Fore.LIGHTYELLOW_EX + """

        ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
        █▄ ▄█ ▄▄▀█ ▄▄██▄██ ▄▄▄█ ████▄ ▄██ ██ █ ██ █ ▄▄▀█▄ ▄█ ▄▄█ ▄▄▀
        ██ ██ ██ █▄▄▀██ ▄█ █▄▀█ ▄▄ ██ ███ ▄▄ █ ██ █ ██ ██ ██ ▄▄█ ▀▀▄
        █▀ ▀█▄██▄█▄▄▄█▄▄▄█▄▄▄▄█▄██▄██▄███ ██ ██▄▄▄█▄██▄██▄██▄▄▄█▄█▄▄
        ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀ 
        Author : Treveen Bastian      |    Date    : 6/9/2023 
        OSINT  : True                 |    Awesome : True 

    """)
    x = PrettyTable()
    x.field_names = ["Commands", "Usage"]
    x.add_row(["setUsername", " -Config a username to use"])
    x.add_row(["huntAll", " -Hunt All social media platforms"])
    x.add_row(["listAllMedia", " -list all media platforms"])
    x.add_row(["huntTarget", " -Hunt a target social media"])

    x.add_row(["run", " -runs the prgram"])
    print(x)


def main():
    global GotUser 
    global huntAll 
    global huntTarget
    global target_inp 
    global Name 

    AppOn = True 
    GotUser = False 
    huntAll = True 
    huntTarget = False 

    string_sites = ['instagram', 'facebook', 'twitter', 'tiktok', 'telegram', 'codecademy', 'patreon', 'bitbucket', 'slack', 'imgur', 'cashme', 'goodreads', 'livejournal', 'aboutme', 'flipboard', 'ebay', 'canva', 'scribd', 'creative_market', 'instructables', 'steam',' wordpress', 'gravatar', 'vimeo', 'twitch', 'github', 'pinterest', 'quora', 'flickr', 'soundcloud', 'youtube', 'reddit', 'linkedin', 'medium', 'blogger', 'replit']

    while AppOn:
            inp = str(input(Fore.CYAN + "INSIGHTHUNTER > "))
            if inp.split()[0] == "setUsername":
                Name = inp.split()[1]
                print(f"Username : {Name}")
                GotUser = True 

            # inp commands
            if inp.split()[0] == "huntAll" and inp.split()[1] == "True" and GotUser == True:
                huntAll = True 
                print("[*] Hunt All => True")
            elif inp.split()[0] == "huntAll" and inp.split()[1] == "False" and GotUser == True:
                huntAll = False 
                print("[*] Hunt All => False")

            elif inp.split()[0] == "huntTarget" and inp.split()[1] == "True" and GotUser == True:
                huntTarget = True 
                target_inp = inp.split()[2]
                print(f"[*] Hunt Target => True | Media: {target_inp}")
            
            elif inp.split()[0] == "huntTarget" and inp.split()[1] == "False" and GotUser == True:
                huntTarget  = False 
                print(f"[*] Hunt Target => False")

            if inp == "run" and GotUser == True:
                social_media()

            if inp == "clear":
                subprocess.run("cls", shell=True)

            if inp == "ls":
                subprocess.run("dir", shell=True)

            if inp == "listAllMedia":
                print(string_sites)

            elif inp == "exit":
                print(Fore.LIGHTYELLOW_EX + "[+] - Happy hunting | GoodBye!")
                sys.exit()


def social_media():
    print(Fore.LIGHTCYAN_EX + "=================(( Social Media ))=================")
    time.sleep(0.3)

    instagram = f"https://instagram.com/{Name}"
    facebook = f"https://facebook.com/{Name}"
    twitter = f"https://twitter.com/{Name}"
    youtube = f"https://youtube.com/{Name}"
    reddit = f"https://reddit.com/user/{Name}"
    pinterest = f"https://www.pinterest.com/{Name}"
    linkedin = f"https://www.linkedin.com/in/{Name}"
    tiktok = f"https://www.tiktok.com/@{Name}"
    vimeo = f"https://www.vimeo.com/{Name}"
    twitch = f"https://www.twitch.tv/{Name}"
    flickr = f"https://www.flickr.com/people/{Name}"
    quora = f"https://www.quora.com/profile/{Name}"
    soundcloud = f"https://www.soundcloud.com/{Name}"
    github = f"https://www.github.com/{Name}"
    medium = f"https://www.medium.com/@{Name}"
    telegram = f"https://www.t.me/{Name}"
    blogger = f"https://{Name}.blogspot.com"
    replit = f"https://replit.com/@{Name}"
    steam = f'https://steamcommunity.com/id/{Name}'
    flipboard = f'https://flipboard.com/@{Name}'
    scribd = f'https://www.scribd.com/{Name}'
    instructables = f'https://www.instructables.com/member/{Name}'
    codecademy = f'https://www.codecademy.com/{Name}'
    gravatar = f'https://en.gravatar.com/{Name}'
    canva = f'https://www.canva.com/{Name}'
    creative_market = f'https://creativemarket.com/{Name}'
    ebay = f'https://www.ebay.com/usr/{Name}'
    slack = f'https://{Name}.slack.com'
    patreon = f'https://www.patreon.com/{Name}'
    bitbucket = f'https://bitbucket.org/{Name}'
    flipboard = f'https://flipboard.com/@{Name}'
    aboutme = f'https://about.me/{Name}'
    imgur = f'https://imgur.com/user/{Name}'
    cashme = f'https://cash.me/{Name}'
    goodreads = f'https://www.goodreads.com/{Name}'
    chess = f'https://chess.com/member/{Name}'
    disqus = f'https://disqus.com/{Name}'
    leetcode = f'https://leetcode.com/{Name}'
    codesignal = f'https://app.codesignal.com/profile/{Name}'
    minecraft = f'https://app.mojang.com/users/profiles/minecraft/{Name}'
    ok = f'https://ok.ru/{Name}'
    redbubble = f'https://redbubble.com/people/{Name}'
    
    sites = [instagram, facebook, twitter, tiktok, telegram, codecademy, patreon, 
             bitbucket, slack, imgur, cashme, goodreads, aboutme, flipboard, 
             ebay, canva, scribd, creative_market, instructables, steam, 
             gravatar, vimeo, twitch, github, pinterest, quora, flickr, soundcloud, 
             youtube, reddit, linkedin, medium, blogger, replit, chess, disqus, leetcode, codesignal,
             minecraft, ok, redbubble]

    OnSite = False 
    if huntAll:
        for site in sites:
                server = requests.get(site)
                if server.status_code == 200:
                    print(Fore.GREEN + f"Site: {site} =>")
                    time.sleep(0.3)
                    if Name in server.text:
                        OnSite = True 
                        print(Fore.GREEN + f"[+] Username : {Name} located in site! | STATUS : {server.status_code}")
                        print(Fore.GREEN + "- + - + - + - + - + - + - + - + - + - + - +")
                    else:
                        print(Fore.RED + f"[-] Username : {Name} not found in site! | STATUS : {server.status_code}")
                        print(Fore.RED + "- + - + - + - + - + - + - + - + - + - + - +")

    elif huntTarget:
        server = requests.get(target_inp)
        if server.status_code == 200:
            print(Fore.GREEN + f"Site: {target_inp}")
            if Name in server.text:
                OnSite = True 
                print(Fore.GREEN + f"[+] Username : {Name} located in site! | STATUS : {server.status_code}")
            else:
                print(Fore.RED + f"[-] Username : {Name} not found in site! | STATUS : {server.status_code}")

if __name__ == "__main__":
    banner()
    main()
