<h1> MLCrawler 6262 Project Repository </h1>
**Analysis**
 -- blacklist_check.py : shows blacklist deferral that we also crawled in our dataset
 -- extract_data.py : stats generation from raw crawled document


**Crawler:**
|-- provision_main.sh : provision system necessary to run everything
|-- blacklist
    |-- blacklist_parser.py : parse and generate single blacklist csv from collect source data with different formatting
    |-- blacklist_solr.py : post blacklist data into SOLR
|-- crawler-scrapy
  |-- alexatop
    |-- alexatop
      |-- spiders
        |-- alexa_spider.py : Alexa Spider to crawl alexa list
      |-- items.py : Crawled Document class
      |-- middlewares.py
      |-- pipelines.py
      |-- settings.py : conifguration of log and data directory
      |-- util.py : helper function on parsing crawled urls
    |-- run_alexa.py : divide 1M alexa list into 10 different files and initiate crawler in seperate process
    |-- scrapy.cfg : scrapy project config
    |-- data : data repo for crawled items
    |-- logs : scrapy run log

**Resources:**
  - pbl_crawl.sh: cronbased daily blacklist fetch script
  - run_alexa_crawl.sh : cronbased daily alexa startup script


.
 * [tree-md](./tree-md)
 * [dir2](./dir2)
   * [file21.ext](./dir2/file21.ext)
   * [file22.ext](./dir2/file22.ext)
   * [file23.ext](./dir2/file23.ext)
 * [dir1](./dir1)
   * [file11.ext](./dir1/file11.ext)
   * [file12.ext](./dir1/file12.ext)
 * [file_in_root.ext](./file_in_root.ext)
 * [README.md](./README.md)
 * [dir3](./dir3)
