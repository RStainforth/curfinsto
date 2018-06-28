# Copyright Rob Stainforth
#
#!/usr/bin/env python
# TMX Scraper for stock symbols and their rate of return.
# Inspired by following webpage:
# #https://stackoverflow.com/questions/8049520/web-scraping-javascript-page-with-python
#https://stackoverflow.com/questions/10309550/python-beautifulsoup-iterate-over-table
#https://stackoverflow.com/questions/37926684/entering-value-into-search-bar-and-downloading-output-from-webpage
###################################
###################################
# import dryscrape
# from bs4 import BeautifulSoup
# session = dryscrape.Session()
# session.visit(my_url)
# response = session.body()
# soup = BeautifulSoup(response)
# soup.find(id="intro-text")
## Result:
# <p id="intro-text">Yay! Supports javascript</p>
###################################
###################################

import dryscrape
from bs4 import BeautifulSoup
import os
import sys
import json
import requests
import string
import datetime
import glob
import time
#import shutil
	
################################################
################################################

def get_value( value_divs ):

	_value = "N/A"
	for div in value_divs:
		_value = "".join(((div.get_text()).split("$")[1]).split())
		
	return _value

def get_volume( volume_divs ):

	volume_value = "N/A"
	for div in volume_divs:
		volume_value = "".join(((div.get_text()).split(':')[1]).split()) 
		
	return volume_value
	
def get_dividend( dividend_divs ):

	dividend_value = "N/A"
	for div in dividend_divs:
		dividend_value = "".join(((div.get_text()).split(':')[1]).split())
		print ( div ) 
		
	return dividend_value
	
################################################
################################################

def get_variable_index( variable ):

	if ( variable == "volume" ): return 0
	elif ( variable == "value" ): return 1
	elif ( variable == "open" ): return 2
	elif ( variable == "high" ): return 3
	elif ( variable == "sharesout" ): return 4
	elif ( variable == "beta" ): return 5
	elif ( variable == "prevclose" ): return 6
	elif ( variable == "low" ): return 7
	elif ( variable == "marketcap" ): return 8
	elif ( variable == "vwap" ): return 9
	elif ( variable == "dividend" ): return 10
	elif ( variable == "divfrequency" ): return 11
	elif ( variable == "peratio" ): return 12
	elif ( variable == "eps" ): return 13
	elif ( variable == "yield" ): return 14
	elif ( variable == "exdivdate" ): return 15
	elif ( variable == "pbratio" ): return 16
	elif ( variable == "exchange" ): return 17
	else: 
		print( "Error, unknown variable" )
		print( "Options are: " )
		print( "volume" )
		print( "value" )
		print( "open" )
		print( "high" )
		print( "sharesout" )
		print( "beta" )
		print( "prevclose" )
		print( "low" )
		print( "marketcap" )
		print( "vwap" )
		print( "dividend" )
		print( "divfrequency" )
		print( "peratio" )
		print( "eps" )
		print( "yield" )
		print( "exdivdate" )
		print( "pbratio" )
		print( "exchange" )
		return -1
	

################################################
################################################

def get_stock_info( symbol ):

	stock_info = []
	
	response = ''
	while response == '':
		try:
			response = requests.get("https://web.tmxmoney.com/quote.php?qm_symbol="+str(symbol))
			break
		except:
			print( "Error in connection, will sleep" )
			time.sleep(5)
		
	data = response.text
	soup = BeautifulSoup( response.text, "lxml" )
	
	# Get the volume value
	my_divs = soup.findAll('div', {"class": "quote-volume volumeLarge"})
	volume = get_volume( my_divs )
	volume = volume.replace(",","")
	volume = "Volume: " + str( volume )
	stock_info.append( volume )
	
	# Get the volume value
	my_values = soup.findAll('div', {"class": "quote-price priceLarge"})
	value = get_value( my_values )
	value = "Value: " + str( value )
	stock_info.append( value )
	
	response = ''
	while response == '':
		try:
			response = requests.get("https://web.tmxmoney.com/quote.php?qm_symbol="+str(symbol))
			break
		except:
			print( "Error in connection, will sleep" )
			time.sleep(5)
		
	data = response.text
	soup = BeautifulSoup( response.text, "lxml" )
	
	rows = soup.find_all( "table", {"class": "detailed-quote-table"} )
	for row in rows:
		cols = row.find_all("tr")
		for col in cols:
			cells = col.find_all("td")
			
			# Get the field name of the table value (index 0)
			str_index = cells[0].get_text()
			str_index = "".join(str_index.split())
			
			# The value of the field (index 1)
			str_value = cells[1].get_text()
			# strips whitespace from the string
			str_value = "".join(str_value.split())
			# Removes commas from numbers.
			str_value = str_value.replace(",", "")

			# Print the information.
			cur_out = str_index + " " + str_value
			stock_info.append( cur_out )
			
	for x in range( 0, len(stock_info) ):
		tmp_str = stock_info[x].encode('ascii')
		stock_info[x] = tmp_str
			
	return stock_info
	
################################################
################################################

def get_stocks_by_letter( my_letter, out_file ):
	
	alphabet = []
	names = []
	symbols = []
	for letter in range(65, 91): 
		alphabet.append(chr(letter))
	for alpha in range( 0,len(alphabet) ):
		if ( my_letter != alphabet[alpha] ): continue
		response = ''
		while response == '':
			try:
				response = requests.get("https://www.tsx.com/json/company-directory/search/tsx/"+str(alphabet[alpha])+"?")
				print( "Visiting: " + "https://www.tsx.com/json/company-directory/search/tsx/"+str(alphabet[alpha])+"?" )
				break
			except:
				print( "Error in connection, will sleep" )
				time.sleep(5)

			
		data = response.text
		d = json.loads(str(data))
		for sym in range( len(d['results']) ):
			curName = str(d['results'][sym]['name'])
			names.append( curName )
			curSym = str(d['results'][sym]['symbol'])
			symbols.append( curSym )
	
	with open( out_file, 'w' ) as out_f:
		for i in range( 0, len( names ) ):
			print( "Getting info for stock: " + str(symbols[ i ]) + ", " + str(i) + "/" + str(len(names)) )
			cur_info = get_stock_info( str(symbols[ i ]) )
			out_f.write( names[ i ] + " | " + symbols[ i ] + " | " )
			for v in range( 0, len( cur_info ) ):
				out_f.write( cur_info[ v ] + " | " )
			out_f.write( "\n" );	
	out_f.close()
	return symbols
