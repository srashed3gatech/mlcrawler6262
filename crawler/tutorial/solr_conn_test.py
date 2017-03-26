from urllib.request import *
import simplejson
from urllib.parse import urlsplit

url = "http://stackoverflow.com/questions/9626535/get-domain-name-from-url"
base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
domain = ["{0.netloc}".format(urlsplit(url))]
domain.append('www.google.com')
domain.append('00035.accountant')
domain_simplejson = '+OR+'.join(domain)
domain_pysolr = ' OR '.join(domain)
testQ = 'economics.stackexchange.com+OR+chat.stackexchange.com+OR+www.stackoverflowbusiness.com+OR+meta.superuser.com+OR+scifi.stackexchange.com+OR+data.stackexchange.com+OR+puzzling.stackexchange.com+OR+stackoverflow.blog+OR+academia.stackexchange.com+OR+stackexchange.com+OR+mathematica.stackexchange.com+OR+travel.stackexchange.com+OR+superuser.com+OR+cdn.sstatic.net+OR+gardening.stackexchange.com+OR+ell.stackexchange.com+OR+askubuntu.com+OR+cooking.stackexchange.com+OR+ajax.googleapis.com+OR+mathoverflow.net+OR+creativecommons.org+OR+www.paypal.com+OR+math.stackexchange.com+OR+vegetarianism.stackexchange.com+OR+blog.stackoverflow.com+OR+outdoors.stackexchange.com+OR+worldbuilding.stackexchange.com+OR+wordpress.stackexchange.com+OR+stackoverflow.com+OR+scotthelme.co.uk+OR+codegolf.stackexchange.com'
query = 'http://localhost:8983/solr/blacklist/select?q=url:(%s)&rows=0&start=0&wt=json'%testQ
connection = urlopen(query)
response = simplejson.load(connection)
print(response['response']['numFound'], 'document found.')


# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pysolr
SOLR_CORE_URL = 'http://localhost:8983/solr/blacklist/'

solr = pysolr.Solr(SOLR_CORE_URL, timeout=10)
#result = solr.search(q='url:(%s)'%domain_pysolr,**{'rows':0})


testQ2 = 'stackoverflow.com OR blog.stackoverflow.com OR askubuntu.com OR scifi.stackexchange.com OR cdn.sstatic.net OR chat.stackexchange.com OR outdoors.stackexchange.com OR superuser.com OR writers.stackexchange.com OR workplace.stackexchange.com OR english.stackexchange.com OR unix.stackexchange.com OR codereview.stackexchange.com OR www.stackoverflowbusiness.com OR travel.stackexchange.com OR mathoverflow.net OR puzzling.stackexchange.com OR cs.stackexchange.com OR creativecommons.org OR worldbuilding.stackexchange.com OR stackexchange.com OR ajax.googleapis.com OR codegolf.stackexchange.com OR electronics.stackexchange.com OR www.paypal.com OR stackoverflow.blog OR scotthelme.co.uk OR matheducators.stackexchange.com OR math.stackexchange.com OR data.stackexchange.com OR academia.stackexchange.com OR economics.stackexchange.com OR politics.stackexchange.com OR cooking.stackexchange.com OR meta.superuser.com'
result = solr.search(q='url:(%s)'%testQ2,**{'rows':0})
print(result.hits)
print(len(result))
#print("url:(%s)"%domain_pysolr)
