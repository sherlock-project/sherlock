from sherlock import sherlock


def main():
    print(
        """
                                              .\"\"\"-.
                                             /      \\
 ____  _               _            _        |  _..--'-.
/ ___|| |__   ___ _ __| | ___   ___| |__    >.`__.-\"\"\;\"`
\___ \| '_ \ / _ \ '__| |/ _ \ / __| |/ /   / /(     ^\\
 ___) | | | |  __/ |  | | (_) | (__|   <    '-`)     =|-.
|____/|_| |_|\___|_|  |_|\___/ \___|_|\_\    /`--.'--'   \ .-.
                                           .'`-._ `.\    | J /

"""
    )

    # Load all the parameters
    # Colorama module's initialization.
    python_version = platform.python_version_tuple()
    version_string = ""

    # Check version
    if not int(python_version[0]) == 3 and int(python_version[1]) >= 1:
        print(
            "Sherlock can't use his magnifying glass on python version %s yet."
            % platform.python_version()
        )
        exit()

    version_string = (
            "sherlock %s, %s.\n" % (__version__, __description__)
            + "requests: %s, %s.\n" % (requests.__version__, requests.__description__)
            + "python: %s." % platform.python_version()
    )

    coloramainit(autoreset=True)

    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description="%s (Version %s)" % (__description__, __version__),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=version_string,
        help="Display version information and dependencies.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        "-d",
        "--debug",
        action="store_true",
        dest="verbose",
        default=False,
        help="Display extra debugging information and metrics.",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_false",
        dest="verbose",
        help="Disable debugging information (Default Option).",
    )
    parser.add_argument(
        "--tor",
        "-t",
        action="store_true",
        dest="tor",
        default=False,
        help="Make requests over TOR; increases runtime; requires TOR to be installed and in system path.",
    )
    parser.add_argument(
        "--unique-tor",
        "-u",
        action="store_true",
        dest="unique_tor",
        default=False,
        help="Make requests over TOR with new TOR circuit after each request; increases runtime; requires TOR to be installed and in system path.",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        dest="csv",
        default=False,
        help="Create Comma-Separated Values (CSV) File.",
    )
    parser.add_argument(
        "--site",
        action="append",
        metavar="SITE_NAME",
        dest="site_list",
        default=None,
        help="Limit analysis to just the listed sites.  Add multiple options to specify more than one site.",
    )
    parser.add_argument(
        "username",
        nargs="+",
        metavar="USERNAMES",
        action="store",
        help="One or more usernames to check with social networks.",
    )

    args = parser.parse_args()
    logger = Log.getLogger()

    sherlock.main(
        args.username[0],
        Data.fromFile(filename="data.json", t="json"),
        logger=logger,
    )