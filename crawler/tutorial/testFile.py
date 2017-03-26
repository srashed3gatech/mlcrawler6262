from urllib.parse import urlsplit

url = "http://stackoverflow.com/questions/9626535/get-domain-name-from-url"
base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
domain = "{0.netloc}".format(urlsplit(url))
print(domain)
