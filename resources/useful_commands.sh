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

## configuring dnsmasq for dns caching
sudo vim /etc/NetworkManager/dnsmasq.d/cache
#write following on the cache file
cache-size=1000
#restart network manager to affect cache
sudo restart network-manager
#check whats going on - should see what dns server its using
sudo zgrep dnsmasq /var/log/syslog* | grep dnsmasq
