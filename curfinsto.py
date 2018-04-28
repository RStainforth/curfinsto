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

def get_stock_info( symbol ):

	response = requests.get("https://web.tmxmoney.com/quote.php?qm_symbol="+str(symbol))
	data = response.text
	soup = BeautifulSoup( response.text, "lxml" )
	
	# Get the volume value
	my_divs = soup.findAll('div', {"class": "quote-volume volumeLarge"})
	volume = get_volume( my_divs )
	volume = volume.replace(",","")
	print ( "Volume is: " + str( volume ) )
	
	# Get the volume value
	my_values = soup.findAll('div', {"class": "quote-price priceLarge"})
	value = get_value( my_values )
	print ( "Value is: " + str( value ) )
	
	response = requests.get("https://web.tmxmoney.com/quote.php?qm_symbol="+str(symbol))
	data = response.text
	soup = BeautifulSoup( response.text, "lxml" )
	#print( soup )
	
	# Get the dividend return
	#my_values = soup.findAll('div', {"class": "quote-tabs-content"})
	#value = get_dividend( my_values )
	#print ( "Dividend is: " + str( value ) )
	
	rows = soup.find_all( "table", {"class": "detailed-quote-table"} )
	for row in rows:
		cols = row.find_all("tr")
		for col in cols:
			cells = col.find_all("td")
			
			# Get the field name of the table value (index 0)
			str_index = cells[0].get_text()
			
			# The value of the field (index 1)
			str_value = cells[1].get_text()
			# strips whitespace from the string
			str_value = "".join(str_value.split())
			# Removes commas from numbers.
			str_value = str_value.replace(",", "")

			# Print the information.
			print(str_index + " " + str_value)
	
if __name__ == '__main__':

	# example: ./tmx_scrap "A" "A_symbols"

	in_macro   = str(sys.argv[0])   # Input File
	letter     = str(sys.argv[1])   # Letter to scrape
	out_file   = str(sys.argv[2])   # Output file
	
	alphabet = []
	names = []
	symbols = []
	for letter in range(65, 91): alphabet.append(chr(letter))
	for alpha in range( 0,len(alphabet) ):
		response = requests.get("https://www.tsx.com/json/company-directory/search/tsx/"+str(alphabet[alpha])+"?")
		print( "Visiting: " + "https://www.tsx.com/json/company-directory/search/tsx/"+str(alphabet[alpha])+"?" )
		data = response.text
		d = json.loads(str(data))
		for sym in range( len(d['results']) ):
			curName = str(d['results'][sym]['name'])
			names.append( curName )
			curSym = str(d['results'][sym]['symbol'])
			symbols.append( curSym )
	
	with open( out_file, 'w' ) as out_f:
		for i in range( 0, len( names ) ):
			out_f.write( names[ i ] + "," + symbols[ i ] + "\n" )	
	out_f.close()
