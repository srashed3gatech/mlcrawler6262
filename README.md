# MLCrawler 6262 Project Repository

## Prerequisites

Run the provision script located at the root of this repo to install all dependencies:

`$ ./provision.sh`

The script does the following:

1. Upgrade Ubuntu packages
2. Install OpenJDK 8 and add JAVA_HOME to /etc/environment
3. Installs Apache Solr 6.4.2 to `~/tools/solr` and adds Solr binaries to `$PATH`
4. Install Git and clone this repo to `~/mlcrawler6262`
5. Install `pip` and create a virtualenv under `~/.venv`
6. Navigate to repo root directory and install dependencies from `requirements.txt`

Note that the script requires `sudo` access to install packages.

## Quick Start

1. Source into Python virtualenv: `source ~/.venv/main/bin/activate`
2. Navigate to crawler directory: `cd ~/mlcrawler6262/crawler/crawler-scrapy/alexatop/`
3. Modify the variables at the top of `run_alexa.py` to configure which parts of the Alexa top 1M to crawl (see next section)
4. Run the crawler: `python run_alexa.py`
  - Data stored in `data/`; logs in `logs/`
5. Grab blacklists for the day and parse them: `cd ~/mlcrawler6262/crawler/blacklist && python blacklist_parser.py`
  - Blacklists stored in `~/mlcrawler6262/crawler/blacklist`
6. Once crawl is complete, navigate to `~/mlcrawler6262/analysis`
7. In `blacklist_check.py`, modify `DAYS_CRAWLED` variable to reflect crawl data available
  - List days in `dd-mm-yy` format
8. Run `blacklist_check.py` to (1) build URL lookup tables and crawl indexes, (2) collect crawl stats, and (3) compute blacklist diffs
  - Lookup tables under `lookup/`; stats and crawl indexes under data dir (`~/mlcrawler6262/crawler/crawler-scrapy/alexatop/data`)
9. Run Apache Solr: `solr start`, then create a new core named "search": `solr create_core -c search`
10. Summarize crawl data for all days: `cd ~/mlcrawler6262/analysis && python extract_data.py`
  - Note that script is configured by default to extract top 1000, bottom 1000, and blacklist hits
11. Store summarized data into the Solr core: `post -c search ~/mlcrawler6262/analysis/output/*.json`
12. Access Solr through the web interface or query it at http://localhost:8983/solr.
13. Start visualization web app: `cd ~/mlcrawler6262/visualization && python run.py`
  - Server starts listening on http://localhost:5000

The following sections go into each step in more detail.

## Running the Crawler

The file `~/mlcrawler6262/crawler/crawler-scrapy/alexatop/run_alexa.py` runs the Scrapy crawler. You can change the variables `ALEXA_MAX`, `START_RANK`, and `CRAWL_NUM` to customize the crawl. The script splits the crawl into equal sized URL chunks according to `CRAWL_NUM` (as discussed in report).

The following commands will start running the Scrapy crawler according to the variables listed above:

```
$ source ~/.venv/bin/activate
$ cd ~/mlcrawler6262/crawler/crawler-scrapy/alexatop/
$ python run_alexa.py
```

The following are directories of interest:

- Crawl data is stored in `~/mlcrawler6262/crawler/crawler-scrapy/alexatop/data`
- Scrapy output logs are stored in `~/mlcrawler6262/crawler/crawler-scrapy/alexatop/logs`
- The top 1M `.zip` file for each crawl is stored in `~/mlcrawler6262/crawler/crawler-scrapy/alexatop/urls`

The crawler logic itself is located in `~/mlcrawler6262/crawler/crawler-scrapy/alexatop/alexatop/spiders/alexa_spider.py`. Some extra utility functions -- including a function that grabs the Alexa top 1M list -- is located in `~/mlcrawler6262/crawler/crawler-scrapy/alexatop/alexatop/util.py`.

### Tuning the System

Use local DNS cache & increase max open file limit:

```## configuring dnsmasq for dns caching
$ sudo vim /etc/NetworkManager/dnsmasq.d/cache
#write following on the cache file
cache-size=1000000
#restart network manager to affect cache
$ sudo restart network-manager
#check if its working
$ sudo zgrep dnsmasq /var/log/syslog* | grep dnsmasq

#increasing max file open limit (ulimit -n) for crawler user
$ sudo vim /etc/security/limits.conf
*               soft    nofile          65535
*               hard    nofile          65535
#change this to effect ulimit without restart (then logout and login)
$ sudo vim /etc/pam.d/common-session
session     required    pam_limits.so
```

## Blacklist Parsing

The blacklist parser script is located at `~/mlcrawler6262/crawler/blacklist/blacklist_parser`. The script spits out a CSV file with each row as `URL, type`. `type` refers to the type of malicious activity on the page, according to the blacklist. The filename is `blacklist-dd-mm-yy.csv`.

