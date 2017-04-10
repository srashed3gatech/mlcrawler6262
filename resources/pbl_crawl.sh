#!/bin/bash
# Grab blacklist text files for future reference
mkdir -p pbl_daily
cd pbl_daily

curl -o psh_$(date '+%Y-%m-%d').txt "https://hosts-file.net/psh.txt"
curl -o exp_$(date '+%Y-%m-%d').txt "https://hosts-file.net/exp.txt"
curl -o emd_$(date '+%Y-%m-%d').txt "https://hosts-file.net/emd.txt"
curl -o fsa_$(date '+%Y-%m-%d').txt "https://hosts-file.net/fsa.txt"
curl -o domains_$(date '+%Y-%m-%d').txt "http://mirror2.malwaredomains.com/files/domains.txt"
curl -o suspiciousdomains_$(date '+%Y-%m-%d').txt "https://isc.sans.edu/feeds/suspiciousdomains_Medium.txt"

# Parse them into a single list for easier use
# Filename: blacklist-yyyy-mm-dd.csv
python3 ../../crawler/blacklist/blacklist_parser.py *.txt

cd ..
