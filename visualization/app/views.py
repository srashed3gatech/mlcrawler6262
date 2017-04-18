from flask import Flask, jsonify, render_template, request, Markup
from app import app
from urllib.request import urlopen
from datetime import datetime
import simplejson

#Escape + - && || ! ( ) { } [ ] ^ " ~ * ? : / with \

server = 'http://localhost:8983/solr/search/'
listDate = []
SOLR_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

def format_date(dt, fmt=SOLR_DATE_FORMAT):
    return datetime.strftime(dt, fmt)


@app.route('/')
@app.route('/index')
def index():
	query1K = server+'select?indent=on&fq=alexa_rank:[*%20TO%201000]&q=*:*&rows=1000000&wt=json'
	connection1K = urlopen(query1K)
	query_output1K = simplejson.load(connection1K)
	response1K = query_output1K["response"]
	response_docs1K = response1K["docs"]
	for elements in response_docs1K:
		date = elements["date"]
		date = date[0]
		if date not in listDate:
			listDate.append(date)
	ret_data = request.args.get('date')
	print(ret_data)
	if ret_data==None:
		ret_data = '"2017-04-04T00:00:00Z"'
		query1 = server+'select?indent=on&fq=date:'+ret_data+'&fq=blacklisted:false&fq=alexa_rank:[*%20TO%201000]&q=*:*&rows=1000000&wt=json'
		query2 = server+'select?indent=on&fq=date:'+ret_data+'&fq=blacklisted:true&fq=alexa_rank:[*%20TO%201000]&q=*:*&rows=1000000&wt=json'
	else:
		query1 = server+'select?indent=on&fq=date:"'+ret_data+'"&fq=blacklisted:false&fq=alexa_rank:[*%20TO%201000]&q=*:*&rows=1000000&wt=json'
		query2 = server+'select?indent=on&fq=date:"'+ret_data+'"&fq=blacklisted:true&fq=alexa_rank:[*%20TO%201000]&q=*:*&rows=1000000&wt=json'
	connection1 = urlopen(query1)
	query_output1 = simplejson.load(connection1)
	response1 = query_output1["response"]
	numFoundNotBlacklisted = response1["numFound"]
	connection2 = urlopen(query2)
	query_output2 = simplejson.load(connection2)
	response2 = query_output2["response"]
	numFoundBlacklisted = response2["numFound"]
	labels = ["Not Blacklisted", "Blacklisted"]
	values = [numFoundNotBlacklisted, numFoundBlacklisted]
	colors = [ "#F7464A", "#000000"]
	print(values)
	return render_template("index.html", values=values, labels=labels, colors=colors, listDate=listDate)


@app.route('/search', methods=['GET'])
def search():
    ret_data = request.args.get('searchText')
    query = server+'select?indent=on&fq=url:'+str(ret_data)+'&q=*:*&rows=1000000&wt=json'
    connection = urlopen(query)
    query_output = simplejson.load(connection)
    response = query_output["response"]
    data = response["docs"]
    return render_template("result.html", data=data)
    

@app.route('/top100')
def date():
	return render_template("top100.html")

@app.route('/top100/date', methods=['GET'])
def top():
	ret_data = request.args.get('searchDate')
	d = datetime.strptime(ret_data, '%m/%d/%y')
	data = []
	for rank in range(1,100):
		query = server+'select?indent=on&fq=alexa_rank:'+str(rank)+'&fq=date:"'+str(format_date(d))+'"&q=*:*&rows=1000000&wt=json'
		connection = urlopen(query)
		query_output = simplejson.load(connection)
		response = query_output["response"]
		response_docs = response["docs"]
		data += response_docs
	return render_template("result.html", data=data)

@app.route('/blacklisted', methods=['GET'])
def sector():
	query = server+'select?indent=on&fq=blacklisted:true&q=*:*&rows=1000000&wt=json'
	connection = urlopen(query)
	query_output = simplejson.load(connection)
	response = query_output["response"]
	data = response["docs"]
	return render_template("result.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)