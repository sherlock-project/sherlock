# Sherlock
> Find usernames across [social networks](https://github.com/sdushantha/sherlock/blob/master/sites.md) 

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

# install the requirements
$ pip3 install -r requirements.txt
```

# API Documentation

Classes:
- sherlock.Data
- sherlock.Log
- sherlock.Service

#### __Class__ sherlock.Log

#### `eprint(status: str, message: str, status_color: Fore = Fore.WHITE, status_frame: Fore = Fore.WHITE, message_color: Fore = Fore.WHITE, style: Style = Style.BRIGHT)`

Prints to the logger stored within the Log object.

- **`status`** `str` `option`

   The status of the message.

- **`message`** `str` `option`

   The actual description of the error

- **`status_color`** `Fore` `option` `default = Fore.WHITE`

   The color of the status.

- **`status_frame`** `Fore` `option` `default  = Fore.WHITE`

   The color of the brackets that surround the status.

- **`message_color`** `Fore` `option` `default  = Fore.WHITE`

   The message color.

- **`style`** `Style` `option` `default = Style.BRIGHT`

   The brightness style of the whole message.



#### `error(message: str)`

Error logging.

- **`message`** `str`

   The error message.

#### `info(message: str)`

Info logging.

- **`message`** `str`

   The info message.

#### `lock()`

Locks the logger to a single thread, use to lock the logger if using some particular data on a thread.
Please ensure once your complete, call the unlock method.

#### `log(message: str)`

General logging with no errors.

- **`message`** `str`

   The log message.

#### `unlock()`

Unlocks the logger, relinquishes resources to all threads.
#### __Class__ sherlock.Data

#### `byindex(i: int)`


Gets an entry by index instead of key.

- **`i`** `int`

   returns a tuple of key and data associated with the index i.

#### `keys()`

Gets the keys within the directory

- **`return`** `list`

   A list of keys are return.
#### __Class__ sherlock.SLException

#### `get_message()`

The exception message associated with the SLException object

- **`return`** `str` `return`

   The message of the SLException object.

#### __Class__ sherlock.SLUnsupportedTypeException

#### `get_message()`

The exception message associated with the SLException object

- **`return`** `str` `return`





## Testing using tox
**NOTE**: Tox is required to perform tests on sherlock, for installation instructions for tox,
please visit https://tox.readthedocs.io/en/latest/install.html. Once installed, all that's required is to navigate to the root of the project and type:
    
    $ tox
    
    

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

The ```--rm``` flag is optional.  It removes the container filesystem after running so you do not have a bunch of leftover container filesystem cruft.  See https://docs.docker.com/engine/reference/run/#clean-up---rm

One caveat is the text file that is created will only exist in the container so you will not be able to get at that.


Or you can simply use "Docker Hub" to run `sherlock`:
```
docker run theyahya/sherlock user123
```

## License
MIT License

Copyright (c) 2018 Siddharth Dushantha
