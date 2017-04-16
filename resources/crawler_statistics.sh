#!/bin/bash
cd /home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/

for file in ./crawldata*; do
	FILE_NAME=${file##*/}
	TOTAL_LINE=`wc -l < ${file##*/}`
	DNSFAIL_LINE=`jq 'select(.crawl_status=="DNSLookupError") | .pk' $FILE_NAME | wc -l`
	HTTPFAIL_LINE=`jq 'select(.crawl_status=="HTTPError") | .pk' $FILE_NAME | wc -l`
	TOTALERROR_LINE=`jq 'select(.crawl_status!="OK") | .pk' $FILE_NAME | wc -l`
	TOTALOK_LINE=`jq 'select(.crawl_status=="OK") | .pk' $FILE_NAME | wc -l`
	echo $FILE_NAME,$TOTAL_LINE,$DNSFAIL_LINE,$HTTPFAIL_LINE,$TOTALERROR_LINE,$TOTALOK_LINE
done

#find /home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/* -type f -name crawldata-* -printf "%f\n"
