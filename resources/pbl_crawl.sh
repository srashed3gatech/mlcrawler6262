#!/bin/bash
cd ~/pbl_daily
curl -o psh_$(date '+%y-%m-%d').txt "https://hosts-file.net/psh.txt"
curl -o exp_$(date '+%y-%m-%d').txt "https://hosts-file.net/exp.txt"
curl -o emd_$(date '+%y-%m-%d').txt "https://hosts-file.net/emd.txt"
curl -o fsa_$(date '+%y-%m-%d').txt "https://hosts-file.net/fsa.txt"
curl -o domains_$(date '+%y-%m-%d').txt "http://mirror2.malwaredomains.com/files/domains.txt"
curl -o suspiciousdomains_$(date '+%y-%m-%d').txt "https://isc.sans.edu/feeds/suspiciousdomains_Medium.txt"
