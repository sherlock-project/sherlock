from sherlockdata import SherlockData
from sherlockfinder import SherlockFinder
from sherlocklog import SherlockLog
from sherlockservice import SherlockService

def main(
        data: SherlockData,
        log: SherlockLog):
    log.info("Scanning though all %i different media sites" % len(data))


if __name__ == "__main__":
    
    print("""
                                              .\"\"\"-.
                                             /      \\
 ____  _               _            _        |  _..--'-.
/ ___|| |__   ___ _ __| | ___   ___| |__    >.`__.-\"\"\;\"`
\___ \| '_ \ / _ \ '__| |/ _ \ / __| |/ /   / /(     ^\\
 ___) | | | |  __/ |  | | (_) | (__|   <    '-`)     =|-.
|____/|_| |_|\___|_|  |_|\___/ \___|_|\_\    /`--.'--'   \ .-.
                                           .'`-._ `.\    | J /

""")
    
    main(
        SherlockData.fromFile(filename="data.json",t="json"),
        SherlockLog.getLogger())
    
    