The script can be run in two modes:

1. With no arguments, the script retrieves the latest blacklists from 6 public sources, and combines them into a CSV.
2. Pass it the blacklist text files -- as retrieved from the configured sources -- and it spits out a CSV.
  - This is what's done in  `~/mlcrawler6262/resources/pbl_crawl.sh`.
  - Note that the date format in the shell script is `yy-mm-dd`. You can change its format, but make sure to update the date string on line 158 of `blacklist_parser.py`!

## Post-Crawl Analysis

First, we need to create a Solr core called `search` that will store the summarized data:

```
# Start Solr on port 8983 (default)
$ solr start
$ solr create_core -c search
```

### Blacklist Diff Check

Next, configure the `DAYS_CRAWLED` list on line 10 of `~/mlcrawler6262/analysis/blacklist_check.py`. It needs to reflect what data is actually available in the crawler's data directory (`~/mlcrawler6262/crawler/crawler-scrapy/alexatop/data`). Finally, make sure that the variables `RANK_DELTA` and `RANK_MAX` reflect the number of URLs per crawl data file and the number of total URLs crawled, respectively. In our case, they are set to 100,000 (10 files, 100k URLs each) and 1,000,000 (for Alexa top 1M).

Now simply run `~/mlcrawler6262/analysis/blacklist_check.py` and check stdout for results. You can modify the function `main()` to write results to a file if you prefer. Note that the script will take a while to run the first time due to the function `collect_metadata`. This function is where the following takes place:

1. Building the URL lookup table (stored in `~/mlcrawler6262/analysis/lookup`)
2. Building the crawl index (stored in `~/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/crawl_index`)
3. Collecting crawl stats (stored in `~/mlcrawler6262/crawler/crawler-scrapy/alexatop/stats`)

However, after the first run, the script should run finish quickly.

### Data Extraction and Summarization

The logic for this step of the analysis is all located in `~/mlcrawler6262/analysis/extract_data.py`. The script iterates over the `DAYS_CRAWLED` variable above and performs the following for each day crawled:

1. Extracts and summarizes the data for the Alexa top 1000 URLs.
2. Extracts and summarizes the data for the Alexa bottom 1000 URLs.
3. Extracts and summarizes the data for all crawled URLs from the Alexa top 1M that are **also** in today's blacklist.

The crawl index for the current day is used to provide (almost) random access to the raw crawl data (see `grab_ranks()`).

The key function in this script is `parse_data()`. Be sure to refer to it to see what features are extracted from each crawled page.

The script outputs 3 JSON files for each day: one for top 1000, one for bottom 1000, and one for the blacklisted URLs. The JSON files are dumped into the folder `~/mlcrawler6262/analysis/output`.

## Search API

Setting up the search API is quite easy. We just need to load the summarized data into Apache Solr.

So navigate to `~/mlcrawler6262/analysis/output` and run the Apache Solr `post` utility. Use the command below to load all of the JSON files into the `search` core:

`$ post -c search ~/mlcrawler6262/analysis/output/*.json`

Now all the data is loaded into Solr for use by the visualization UI.

## Visualization UI

The visualization interface depends on Flask (and its dependencies) which are installed if you ran `provision.sh`.

To run the Flask web server, navigate to `~/mlcrawler6262/visualization` and run:

```
$ source ~/.venv/main/bin/activate
$ python run.py
```

The server will start listening on `localhost:5000`.

## Repo Structure

### Analysis
 - blacklist_check.py : shows blacklist deferral that we also crawled in our dataset
 - extract_data.py : stats generation from raw crawled document

### Crawler
- provision_main.sh : provision system necessary to run everything
- blacklist
    - blacklist_parser.py : parse and generate single blacklist csv from collect source data with different formatting
    - blacklist_solr.py : post blacklist data into SOLR
- crawler-scrapy
  - alexatop
    - alexatop
      - spiders
        - alexa_spider.py : Alexa Spider to crawl alexa list
      - items.py : Crawled Document class
      - middlewares.py
      - pipelines.py
      - settings.py : conifguration of log and data directory
      - util.py : helper function on parsing crawled urls
    - run_alexa.py : divide 1M alexa list into 10 different files and initiate crawler in seperate process
    - scrapy.cfg : scrapy project config
    - data : data repo for crawled items
    - logs : scrapy run log

### Resources
  - pbl_crawl.sh: cronbased daily blacklist fetch script
  - run_alexa_crawl.sh : cronbased daily alexa startup script
  - crawler_stat.py : generate crawl trend graph from stats generated by extract_data.py at alanysis folder

### ML Classifier for Blacklist URLs
  - Check `README.md` under `/ml_poc` to see how we ran our POC on crawled data to get Receiver Operating Characteristics
