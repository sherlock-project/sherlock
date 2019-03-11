<p align=center>
 
<img src="https://user-images.githubusercontent.com/27065646/53551960-ae4dff80-3b3a-11e9-9075-cef786c69364.png"/>
 
<br>
<span>Find usernames across <a href="https://github.com/theyahya/sherlock/blob/master/sites.md">social networks</a></span>
<br>
<a target="_blank" href="https://www.python.org/downloads/" title="Python version"><img src="https://img.shields.io/badge/python-%3E=_3.6-green.svg"></a>
<a target="_blank" href="LICENSE" title="License: MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg"></a>
<a target="_blank" href="https://travis-ci.com/TheYahya/sherlock/" title="Build Status"><img src="https://travis-ci.com/TheYahya/sherlock.svg?branch=master"></a>
<a target="_blank" href="https://twitter.com/intent/tweet?text=%F0%9F%94%8E%20Find%20usernames%20across%20social%20networks%20&url=https://github.com/TheYahya/sherlock&hashtags=hacking,%20osint,%20bugbounty,%20reconnaissance" title="Build Status"><img src="https://img.shields.io/twitter/url/http/shields.io.svg?style=social"></a>
<a target="_blank" href="http://sherlock-project.github.io/"><img alt="Website" src="https://img.shields.io/website-up-down-green-red/http/sherlock-project.github.io/.svg"></a>
</p>
<p align="center">
<a href="https://asciinema.org/a/223115">
<img src="./screenshot/preview.gif" width="280" height="477"/>
</a>
</p>

## Installation

**NOTE**: Python 3.6 or higher is required.

```bash
# clone the repo
$ git clone https://github.com/sherlock-project/sherlock.git

# change the working directory to sherlock
$ cd sherlock

# install python3 and python3-pip if not exist

# install the requirements
$ pip3 install -r requirements.txt
```

## Usage

```bash
$ python3 sherlock.py --help
usage: sherlock.py [-h] [--version] [--verbose] [--rank]
                   [--folderoutput FOLDEROUTPUT] [--output OUTPUT] [--tor]
                   [--unique-tor] [--csv] [--site SITE_NAME]
                   [--proxy PROXY_URL] [--json JSON_FILE]
                   USERNAMES [USERNAMES ...]

Sherlock: Find Usernames Across Social Networks (Version 0.5.7)

positional arguments:
  USERNAMES             One or more usernames to check with social networks.

optional arguments:
  -h, --help            show this help message and exit
  --version             Display version information and dependencies.
  --verbose, -v, -d, --debug
                        Display extra debugging information and metrics.
  --rank, -r            Present websites ordered by their Alexa.com global
                        rank in popularity.
  --folderoutput FOLDEROUTPUT, -fo FOLDEROUTPUT
                        If using multiple usernames, the output of the results
                        will be saved at this folder.
  --output OUTPUT, -o OUTPUT
                        If using single username, the output of the result
                        will be saved at this file.
  --tor, -t             Make requests over TOR; increases runtime; requires
                        TOR to be installed and in system path.
  --unique-tor, -u      Make requests over TOR with new TOR circuit after each
                        request; increases runtime; requires TOR to be
                        installed and in system path.
  --csv                 Create Comma-Separated Values (CSV) File.
  --site SITE_NAME      Limit analysis to just the listed sites. Add multiple
                        options to specify more than one site.
  --proxy PROXY_URL, -p PROXY_URL
                        Make requests over a proxy. e.g.
                        socks5://127.0.0.1:1080
  --json JSON_FILE, -j JSON_FILE
                        Load data from a JSON file or an online, valid, JSON
                        file.
  --print-found
			Prints only found messages. Errors, and invalid
			username errors will not appear.
```

For example, run ```python3 sherlock.py user123```, and all of the accounts
found will be stored in a text file with the username (e.g ```user123.txt```).

## Docker Notes
If you have docker installed you can build an image and run this as a container.

```
docker build -t mysherlock-image .
```

Once the image is built sherlock can be invoked by running the following:

```
docker run --rm mysherlock-image user123
```

The optional ```--rm``` flag removes the container filesystem on completion to prevent cruft build-up.  See https://docs.docker.com/engine/reference/run/#clean-up---rm

One caveat is the text file that is created will only exist in the container so you will not be able to get at that.


Or you can simply use "Docker Hub" to run `sherlock`:
```
docker run theyahya/sherlock user123
```

## Adding New Sites

Please look at the Wiki entry on
[adding new sites](https://github.com/TheYahya/sherlock/wiki/Adding-Sites-To-Sherlock)
to understand the issues.

## Tests
If you are contributing to Sherlock, then Thank You!

Before creating a pull request with new development, please run the tests
to ensure that all is well.  It would also be a good idea to run the tests
before starting development to distinguish problems between your
environment and the Sherlock software.

The following is an example of the command line to run all the tests for
Sherlock.  This invocation hides the progress text that Sherlock normally
outputs, and instead shows the verbose output of the tests.

```
$ python3 -m unittest tests.all --buffer --verbose
```

Note that the tests are very much a work in progress.  Significant work is
required to get full test coverage.  But, the current tests are working
properly, and will be expanded as time goes by.

## Stargazers over time

[![Stargazers over time](https://starcharts.herokuapp.com/TheYahya/sherlock.svg)](https://starcharts.herokuapp.com/TheYahya/sherlock)

## License

MIT © [Yahya SayadArbabi](https://theyahya.com)<br/>
Original Creator - [Siddharth Dushantha](https://github.com/sdushantha)
