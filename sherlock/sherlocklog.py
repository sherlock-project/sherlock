class SherlockLog:
    def __init__(self):
        pass

    def _message(self, status: str, message:str):
        pass
    
    def info(
        err: str, 
        var: str, 
        debug=False):
        
        
        print((Style.BRIGHT + Fore.GREEN + "[" +
           Fore.YELLOW + "*" +
           Fore.GREEN + "] Checking username" +
           Fore.WHITE + " {}" +
           Fore.GREEN + " on:").format(username))
        
    @SherlockLog.message    
    def error(self,
        err: str, 
        errstr: str, 
        var: str, 
        debug=False):
        print(Style.BRIGHT + Fore.WHITE + "[" +
              Fore.RED + "-" +
              Fore.WHITE + "]" +
              Fore.RED + f" {errstr}" +
              Fore.YELLOW + f" {err if debug else var}")
