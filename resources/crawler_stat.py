import os
import json
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

file_path = '/home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/stats/'


df_allStats = pd.DataFrame()

for filename in os.listdir(file_path):
    if filename.startswith("stats-"):
        file_date = re.findall('stats-([\d\-]+)',filename)[0]
        statfile = os.path.join(file_path, filename)
        df = pd.read_csv(statfile)
        df['date'] = pd.to_datetime(file_date,format='%d-%m-%y')
        df_allStats = pd.concat([df, df_allStats])

df_allStats = df_allStats.set_index(['date'])
f = plt.figure()
plt.title('Daily Crawl Trend', color='black')
df_allStats.plot(kind='line', ax=f.gca(), logy=True)
ax = f.gca()
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
plt.show()
