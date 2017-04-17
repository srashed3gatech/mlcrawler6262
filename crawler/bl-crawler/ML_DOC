Machine Learning:

Data Collecation:
Blacklists are known to be malicious and we can crawl them using blacklist URLs we collected using our 4 different source. Comparing blacklist pages with Alexa top 500 would give us some insight on what differ between those two web-pages. So Blacklist sets are labeled Malicous and alexa top 500 as BENIGN.

For our system we'll consider 1 day worth of data collected for top 500 BL sits and top 500 alexa sites.

Items Considered for Feature:
Network Features - we want to see how a page links are distributed among its network space. Our idea is to see how a site can host malware in its close network proximity, may be with different domain name on same machine or same network (asn/cidr).

One other important and easy extractable features are urls from a page, assuming URLs tends to allure users to end-up downloading malware and most malicicious url words construction is different than benign one, we can leverage a ml labeler described in [1] and label if an url is bad or good.

Features:
We collected ip/asn/cidr for each URLs we found in a page (including the crawled domain).
For each page we then calculate:
  1. mean of count of urls hosted on same X (IP, ASN, CIDR)
  2. median of count of urls hosted on same X (IP, ASN, CIDR)
  3. standard deviation of count of urls hosted on same X (IP, ASN, CIDR)
This gives us 9 features for our ML.

Then we go for URL decency check and collect: Ratio of URL decency = (total bad url / (total good url + total bad url))

ML Classifier:
We used SVM (linear) to feed the extracted features and result ROC. 
ROC having 68% True Positive rate.

Refernce:
[1] https://github.com/faizann24/Using-machine-learning-to-detect-malicious-URLs
