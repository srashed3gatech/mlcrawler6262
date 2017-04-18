#!/usr/bin/env bash

## Tested on Ubuntu 14.04 LTS

# Update Ubuntu packages
sudo apt-get -y update
sudo apt-get -y upgrade

# Install Solr
## 1. Install JRE 8x
sudo apt-get -y install openjdk-8-jre

## 2. Set JAVA_HOME
sed -i '$ a JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64/"' /etc/environment
source /etc/environment

## 3. Install Solr 6.4.2
mkdir -p ~/tools && cd ~/tools
wget http://archive.apache.org/dist/lucene/solr/6.4.2/solr-6.4.2.tgz
tar -xvfz solr-6.4.2.tgz
mv solr-6.4.2 solr

## 4. Add Solr to $PATH
echo 'export PATH="~/tools/solr/bin/:$PATH"' >> ~/.bash_profile
source ~/.bash_profile

# Clone this repo
sudo apt-get -y install git
cd ~
git clone https://github.com/srashed3gatech/mlcrawler6262.git

# Install pip and dependencies (OpenSSL, etc.)
sudo apt-get -y install python3-pip libffi-dev libssl-dev libxml2-dev \
                        libxslt1-dev libjpeg8-dev zlib1g-dev

# Setup a local virtual env for packages
sudo pip3 install virtualenv
mkdir ~/.venv
cd ~/.venv && virtualenv main

# Install Python dependencies under virtualenv
cd ~/mlcrawler6262
source ~/.venv/main/bin/activate
pip install -r requirements.txt

echo 'Done!'
