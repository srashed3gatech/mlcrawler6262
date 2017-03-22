#!/usr/bin/env bash

# Simple script that runs blacklist parser and writes data to a Solr collection
BLACKLIST_CORE = blacklist

python blacklist_parser.py

~/bin/post -c $BLACKLIST_CORE data.json
