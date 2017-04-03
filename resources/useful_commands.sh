##03/07/2017## Deployment of scrapy and solr
#prereq - solr running fine, git clone available
#create a solr core
sudo apt-get install python-dev libevent-dev libssl-dev
sudo pip install pyasn1 --upgrade
sudo pip install pydispatch
sudo pip2 install -r requirements.txt
sudo pip install Twisted==16.4.1

#mkdir logs under alexatop directory

#how to push json file into solr
java -Durl="http://localhost:8983/solr/crawler/update" -Dtype=application/json -jar /opt/solr/example/exampledocs/post.jar /opt/crawler/crawler/crawler-scrapy/alexatop/output/results-2017-03-09T22-17-39.json

#run scrapy in background and note pid in run.pid
nohup scrapy crawl alexa > /dev/null 2>&1 & echo $! > run.pid
#see log of scrapy
tail -f /home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/logs/`ls -1t /home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/logs | head -1`
#see data of scrapy
tail -f /home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/`ls -1t /home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data | head -1`

## configuring dnsmasq for dns caching
sudo vim /etc/NetworkManager/dnsmasq.d/cache
#write following on the cache file
cache-size=1000000
#restart network manager to affect cache
sudo restart network-manager
#check whats going on - should see what dns server its using
sudo zgrep dnsmasq /var/log/syslog* | grep dnsmasq
#######https://www.rootusers.com/how-to-configure-local-dns-query-cache-in-linux/
srashed3@acs-8:~$ sudo vim /etc/NetworkManager/dnsmasq.d/cache
srashed3@acs-8:~$ sudo vim /etc/NetworkManager/NetworkManager.conf
srashed3@acs-8:~$ sudo vim /etc/resolv.conf
srashed3@acs-8:~$ sudo netstat -antup | grep dnsmasq
tcp        0      0 127.0.1.1:53            0.0.0.0:*               LISTEN      22969/dnsmasq
udp        0      0 127.0.1.1:53            0.0.0.0:*                           22969/dnsmasq

srashed3@acs-8:~$ sudo zgrep dnsmasq /var/log/syslog* | grep dnsmasq
/var/log/syslog.1:Apr  1 07:07:49 acs-8 dnsmasq[22969]: setting upstream servers from DBus
/var/log/syslog.1:Apr  1 07:07:49 acs-8 dnsmasq[22969]: exiting on receipt of SIGTERM
/var/log/syslog.1:Apr  1 07:07:50 acs-8 NetworkManager[24658]: <info> DNS: loaded plugin dnsmasq
/var/log/syslog.1:Apr  1 07:07:51 acs-8 NetworkManager[24658]: <info> DNS: starting dnsmasq...
/var/log/syslog.1:Apr  1 07:07:51 acs-8 NetworkManager[24658]: <warn> dnsmasq not available on the bus, can't update servers.
/var/log/syslog.1:Apr  1 07:07:51 acs-8 NetworkManager[24658]: <error> [1491044871.219307] [nm-dns-dnsmasq.c:396] update(): dnsmasq owner not found on bus: Could not get owner of name 'org.freedesktop.NetworkManager.dnsmasq': no such name
/var/log/syslog.1:Apr  1 07:07:51 acs-8 NetworkManager[24658]: <warn> DNS: plugin dnsmasq update failed
/var/log/syslog.1:Apr  1 07:07:51 acs-8 dnsmasq[24669]: started, version 2.68 cachesize 10000
/var/log/syslog.1:Apr  1 07:07:51 acs-8 dnsmasq[24669]: compile time options: IPv6 GNU-getopt DBus i18n IDN DHCP DHCPv6 no-Lua TFTP conntrack ipset auth
/var/log/syslog.1:Apr  1 07:07:51 acs-8 dnsmasq[24669]: DBus support enabled: connected to system bus
/var/log/syslog.1:Apr  1 07:07:51 acs-8 dnsmasq[24669]: warning: no upstream servers configured
/var/log/syslog.1:Apr  1 07:07:51 acs-8 dnsmasq[24669]: cleared cache
/var/log/syslog.1:Apr  1 07:07:51 acs-8 NetworkManager[24658]: <warn> dnsmasq appeared on DBus: :1.2602
/var/log/syslog.1:Apr  1 07:07:51 acs-8 dnsmasq[24669]: setting upstream servers from DBus
/var/log/syslog.1:Apr  1 07:07:51 acs-8 dnsmasq[24669]: using nameserver 143.215.143.72#53
/var/log/syslog.1:Apr  1 07:07:51 acs-8 dnsmasq[24669]: using nameserver 130.207.165.170#53
/var/log/syslog.1:Apr  1 07:07:51 acs-8 dnsmasq[24669]: using nameserver 130.207.17.22#53
/var/log/syslog.1:Apr  1 07:07:51 acs-8 dnsmasq[24669]: using nameserver 130.207.17.21#53


#increasing max file open limit (ulimit -n) for crawler user
#http://stackoverflow.com/questions/21515463/how-to-increase-maximum-file-open-limit-ulimit-in-ubuntu
srashed3@acs-8:~$ sudo vim /etc/security/limits.conf
*               soft    nofile          65535
*               hard    nofile          65535
#change this to effect ulimit without restart (then logout and login)
srashed3@acs-8:~$ sudo vim /etc/pam.d/common-session
session     required    pam_limits.so

#how to run scrapy into backend while you logged off
#http://askubuntu.com/questions/8653/how-to-keep-processes-running-after-ending-ssh-session
#source srcenv
#http://askubuntu.com/questions/8653/how-to-keep-processes-running-after-ending-ssh-session
#tmux
#leave/detach the tmux session by typing Ctrl+B and then D
#/opt/crawler/crawler/crawler-scrapy/alexatop$ nohup scrapy crawl alexa > /dev/null 2>&1 & echo $! > run.pid

#solr 6
#create a new core with data driven schema
bin/solr create_core -c crawler
bin/solr create_core -c blacklist

#python with solr - library install simplejson
pip3 install simplejson

#use jq to get file stats
#get primary key count from crawled data
jq .'pk' /home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/crawldata-01-04-17.json | wc -l
#get count of pk where there was error
jq 'select(.crawl_status!="OK") | .pk' /home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/crawldata-01-04-17.json | wc -l
#get dnslookup error
jq 'select(.crawl_status=="DNSLookupError") | .pk' /home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/crawldata-01-04-17.json | wc -l

#other jq queries (conditional)
srashed3@acs-8:~$ jq 'select(.crawl_status=="OK") | .pk' /home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/crawldata-01-04-17.json | wc -l
4689
srashed3@acs-8:~$ jq 'select(.crawl_status!="OK") | .pk' /home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/crawldata-01-04-17.json | wc -l
3436

#cronjob config
crontab -e
1 0 * * * /home/crawler/bin/run_crawler_cron.sh > /home/crawler/crawler_run_history.log 2>&1
crawler@acs-8:~/bin$ cat /home/crawler/bin/run_crawler_cron.sh
#!/bin/bash
. ~/.venv/main/bin/activate
cd ~/mlcrawler6262/crawler/crawler-scrapy/alexatop/
nohup scrapy crawl alexa & echo "STARTING CRAWLER AT PID# $! @ $(date)"
