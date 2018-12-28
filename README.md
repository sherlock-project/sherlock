# Sherlock
> Find usernames across social networks 

<p align="center">
<img src="preview.png">
</a>
</p>

## Installation

```bash
# clone the repo
$ git clone https://github.com/sdushantha/sherlock.git

# change the working directory to sherlock
$ cd sherlock

# install the requirements
$ pip3 install -r requirements.txt
```

## Usage

```bash
$ python3 sherlock.py --help
usage: sherlock.py [-h] [--version] [--verbose] [--quiet]
                   USERNAMES [USERNAMES ...]

Sherlock: Find Usernames Across Social Networks (Version 0.1.0)

positional arguments:
  USERNAMES             One or more usernames to check with social networks.

optional arguments:
  -h, --help            show this help message and exit
  --version             Display version information and dependencies.
  --verbose, -v, -d, --debug
                        Display extra debugging information.
  --quiet, -q           Disable debugging information (Default Option).
```

For example, run ```python3 sherlock.py user123```, and all of the accounts
found will be stored in a text file with the username (e.g ```user123.txt```).

## License
MIT License

Copyright (c) 2018 Siddharth Dushantha
