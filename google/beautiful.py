#!/usr/bin/env python
 
import sys
import urllib2
import re
import sqlite3
import datetime
 
from BeautifulSoup import BeautifulSoup  # available at: http://www.crummy.com/software/BeautifulSoup/
 
conn = sqlite3.connect("espionage.sqlite")
conn.row_factory = sqlite3.Row
 
def get_google_search_results(keywordPhrase):
	"""make the GET request to Google.com for the keyword phrase and return the HTML text
	"""
	url='http://www.google.com/search?hl=en&q=' + '+'.join(keywordPhrase.split())
	req = urllib2.Request(url)
	req.add_header('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.29 Safari/525.13')
	page = urllib2.urlopen(req)
	HTML = page.read()
	return HTML
 
def scrape_ads(text, phraseID):
	"""Scrape the text as HTML, find and parse out all the ads and store them in a database
	"""
	soup = BeautifulSoup(text)
	#get the ads on the right hand side of the page
	ads = soup.find(id='rhsline').findAll('li')
	position = 0
	for ad in ads:
		position += 1
 
		#display url
		parts = ad.find('cite').findAll(text=True)
		site = ''.join([word.strip() for word in parts]).strip()
		ad.find('cite').replaceWith("")
 
		#the header line
		parts = ad.find('a').findAll(text=True)
		title = ' '.join([word.strip() for word in parts]).strip()
 
		#the destination URL
		href = ad.find('a')['href']
		start = href.find('&q=')
		if start != -1 :
			dest = href[start+3:]
		else :
			dest = None
			print 'error', href
 
		ad.find('a').replaceWith("")
 
		#body of ad
		brs = ad.findAll('br')
		for br in brs:
			br.replaceWith("%BR%")
		parts = ad.findAll(text=True)
		body = ' '.join([word.strip() for word in parts]).strip()
		line1 = body.split('%BR%')[0].strip()
		line2 = body.split('%BR%')[1].strip()
 
		#see if the ad is in the database
		c = conn.cursor()
		c.execute('SELECT adID FROM AdTable WHERE destination=? and title=? and line1=? and line2=? and site=? and phraseID=?', (dest, title, line1, line2, site, phraseID))
		result = c.fetchall() 
		if len(result) == 0:
			#NEW AD - insert into the table
			c.execute('INSERT INTO AdTable (`destination`, `title`, `line1`, `line2`, `site`, `phraseID`) VALUES (?,?,?,?,?,?)', (dest, title, line1, line2, site, phraseID))
			conn.commit()
			c.execute('SELECT adID FROM AdTable WHERE destination=? and title=? and line1=? and line2=? and site=? and phraseID=?', (dest, title, line1, line2, site, phraseID))
			result = c.fetchall()
		elif len(result) > 1:
			continue
 
		adID = result[0]['adID']
 
		c.execute('INSERT INTO ShowTime (`adID`,`date`,`time`, `position`) VALUES (?,?,?,?)', (adID, datetime.datetime.now(), datetime.datetime.now(), position))
 
 
def do_all_keywords():
	c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS "main"."AdTable" ("adID" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL , "title" VARCHAR, "line1" VARCHAR, "line2" VARCHAR, "site" VARCHAR, "destination" VARCHAR NOT NULL , "phraseID" INTEGER NOT NULL )')
        c.execute('CREATE TABLE IF NOT EXISTS "main"."ShowTime" ("adID" INTEGER PRIMARY KEY NOT NULL , "date" DATETIME, "time" DATETIME, "position" INTEGER)')
        c.execute('CREATE TABLE IF NOT EXISTS "main"."KeywordList" ("phraseID" INTEGER PRIMARY KEY NOT NULL , "keywordPhrase" VARCHAR)')
        c.execute('CREATE TABLE IF NOT EXISTS "main"."CPCEstimate" ("phraseID" INTEGER NOT NULL , "date" DATETIME NOT NULL , "cpc" DOUBLE, PRIMARY KEY ("phraseID", "date"))')
	c.execute('SELECT * FROM KeywordList')
	result = c.fetchall()
	for row in result:
		html = get_google_search_results(row['keywordPhrase'])
		scrape_ads(html, row['phraseID'])
 
if __name__ == '__main__' :
	do_all_keywords()
