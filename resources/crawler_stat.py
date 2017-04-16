import os
import json
import pandas as pd
import numpy as np
import re
file_path = '/home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/'


listOfStatsPerFile = list()

for filename in os.listdir(file_path):
    file_date = ""
    total_line = 0
    dnsfail = 0
    httpfail = 0
    totalerror = 0
    totalok = 0

    if filename.startswith("crawldata-"):
        file_date = re.findall('crawldata-([\d\-]+).json',filename)[0]
        line_chunk=100
        with open(os.path.join(file_path, filename), 'r') as f:
            for line in f:
                if line_chunk > 0:
                    line_chunk -= 1
                else:
                    break;
                try:
                    item = json.loads(line, encoding='utf-8')

                    if 'pk' in item and item['pk']:
                        total_line += 1

                        if item['crawl_status'] == "OK":
                            totalok += 1
                        else:
                            totalerror += 1
                            if item['crawl_status'] == "HTTPError":
                                dnsfail += 1
                            if item['crawl_status'] == "DNSLookupError":
                                httpfail += 1
                except:
                    pass
        listOfStatsPerFile.append([file_date, total_line, dnsfail, httpfail, totalerror, totalok,
                            startAlexaRank, endAlexaRank])
        print([file_date, total_line, dnsfail, httpfail, totalerror, totalok])
df = pd.DataFrame(listOfStatsPerFile,columns=['file_date', 'total_line', 'dnsfail',
            'httpfail', 'totalerror', 'totalok'])
