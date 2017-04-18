import pandas as pd
import json
import pyasn
import socket
from urllib.parse import urlparse
import numpy as np

##########ML Labeler for url string decency analysis#################
#code stolen from https://github.com/faizann24/Using-machine-learning-to-detect-malicious-URLs
import pandas as pd
import numpy as np
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import sys
import os


def getTokens(input):
    tokensBySlash = str(input.encode('utf-8')).split('/')	#get tokens after splitting by slash
    allTokens = []
    for i in tokensBySlash:
        tokens = str(i).split('-')	#get tokens after splitting by dash
        tokensByDot = []
        for j in range(0,len(tokens)):
            tempTokens = str(tokens[j]).split('.')	#get tokens after splitting by dot
            tokensByDot = tokensByDot + tempTokens
        allTokens = allTokens + tokens + tokensByDot
    allTokens = list(set(allTokens))	#remove redundant tokens
    if 'com' in allTokens:
        allTokens.remove('com')	#removing .com since it occurs a lot of times and it should not be included in our features
    return allTokens

def TL():
    allurls = './data.csv'	#path to our all urls file
    allurlscsv = pd.read_csv(allurls,',',error_bad_lines=False)	#reading file
    allurlsdata = pd.DataFrame(allurlscsv)	#converting to a dataframe

    allurlsdata = np.array(allurlsdata)	#converting it into an array
    random.shuffle(allurlsdata)	#shuffling

    y = [d[1] for d in allurlsdata]	#all labels 
    corpus = [d[0] for d in allurlsdata]	#all urls corresponding to a label (either good or bad)
    vectorizer = TfidfVectorizer(tokenizer=getTokens)	#get a vector for each url but use our customized tokenizer
    X = vectorizer.fit_transform(corpus)	#get the X vector

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)	#split into training and testing set 80/20 ratio

    lgs = LogisticRegression()	#using logistic regression
    lgs.fit(X_train, y_train)
    print(lgs.score(X_test, y_test))	#pring the score. It comes out to be 98%
    return vectorizer, lgs
vectorizer, lgs  = TL()
#example usage
#X_predict = df_network_features['url'].tolist()
#X_predict = vectorizer.transform(X_predict)
#y_Predict = lgs.predict(X_predict)
##############################################################

def getHostIP_ASN_CIDR_array(url):
    ip_addr = "N/A"
    asn = "N/A"
    cidr = "N/A"
    try:
        if not urlparse(url).scheme:
            url = "http://"+url
        if urlparse(url).hostname :
            ip_addr = socket.gethostbyname(urlparse(url).hostname)
            asn, cidr =  asndb.lookup(ip_addr)
        return [url, ip_addr, asn, cidr]
    except:
        return [url, ip_addr, asn, cidr]

#load asn db: required for ip/asn/cidr lookup
asndb_file = "ipasn_20170403.dat"
asndb = pyasn.pyasn(asndb_file)

#Collect Blacklist crawled data (500 successful crawl)
crawl_data = "/home/crawler/mlcrawler6262/crawler/bl-crawler/data/crawldata-15-04-17-1326.json"
#crawl_data = "/home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/crawldata-15-04-17-0001.json"

line_chunk = 7000

#open number of lines in dataframe
with open(crawl_data) as myfile:
    dfElement = pd.DataFrame(json.loads(next(myfile)) for x in range(line_chunk))
    dfElement = dfElement[dfElement['crawl_status']=='OK'][['url','urls','date']]
    dfElement['label'] = 'MALICIOUS'


dfElement.shape
#url_ip_map = pd.DataFrame([getHostIP_ASN_CIDR_array(url) for url in dfElement['url']], columns=['url','ip','asn','cidr'])

#Collect Whitelist crawled data (500 top alexa)
crawl_data = "/home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/crawldata-15-04-17-0001.json"
asndb_file = "/nethome/srashed3/scripts/ipasn_20170403.dat"
line_chunk = 550

#open number of lines in dataframe
with open(crawl_data) as myfile:
    dfElementWL = pd.DataFrame(json.loads(next(myfile)) for x in range(line_chunk))
    dfElementWL = dfElementWL[dfElementWL['crawl_status']=='OK'][['url','urls','date']]
    dfElementWL['label'] = 'BENIGN'
dfElementWL.shape

#Merge data frames together
dfElement = dfElement.append(dfElementWL)
dfElement.shape

#Collect features (network diversity and url decency)
#for each url, get all url inside a list(not getting js_urls as its already coming in url)
list_url_network_features = list()
for index, row in dfElement.iterrows():
    all_url_list = []
    all_url_list = row['urls']
    all_url_list.append(row['url'])
    all_url_list = set(all_url_list)
    url_ip_map = pd.DataFrame([getHostIP_ASN_CIDR_array(url) for url in all_url_list], columns=['url','ip','asn','cidr'])
    url_ip_map = url_ip_map.replace('N/A',np.NaN)
    url_ip_map = url_ip_map.dropna()

    
    mean_of_ip, median_of_ip, sd_of_ip = np.nan, np.nan, np.nan
    mean_of_cidr, median_of_cidr, sd_of_cidr = np.nan, np.nan, np.nan 
    mean_of_asn, median_of_asn, sd_of_asn = np.nan, np.nan, np.nan
    url_decency_ratio = np.nan
    
    #aggregation: network diversity based statistical feature
    temp_dfs = url_ip_map.pivot_table(index=['ip'], values=['url'], aggfunc='count')
    if temp_dfs['url'].count() > 0:
        mean_of_ip = np.mean(temp_dfs['url'].values)
        median_of_ip = np.median(temp_dfs['url'].values)
        sd_of_ip = np.std(temp_dfs['url'].values)
        
    temp_dfs = url_ip_map.pivot_table(index=['cidr'], values=['url'], aggfunc='count')
    if temp_dfs['url'].count() > 0:
        mean_of_cidr = np.mean(temp_dfs['url'].values)
        median_of_cidr = np.median(temp_dfs['url'].values)
        sd_of_cidr = np.median(temp_dfs['url'].values)
    
    temp_dfs = url_ip_map.pivot_table(index=['asn'], values=['url'], aggfunc='count')
    if temp_dfs['url'].count() > 0:
        mean_of_asn = np.mean(temp_dfs['url'].values)
        median_of_asn = np.mean(temp_dfs['url'].values)
        sd_of_asn = np.mean(temp_dfs['url'].values)
    
    #aggregation: url string based decency ratio
    X_predict = list(all_url_list)
    X_predict = vectorizer.transform(X_predict)
    y_Predict = lgs.predict(X_predict)
    url_decency_ratio = y_Predict.tolist().count('bad') / len(y_Predict)
    
    
    list_url_network_features.append([row['url'],mean_of_ip, median_of_ip, sd_of_ip, 
                                 mean_of_cidr, median_of_cidr, sd_of_cidr,
                                 mean_of_asn, median_of_asn, sd_of_asn, url_decency_ratio,row['label']])

df_network_features = pd.DataFrame(list_url_network_features, columns=['url','ip_mean','ip_median','ip_sd', 
                                                                     'cidr_mean','cidr_median','cidr_sd',
                                                                    'asn_mean', 'asn_median', 'asn_sd', 'url_decency','label'])
#save feature to file (for future use)
#df_network_features.to_csv("mlcrawler6262_feature.csv", sep=',')

df_network_features = df_network_features.merge(dfElement[['url','label']], how='inner', on='url')
df_network_features.to_csv("test_dataset.csv",sep=',')
