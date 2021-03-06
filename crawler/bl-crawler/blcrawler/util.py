import os
import csv
import json
import time
import hashlib
import requests

from datetime import datetime
from urllib.parse import urlparse
from zipfile import ZipFile

ALEXA_LIST_URL = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'

SOLR_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

def format_date(dt, fmt=SOLR_DATE_FORMAT):
    return datetime.strftime(dt, fmt)

def get_today():
    date = datetime.now().replace(hour=0, second=0, minute=0)
    return format_date(datetime.now())

def extract_url(url):
    p = urlparse(url)
    return p.netloc

def grab_alexa(count=0,start_idx=0,directory=''):
    '''Grabs Alexa top 1M list and returns it as a OrderedDict int (rank) -> str (url)'''
    # Grab ZIP and store on disk
    resp = requests.get(ALEXA_LIST_URL)
    archive = resp.content

    save_zip = os.path.join(directory, 'top1m-{0}.zip'.format(time.strftime('%d-%m-%y')))

    with open(save_zip, 'wb') as f:
        f.write(archive)

    data = []

    # Unzip, read, and parse CSV
    with ZipFile(save_zip, 'r') as zf:
        lines = [line.decode() for line in zf.open('top-1m.csv', 'r').readlines()]

        if count > 0:
            lines = lines[start_idx:count+start_idx]
        else:
            raise Exception('Please pass in a positive count.')

        # Parse CSV and convert to dict format
        for row in csv.reader(lines):
            data.append('http://' + row[1])

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
