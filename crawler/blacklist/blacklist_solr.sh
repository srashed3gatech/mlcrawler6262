#!/usr/bin/env bash

# Simple script that runs blacklist parser and writes data to a Solr collection
python blacklist_parser.py
~/bin/post -c blacklist data.json
