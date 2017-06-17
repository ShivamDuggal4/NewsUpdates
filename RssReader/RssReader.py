import urllib2
import os
import re, json
import bs4
from bs4 import BeautifulSoup
import datetime,time
import csv
import sys
from pyquery import PyQuery as pq
import urllib2
import traceback
import requests
from datetime import timedelta,datetime
from dateutil import parser
from goose import Goose
import feedparser
from time import mktime
from datetime import datetime
import urlparse
import easygui
import time
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from smtplib import SMTPException
import socket
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest




class FrequencySummarizer:
  def __init__(self, min_cut=0.1, max_cut=0.9):
    """
     Initilize the text summarizer.
     Words that have a frequency term lower than min_cut 
     or higer than max_cut will be ignored.
    """
    self._min_cut = min_cut
    self._max_cut = max_cut 
    self._stopwords = set(stopwords.words('english') + list(punctuation))

  def _compute_frequencies(self, word_sent):
    """ 
      Compute the frequency of each of word.
      Input: 
       word_sent, a list of sentences already tokenized.
      Output: 
       freq, a dictionary where freq[w] is the frequency of w.
    """
    freq = defaultdict(int)
    for s in word_sent:
      for word in s:
        if word not in self._stopwords:
          freq[word] += 1
    # frequencies normalization and fitering
    m = float(max(freq.values()))
    for w in freq.keys():
      freq[w] = freq[w]/m
      if freq[w] >= self._max_cut or freq[w] <= self._min_cut:
        del freq[w]
    return freq

  def summarize(self, text, n):
    """
      Return a list of n sentences 
      which represent the summary of text.
    """
    sents = sent_tokenize(text)
    assert n <= len(sents)
    word_sent = [word_tokenize(s.lower()) for s in sents]
    self._freq = self._compute_frequencies(word_sent)
    ranking = defaultdict(int)
    for i,sent in enumerate(word_sent):
      for w in sent:
        if w in self._freq:
          ranking[i] += self._freq[w]
    sents_idx = self._rank(ranking, n)    
    return [sents[j] for j in sents_idx]

  def _rank(self, ranking, n):
    """ return the first n sentences with highest ranking """
    return nlargest(n, ranking, key=ranking.get)



def message(heading,data):
	SERVER = "smtp.gmail.com:587"
	FROM = ""
	TO = [""]
	SUBJECT = heading
	TEXT = "Automated E-Mail informing about the result."
	message = data
	username="" 
	password=""			   
	server = smtplib.SMTP_SSL('mtp.googlemail.com', 465)
	server.login(username,password)
	server.sendmail(FROM, TO, message)
	server.quit()
	return


def getHost(link):
   parsed_uri = urlparse.urlparse(link )
   domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
   return domain

def call_goose(url,timestamp,client):
	link = url
	f = open('outputFile.txt','a')

	check = set()

	try:
		g = Goose()
		article = g.extract(url=link)
	except:
		f = open('unscraped_links.txt','a')
		f.write(str(link)+'|')
		f.close()
	
	try:
		heading = article.title.encode('ascii','ignore')
	except:
		heading = ''
		print traceback.format_exc()	

	try:
		contents = article.cleaned_text.encode('ascii','ignore')
	except:
		contents = ''
		print traceback.format_exc()
			
	try:
		tags = article.meta_keywords.encode('ascii','ignore')
	except:
		tags = ''
		print traceback.format_exc()
			
	try:
		img_link = article.top_image.src
		#print img_link
	except:
		img_link = ''
		print traceback.format_exc()

			
	try:
		description = article.meta_description.encode('ascii','ignore')
	except:
		description = ''
		print traceback.format_exc()
			
		
	#sno = int('8'+str(random.randint(10000000,99999999)))
				
	try:
		ss = ''
		'''
		to print the data to a file
		
		print link
		fs = FrequencySummarizer()
		print >>f, heading
		for s in fs.summarize(contents, 1):
			ss = s
			print >>f,  '*',s
		
		'''

		fs = FrequencySummarizer()
		for s in fs.summarize(contents, 1):
			ss = s

		if heading not in check:
			easygui.msgbox(ss, title=heading)
			check.add(heading)
			#message(heading,ss)
		
		
	except:
		print traceback.format_exc()
		f = open('unscraped_links.txt','a')
		f.write(str(link)+'|')
		f.close()



def call_rss(url):
	try:
		feed = feedparser.parse(url)
		
		client = getHost(url)
		
		for item in feed[ "items"]:
			timestamp = datetime.fromtimestamp(mktime(item['published_parsed']))	
			itemlink = item['link']
			#print itemlink
			call_goose(itemlink,timestamp,client)

	except:
		print traceback.format_exc()
		f = open('unscraped_links.txt','a')
		f.write(str(url)+'|')
		f.close()
		


if __name__ == "__main__":
	

	for arg in sys.argv:
		print sys.argv[1],sys.argv[2]


	f = open('conf.json')
	config_file = json.load(f)

	if sys.argv[1] == "thehindu":
		config_file[0]["link"] =  "http://www.thehindu.com/" + str(sys.argv[2]) + "/?service=rss"	
		
	f = open('conf.json','w')
	json.dump(config_file,f)
	f.close()
	

	f = open("conf.json")
	config = json.load(f)

	while(1):
		for i,section in enumerate(config):
			#print section["link"]
			call_rss(section["link"])

		time.sleep(20);
			