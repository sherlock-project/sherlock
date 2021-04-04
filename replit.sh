#!/usr/bin/env bash

echo -en 'enter usernames to search for:\n\t'
read -p '? ' REPLY
mkdir -p searchs
python sherlock/sherlock.py --folderoutput ./searchs \
                            $REPLY
