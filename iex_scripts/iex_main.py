#!/usr/bin/env python
# Author: J. Walker
# Date: Feb 11th, 2019
# Brief: A short script that uses the 'iex_tools' module to 
#        extract stock information from the IEX API
# Usage: ./iex_main
# Would get all new stock information

import iex_tools
import os
import sys
#import pymongo
#from pymongo import MongoClient

################################################
################################################

if __name__ == '__main__':

    #Flags for inserting specific data types
    insert_symbols = False
    insert_prices = False
    insert_dividends = False
    insert_earnings = False
    insert_financials = True

    db = iex_tools.get_mongodb()

    #Get list of all stock symbols
    if insert_symbols:
        symbols = iex_tools.iex_get_symbols(ref_type="cs")
        symbols_spy = iex_tools.iex_get_symbols(ref_symbol="SPY")
        symbols.reset_index(drop=True, inplace=True)
        symbols_spy.reset_index(drop=True, inplace=True)
        #print( symbols )
        symbols = symbols.append(symbols_spy, ignore_index=True)
        symbols.reset_index(drop=True, inplace=True)
        symbols_len = len(symbols.index)
        #print( symbols )
        #If different to existing list the upload new list
        for index, symbol in symbols.iterrows():
            #Exclude forbidden characters
            forbidden = ["#"]
            if forbidden in symbol["symbol"]:
                continue
            #print( symbol )
            #db.iex_symbols.insert_one( symbol.to_dict() )
            #is different to mongodb?
            if iex_tools.mdb_new_symbol( symbol ):
                #insert symbol document
                print( str(index) + "/" + str(symbols_len) + " Inserting new symbol: " + symbol["symbol"] )
                db.iex_symbols.insert_one( symbol.to_dict() )
            else:
                print( str(index) + "/" + str(symbols_len) + " Symbol " + symbol["symbol"] + " already exists" )

    #If new prices exist then upload them
    if insert_prices:
        mdb_symbols = iex_tools.mdb_get_symbols()
        #print(mdb_symbols)
        for index, mdb_symbol in mdb_symbols.iterrows():
            #print(mdb_symbol)
            iex_chart = iex_tools.iex_get_chart( mdb_symbol["symbol"], ref_range='2y' )
            mdb_chart = iex_tools.mdb_get_chart( mdb_symbol["symbol"] )
            #print( iex_chart )
            #print( mdb_chart )
            #Remove existing dates
            #print( iex_chart["date"] )
            #print( mdb_chart["date"] )
            #print( ~iex_chart["date"].isin(mdb_chart["date"]) )
            #Remove any existing dates
            if not mdb_chart.empty and not iex_chart.empty:
                iex_chart = iex_chart[ ~iex_chart["date"].isin(mdb_chart["date"]) ]
            #print( iex_chart )

            if not iex_chart.empty:
                print( str(index) + "/" + str(len(mdb_symbols.index)) + " Inserting chart for " + mdb_symbol["symbol"] )
                #print( iex_chart )
                #print( iex_chart.to_dict('records') )
                #db.iex_charts.insert_many( iex_chart.to_dict('records') )
            else:
                print( str(index) + "/" + str(len(mdb_symbols.index)) + " No new data for " + mdb_symbol["symbol"] )

    #If new dividends exist then upload them
    if insert_dividends:
        mdb_symbols = iex_tools.mdb_get_symbols()
        #print(mdb_symbols)
        for index, mdb_symbol in mdb_symbols.iterrows():
            iex_dividends = iex_tools.iex_get_dividends( mdb_symbol["symbol"], ref_range='2y' )
            mdb_dividends = iex_tools.mdb_get_dividends( mdb_symbol["symbol"] )
            #print( iex_dividends )
            #print( mdb_dividends )
            #Remove existing dates
            #print( iex_dividends["exDate"] )
            #print( mdb_dividends["exDate"] )
            #print( ~iex_dividends["exDate"].isin(mdb_dividends["exDate"]) )
            #Remove any existing dates
            if not mdb_dividends.empty and not iex_dividends.empty:
                iex_dividends = iex_dividends[ ~iex_dividends["exDate"].isin(mdb_dividends["exDate"]) ]
            #print( iex_dividends )

            if not iex_dividends.empty:
                print( str(index) + "/" + str(len(mdb_symbols.index)) + " Inserting dividend for " + mdb_symbol["symbol"] )
                #print( iex_dividends )
                #print( iex_dividends.to_dict('records') )
                db.iex_dividends.insert_many( iex_dividends.to_dict('records') )
            else:
                print( str(index) + "/" + str(len(mdb_symbols.index)) + " No new data for " + mdb_symbol["symbol"] )
    
    #If new earnings exist then upload them
    if insert_earnings:
        mdb_symbols = iex_tools.mdb_get_symbols()
        #print(mdb_symbols)
        for index, mdb_symbol in mdb_symbols.iterrows():
            iex_earnings = iex_tools.iex_get_earnings( mdb_symbol["symbol"] )
            mdb_earnings = iex_tools.mdb_get_earnings( mdb_symbol["symbol"] )
            #print( iex_earnings )
            #print( mdb_earnings )
            #Remove existing dates
            #print( iex_earnings["fiscalEndDate"] )
            #print( mdb_earnings["fiscalEndDate"] )
            #print( ~iex_earnings["fiscalEndDate"].isin(mdb_earnings["fiscalEndDate"]) )
            #Remove any existing dates
            if not mdb_earnings.empty and not iex_earnings.empty:
                iex_earnings = iex_earnings[ ~iex_earnings["fiscalEndDate"].isin(mdb_earnings["fiscalEndDate"]) ]
            #print( iex_earnings )

            if not iex_earnings.empty:
                print( str(index) + "/" + str(len(mdb_symbols.index)) + " Inserting earnings for " + mdb_symbol["symbol"] )
                #print( iex_earnings )
                #print( iex_earnings.to_dict('records') )
                db.iex_earnings.insert_many( iex_earnings.to_dict('records') )
            else:
                print( str(index) + "/" + str(len(mdb_symbols.index)) + " No new data for " + mdb_symbol["symbol"] )

    #If new financials exist then upload them
    if insert_financials:
        mdb_symbols = iex_tools.mdb_get_symbols()
        #print(mdb_symbols)
        for index, mdb_symbol in mdb_symbols.iterrows():
            print( "Getting data for " + mdb_symbol["symbol"] )
            iex_financials = iex_tools.iex_get_financials( mdb_symbol["symbol"] )
            mdb_financials = iex_tools.mdb_get_financials( mdb_symbol["symbol"] )
            #print( iex_financials )
            #print( mdb_financials )
            #Remove existing dates
            #print( iex_financials["reportDate"] )
            #print( mdb_financials["reportDate"] )
            #print( ~iex_financials["reportDate"].isin(mdb_financials["reportDate"]) )
            #Remove any existing dates
            if not mdb_financials.empty and not iex_financials.empty:
                iex_financials = iex_financials[ ~iex_financials["reportDate"].isin(mdb_financials["reportDate"]) ]
            #print( iex_financials )

            if not iex_financials.empty:
                print( str(index) + "/" + str(len(mdb_symbols.index)) + " Inserting financials for " + mdb_symbol["symbol"] )
                #print( iex_financials )
                #print( iex_financials.to_dict('records') )
                db.iex_financials.insert_many( iex_financials.to_dict('records') )
            else:
                print( str(index) + "/" + str(len(mdb_symbols.index)) + " No new data for " + mdb_symbol["symbol"] )

    #Calculate PE, ROE and mcap for each stock on a given date
    #Store 2 days - delete first day after adding new one
    #Filter by mcap
    #How many stocks in the universe for different mcap values
    #What are the mcaps for different stock variants?
    #Find top 30 stocks for given mcap minimum
    #Calculate portfolio value
    # * Pick n mcap limits
    # * Buy x shares of value ~$10,000
    # * Store shares, value, total and percentage change

    #Key stats
    #/stock/aapl/stats
    #marketcap
    #latestEPS
    #returnOnEquity trailing 12 months
    #sharesOutstanding - can also calculate from EPS and netIncome?

    #Symbols available
    #/ref-data/symbols
    #Only type=cs
    #For S&P 500 use ETF SPY? type=et

    #Keep track of corporate actions
    #/ref-data/daily-list/corporate-actions

    #iex_tools.sandbox()



    #stock_letter = str(sys.argv[1])   # Stock Symbol to request
    #print( "Requested information for symbol with letter: " + str(stock_letter) )
    #stock = iex_tools
    #get_by_letter_output = stock.get_stocks_by_letter( str(stock_letter), str(stock_letter)+"_stocks.txt" )
    #symbol_list = get_by_letter_output[0]
    #for sym in range (len(symbol_list)):
    #        stock_info = stock.get_stock_info( symbol_list[ sym ] )[0]
    #        print( "Stock info for " + symbol_list[ sym ] )
    #        print( stock_info )
    #        print( "-----------------------------" )

    #documents = get_by_letter_output[1]

    #print( documents )

    #print( "Inserting documents..." )
    #db = iex_tools.get_mongodb_connection()
    #db.insert_many(documents)
    #print( "Documents inserted." )



    #stock_info = stock.get_stock_info( str(stock_symbol) )[0]
    #for x in range (len(stock_info)):
    #        print( stock_info[ x ] ) 
