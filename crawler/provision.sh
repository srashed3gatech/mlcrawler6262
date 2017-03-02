#!/usr/bin/env bash

# Setup config files for user
touch ~/.bash_aliases
touch ~/.bash_profile

# Create tools dir
mkdir ~/tools

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

## 3. Grab Nutch 1.12 and Solr 6.4.1
cd ~
wget http://mirror.reverse.net/pub/apache/nutch/1.12/apache-nutch-1.12-bin.tar.gz
wget http://www.trieuvan.com/apache/lucene/solr/6.4.1/solr-6.4.1.tgz

## 4. Extract to dirs
mkdir -p tools/nutch
mkdir -p tools/solr
tar -xf apache-nutch-1.12-bin.tar.gz -C tools/nutch --strip-components=1
tar -xf solr-6.4.1.tgz -C tools/solr --strip-components=1

## 5. Add both to PATH
### Use `sed` to append a line to end of file
echo 'export PATH="~/tools/nutch/bin/:$PATH"' >> ~/.bash_profile
echo 'export PATH="~/tools/solr/bin/:$PATH"' >> ~/.bash_profile
source ~/.bash_profile

# Clone crawler from Github
cd ~/tools
git clone https://github.com/srashed3gatech/mlcrawler6262.git

# Install pip and install dependencies (OpenSSL, etc.)
cd mlcrawler6262/crawler/crawler-scrapy
sudo apt-get -y install python3-pip libffi-dev libssl-dev libxml2-dev \
                        libxslt1-dev libjpeg8-dev zlib1g-dev

# Install crawler deps
sudo pip3 install -r requirements.txt

# Add Mongo install
