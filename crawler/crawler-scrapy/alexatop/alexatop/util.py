import os
import csv
import json
import hashlib
import requests
from zipfile import ZipFile
from collections import OrderedDict

ALEXA_LIST_URL = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'

def grab_alexa(count=0):
    '''Grabs Alexa top 1M list and returns it as a OrderedDict int (rank) -> str (url)'''
    # Grab ZIP and store on disk
    resp = requests.get(ALEXA_LIST_URL)
    archive = resp.content

    with open('top1m.zip', 'wb') as f:
        f.write(archive)

    data = []

    # Unzip, read, and parse CSV
    with ZipFile('top1m.zip', 'r') as zf:
        lines = [line.decode() for line in zf.open('top-1m.csv', 'r').readlines()]

        if count > 0:
            lines = lines[:count]
        else:
            raise Exception('Please pass in a positive count.')

        # Append each URL to list, in rank order
        for row in csv.reader(lines):
            data.append('http://' + row[1])

    # Clean up (delete .zip file)
    os.remove('top1m.zip')

    return data

def compute_md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def dict_to_json(d):
    '''Convert a dict to JSON.'''
    # Convert a binary dict to clean dict for JSON encoding
    # http://stackoverflow.com/questions/33137741/fastest-way-to-convert-a-dicts-keys-values-from-bytes-to-str-in-python3
    def convert(data):
        if isinstance(data, list):   return data[0].decode()
        if isinstance(data, bytes):  return data.decode()
        if isinstance(data, dict):   return dict(map(convert, data.items()))
        if isinstance(data, tuple):  return map(convert, data)
        return data

    return json.dumps(convert(d))
