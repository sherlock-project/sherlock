#!/bin/bash

# install python3 if not exist
sudo apt-get install python3

# install the all the necessery packages and requirements
sudo apt-get install python3-pip
sudo pip3 install --upgrade setuptools
sudo pip3 install -r requirements.txt


