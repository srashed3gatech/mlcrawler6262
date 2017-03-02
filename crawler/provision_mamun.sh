#!/usr/bin/env bash

# Setup config files for user
touch ~/.bash_aliases
touch ~/.bash_profile

# Update Ubuntu packages
sudo apt-get -y update
sudo apt-get -y upgrade

# Install Docker
## 1. Setup Docker repo
sudo apt-get -y install apt-transport-https \
                software-properties-common \
                ca-certificates
curl -fsSL https://yum.dockerproject.org/gpg | sudo apt-key add
apt-key fingerprint 58118E89F3A912897C070ADBF76221572C52609D
sudo apt-get -y install software-properties-common
sudo add-apt-repository \
     "deb https://apt.dockerproject.org/repo/ \
     ubuntu-$(lsb_release -cs) \
     main"

## 2. Install Docker (for real now)
sudo apt-get update
sudo apt-get -y install docker-engine

# Setup `docker` user group, avoid running as root
# TODO

# Grab Postgres Docker container
# => Source: https://hub.docker.com/_/postgres/
sudo docker pull postgres

# Run Postgres
# => Container named "pgdb"
# => Username: postgres, pass: mysecretpassword
sudo docker run --name pgdb \
                -e POSTGRES_PASSWORD=mysecretpassword \
                -d postgres

# Setup easy shortcut for Postgres
echo 'alias pgshell="sudo docker run -it --rm --link pgdb:postgres postgres psql -h postgres -U postgres"' > ~/.bash_aliases
source ~/.bashrc

# TODO Configure PG to run on boot
# Guide: https://docs.docker.com/engine/admin/host_integration/

# Install Apache Nutch and Solr
## 1. Install JRE 8x
sudo apt-get -y install openjdk-8-jre

## 2. Set JAVA_HOME
sed -i '$ a JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64/"' /etc/environment
source /etc/environment

## 3. Grab Nutch 1.10 and Solr 4.10
#download & install
mkdir -p ~/tools
cd ~/tools
wget http://archive.apache.org/dist/nutch/1.10/apache-nutch-1.10-bin.tar.gz
tar -xvfz apache-nutch-1.10-bin.tar.gz
mv apache-nutch-1.10-bin nutch

wget http://archive.apache.org/dist/lucene/solr/4.10.1/solr-4.10.1.tgz
tar -xvfz solr-4.10.1.tgz
mv solr-4.10.1 solr

# Clone repo locally
sudo apt-get -y install git
cd ~/tools
git clone https://github.com/srashed3gatech/mlcrawler6262.git
BASEDIR=~/tools/mlcrawler6262

#configure nutch-site
mv ~/tools/nutch/conf/nutch-site.xml ~/tools/nutch/conf/nutch-site.xml.bak
cp $BASEDIR/resources/nutch/config/nutch-site.xml ~/tools/nutch/conf/nutch-site.xml
cp $BASEDIR/resources/nutch/config/regex-urlfilter.txt ~/tools/nutch/conf/regex-urlfilter.txt

#configure seed
mkdir -p ~/tools/nutch/conf/urls
cp $BASEDIR/resources/nutch/config/seed.txt ~/tools/nutch/conf/urls/seed.txt

#configure solr site
cp -R $BASEDIR/resources/solr/nutch-example ~/tools/solr/example/solr/

## 5. Add Nutch and Solr to $PATH
### Use `sed` to append a line to end of file
echo 'export PATH="~/tools/nutch/bin/:$PATH"' >> ~/.bash_profile
echo 'export PATH="~/tools/solr/bin/:$PATH"' >> ~/.bash_profile
source ~/.bash_profile

chown -R ubuntu:ubuntu ~/tools

#start solr
solr start

#run crawling
cd ~/tools/nutch
bin/crawl -i -D solr.server.url=http://localhost:8983/solr/nutch-example conf/urls crawl 1
