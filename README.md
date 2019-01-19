# Sherlock
> Find usernames across [social networks](https://github.com/theyahya/sherlock/blob/master/sites.md) 

<p align="center">
<img src="./screenshot/preview.png">
</p>

## Installation

**NOTE**: Python 3.6 or higher is required.

```bash
# clone the repo
$ git clone https://github.com/TheYahya/sherlock.git

# change the working directory to sherlock
$ cd sherlock

# install python3 and python3-pip if not exist

# install the requirements
$ pip3 install -r requirements.txt
```

## Usage

```bash
$ python3 sherlock.py --help
usage: sherlock.py [-h] [--version] [--verbose] [--quiet] [--tor]
                   [--unique-tor] [--csv] [--site SITE_NAME]
                   USERNAMES [USERNAMES ...]

Sherlock: Find Usernames Across Social Networks (Version 0.2.0)

positional arguments:
  USERNAMES             One or more usernames to check with social networks.

optional arguments:
  -h, --help            show this help message and exit
  --version             Display version information and dependencies.
  --verbose, -v, -d, --debug
                        Display extra debugging information and metrics.
  --quiet, -q           Disable debugging information (Default Option).
  --tor, -t             Make requests over TOR; increases runtime; requires
                        TOR to be installed and in system path.
  --unique-tor, -u      Make requests over TOR with new TOR circuit after each
                        request; increases runtime; requires TOR to be
                        installed and in system path.
  --csv                 Create Comma-Separated Values (CSV) File.
  --site SITE_NAME      Limit analysis to just the listed sites. Add multiple
                        options to specify more than one site.
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

## License

MIT © [Yahya SayadArbabi](https://theyahya.com)
