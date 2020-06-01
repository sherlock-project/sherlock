import os
import sys
import colorama
from colorama import Fore, Style
colorama.init(autoreset=True)

def userError(str):
    print(Fore.RED+str)
def userWarn(str):
    print(f"{Fore.YELLOW}Warning: {str}")
def userFine(str):
    print(Fore.GREEN+str)

def run():
    # If there are arguments
    if len(sys.argv) != 1:
        try:
            file = open(sys.argv[1] + ".txt", "r")
        except:
            userWarn(f"No such file {sys.argv[1]}.txt exists!")
            return True
        lines = file.readlines()
        # removes the last line in the .txt which isnt a url
        lines = lines[:-1]
        if sys.argv[2] == "all":
            if len(lines) > 20:
                userWarn(f"The amount of sites about to be opened is greater than 20 totalling {Fore.RED}{len(lines)}{Fore.YELLOW}. Proceed? y/n")
                resume = input()
                if resume.lower() == "y":
                    for i in range(0, len(lines)):
                        os.system('start "" ' + lines[i])
                    userFine("Action completed!")
                else:
                    userWarn("Action aborted\n")
                    userFine("Consider setting a custom amount: python3 opensites.py [file (no .txt extension)] [custom val]\n\nEg:\npython3 openfile.py username 10")
        else:
            # since you havent typed "all" it makes sure you have entered a number instead
            try:
                arg2 = int(sys.argv[2])
                # if arg2 is even in the len(array)
                if arg2 < len(lines)-1 and arg2 >= 0:
                    for i in range(0, arg2):
                        os.system('start "" ' + lines[i])
                else:
                    userError("Invalid entry, must be at least 0 and at max len(lines)")
            # You haven't entered a number instead
            except ValueError:
                userError("Invalid entry, must be this format: [all || <amount>]")
    else:
        userError("\nNo arguments supplied!\nusage: python3 opensites.py [file (without.txt extension)] [all || <amount>]\n")

run()
