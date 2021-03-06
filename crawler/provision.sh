#!/usr/bin/env bash

# Update Ubuntu packages
sudo apt-get -y update

# Create new user for running the crawler
sudo adduser --gecos "" --disabled-password crawler
echo "crawler:crawler" | sudo chpasswd
HOME=/home/crawler

# Install Solr
## 1. Install JRE 8x
sudo add-apt-repository -y ppa:openjdk-r/ppa
sudo apt-get -y install openjdk-8-jre

## 2. Set JAVA_HOME
sudo sed -i '$ a JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64/"' /etc/environment
source /etc/environment

## 3. Install Solr 6.4.2
cd $HOME
wget http://archive.apache.org/dist/lucene/solr/6.4.2/solr-6.4.2.tgz
tar -xvf solr-6.4.2.tgz
rm solr-6.4.2.tgz
mv solr-6.4.2 solr

## 4. Setup a symlink in bin directory
mkdir bin
ln -s $HOME/solr/bin/solr bin/solr
ln -s $HOME/solr/bin/post bin/post

# Clone GH repo locally
cd $HOME
sudo apt-get -y install git
git clone https://github.com/srashed3gatech/mlcrawler6262.git

# Install pip and dependencies for Scrapy (OpenSSL, etc.)
cd mlcrawler6262/crawler/crawler-scrapy
sudo apt-get -y install python3-pip libffi-dev libssl-dev libxml2-dev \
                        libxslt1-dev libjpeg8-dev zlib1g-dev

# Setup a local virtual env for packages
sudo pip3 install virtualenv
cd $HOME
mkdir .venv && virtualenv .venv/main
source .venv/main/bin/activate

# Setup dependencies for Scrapy
cd $HOME/mlcrawler6262/crawler/crawler-scrapy
pip install -r requirements.txt

echo 'Done!'
