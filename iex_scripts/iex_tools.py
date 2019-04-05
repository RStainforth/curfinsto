#!/usr/bin/env python
# Author: J. Walker
# Date: Feb 11th, 2019
# Brief: Toolkit to access the IEX API and data stored in MongoDB.

import os
import sys
import json
import requests
import string
import datetime
import glob
import time
import pymongo
from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING
import numpy
import pandas
from iex import reference
from iex import Stock

################################################
# General functions
################################################

# reorder columns
def set_column_sequence(dataframe, seq, front=True):
    '''Takes a dataframe and a subsequence of its columns,
       returns dataframe with seq as first columns if "front" is True,
       and seq as last columns if "front" is False.
    '''
    cols = seq[:] # copy so we don't mutate seq
    for x in dataframe.columns:
        if x not in cols:
            if front: #we want "seq" to be in the front
                #so append current column to the end of the list
                cols.append(x)
            else:
                #we want "seq" to be last, so insert this
                #column in the front of the new column list
                #"cols" we are building:
                cols.insert(0, x)
    return dataframe[cols]


################################################
# IEX interfacing functions
################################################
        
def iex_get_symbols(ref_symbol=None, ref_type=None):

    reference.output_format = 'dataframe'
    symbols = reference.symbols()
    
    if ref_symbol is not None:
        symbols = symbols[symbols.symbol == ref_symbol]
    if ref_type is not None:
        symbols = symbols[symbols.type == ref_type]
    
    return symbols

def iex_get_company(ref_symbol):

    stock = Stock( ref_symbol )
    company = stock.company_table()
    #print( company )
    #remove unnecesary data
    company.drop(["exchange","website","CEO","issueType"], axis=1, errors='ignore', inplace=True)
    #add symbol name
    #print( company )
    if not company.empty:
        company = set_column_sequence(company, ["symbol","companyName","industry","description","sector"])
        #print( company )

    return company

def iex_get_chart(ref_symbol, ref_range='1m'):

    stock = Stock( ref_symbol )
    chart = stock.chart_table(ref_range)
    #print( chart )
    #remove unnecesary data
    chart.drop(["high","low","volume","unadjustedVolume","change","changePercent","vwap","label","changeOverTime"], axis=1, errors='ignore', inplace=True)
    #add symbol name
    #print( chart )
    if not chart.empty:
        chart_len = len( chart.index )
        chart_arr = [ref_symbol] * chart_len
        #print( chart_arr )
        chart.insert(loc=0, column='symbol', value=chart_arr)
        chart = set_column_sequence(chart, ["symbol","date"])
        #print( chart )

    return chart

def iex_get_dividends(ref_symbol, ref_range='1m'):

    stock = Stock( ref_symbol )
    dividends = stock.dividends_table(ref_range)
    #print( dividends )
    #remove unnecesary data
    dividends.drop(["recordDate","declaredDate","flag","type","qualified","indicated"], axis=1, errors='ignore', inplace=True)
    #add symbol name
    #print( dividends )
    if not dividends.empty:
        dividends_len = len( dividends.index )
        dividends_arr = [ref_symbol] * dividends_len
        #print( dividends_arr )
        dividends.insert(loc=0, column='symbol', value=dividends_arr)
        dividends = set_column_sequence(dividends, ["symbol","exDate","paymentDate","amount"])
        #print( dividends )

    return dividends

def iex_get_earnings(ref_symbol):

    stock = Stock( ref_symbol )
    earnings = stock.earnings_table()
    #print( earnings_dict )
    #remove unnecesary data
    #print( earnings_dict.get("earnings") )
    #earnings = pandas.DataFrame.from_dict(earnings_dict.get("earnings"))
    earnings.drop(["consensusEPS","estimatedEPS","numberOfEstimates","EPSSurpriseDollar","yearAgoChangePercent","estimatedChangePercent","symbolId"], axis=1, errors='ignore', inplace=True)
    #add symbol name
    #print( earnings )
    if not earnings.empty:
        earnings_len = len( earnings.index )
        earnings_arr = [ref_symbol] * earnings_len
        #print( earnings_arr )
        earnings.insert(loc=0, column='symbol', value=earnings_arr)
        earnings = set_column_sequence(earnings, ["symbol","actualEPS","announceTime","EPSReportDate","fiscalPeriod","fiscalEndDate"])
        #print( earnings )

    return earnings

def iex_get_financials(ref_symbol):

    stock = Stock( ref_symbol )
    financials = stock.financials_table()
    #print( stock.financials() )
    #print( financials_dict )
    #remove unnecesary data
    #print( financials_dict.get("financials") )
    #financials = pandas.DataFrame.from_dict(financials_dict.get("financials"))
    #financials.drop(["consensusEPS","estimatedEPS","numberOfEstimates","EPSSurpriseDollar","yearAgoChangePercent","estimatedChangePercent","symbolId"], axis=1, errors='ignore', inplace=True)
    #add symbol name
    #print( financials )
    if not financials.empty:
        financials_len = len( financials.index )
        financials_arr = [ref_symbol] * financials_len
        #print( financials_arr )
        financials.insert(loc=0, column='symbol', value=financials_arr)
        financials = set_column_sequence(financials, ["symbol","reportDate"])
        #print( financials )

    return financials

#Sandbox function for testing only
def sandbox():

    reference.output_format = 'dataframe'
    symbols = reference.symbols()

    symbols = symbols[symbols.type == 'cs']

    symbols.reset_index(drop=True, inplace=True)
    symbols = symbols[0:100]
    symbols_copy = symbols

    for index, symbol in symbols_copy.iterrows():
        stock = Stock(symbol["symbol"])
        marketcap = stock.stats()["marketcap"]
        print( marketcap )
        print( stock.company()["companyName"] )
        print( stock.company()["sector"] )
        if marketcap < 50000000:
            print( symbol["symbol"] )
            symbols.drop(index, axis=0, inplace=True)

    symbols.reset_index(drop=True, inplace=True)

    print( symbols )

#Another sandbox function
def sandbox2():

    query = { "symbol": "WAB#" }
    #print( query )

    db = get_mongodb()

    db.iex_symbols.delete_one(query)




################################################
# MongoDB interfacing functions
################################################

def get_mongodb():

    connection_params = {
        'user': 'jwalker',
        'password': 'R0bandJohn',
        'host': 'ds235877.mlab.com',
        'port': 35877,
        'namespace': 'diywealth',
    }

    connection = MongoClient(
        'mongodb://{user}:{password}@{host}:'
        '{port}/{namespace}'.format(**connection_params)
    )

    db = connection.diywealth

    return db

def mdb_new_symbol( symbol ):

    query = { "symbol": symbol["symbol"] }
    #print( query )

    db = get_mongodb()

    results = db.iex_symbols.find( query ).sort("date", ASCENDING)

    entry_match = False

    #Does most recent entry in mongoDB match IEX?
    for doc in results:
        if (doc.get("iexId") == symbol["iexId"] and
            doc.get("isEnabled") == symbol["isEnabled"] and
            doc.get("name") == symbol["name"] and
            doc.get("type") == symbol["type"]):
            entry_match = True
        else:
            entry_match = False

    #print( entry_match )
    return not entry_match

def mdb_get_symbols():

    db = get_mongodb()

    results = db.iex_symbols.aggregate([
        { "$sort": { "date": DESCENDING } },
        { "$group": {
            "_id": "$symbol",
            "symbols": { "$push": "$$ROOT" }
            }
        },
        { "$replaceRoot": {
            "newRoot": { "$arrayElemAt": ["$symbols", 0] }
            }
        },
        { "$sort": { "symbol": ASCENDING } }
    ])
    #results = results.sort("symbol", ASCENDING)

    symbols = pandas.DataFrame()
    for doc in results:
        #print( doc )
        #print( pandas.DataFrame.from_dict(doc, orient='index').T )
        symbols = symbols.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )
        #print( symbols )
        #index = index+1

    symbols.drop("_id", axis=1, inplace=True)
    symbols = symbols[symbols.isEnabled != False]
    symbols.reset_index(drop=True, inplace=True)
    #print( symbols )

    return symbols

def mdb_get_company(symbol):

    db = get_mongodb()

    query = { "symbol": { "$in": symbol } }

    results = db.iex_company.find( query ).sort("symbol", ASCENDING)

    company = pandas.DataFrame()
    for doc in results:
        #print( doc )
        #print( pandas.DataFrame.from_dict(doc, orient='index').T )
        company = company.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )
        #print( symbols )
        #index = index+1

    company.drop("_id", axis=1, errors='ignore', inplace=True)
    #symbols = symbols[symbols.isEnabled != False]
    company.reset_index(drop=True, inplace=True)
    #print( chart )

    return company

#when = "after"
#when = "latest"
def mdb_get_chart(ref_symbol, ref_date = "1990-01-01", when = "after"):

    db = get_mongodb()

    query = []

    gte_date = (pandas.Timestamp(ref_date) + pandas.DateOffset(days=-100)).strftime('%Y-%m-%d')

    if when == "after":
        query = { "symbol": { "$in": ref_symbol },
                    "date": { "$gte": ref_date } }
    else:
        query = [
                    { "$match": { "symbol": { "$in": ref_symbol },
                                    "date": { "$lte": ref_date },
                                    "date": { "$gte": gte_date } } },
                    { "$sort": { "date": DESCENDING } },
                    { "$group": {
                        "_id": "$symbol",
                        "symbols": { "$push": "$$ROOT" }
                        }
                    },
                    { "$replaceRoot": {
                        "newRoot": { "$arrayElemAt": ["$symbols", 0] }
                        }
                    },
                    { "$sort": { "symbol": ASCENDING } }
                ]

    #print( query )

    results = []

    if when == "after":
        results = db.iex_charts.find( query ).sort("date", DESCENDING)
    else:
        results = db.iex_charts.aggregate( query )

    chart = pandas.DataFrame()
    for doc in results:
        #print( doc )
        #print( pandas.DataFrame.from_dict(doc, orient='index').T )
        chart = chart.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )
        #print( symbols )
        #index = index+1

    chart.drop("_id", axis=1, errors='ignore', inplace=True)
    #symbols = symbols[symbols.isEnabled != False]
    chart.reset_index(drop=True, inplace=True)
    #print( chart )

    return chart
   
#when = after
#when = latest
def mdb_get_dividends(ref_symbol, ref_date = "1900-01-01", when = "after"):

    db = get_mongodb()

    query = []

    if when == "after":
        query = { "symbol": { "$in": ref_symbol },
                    "exDate": { "$gte": ref_date } }
    else:
        query = [
                    { "$match": { "symbol": { "$in": ref_symbol },
                                    "exDate": { "$lte": ref_date } } },
                    { "$sort": { "exDate": DESCENDING } },
                    { "$group": {
                        "_id": "$symbol",
                        "symbols": { "$push": "$$ROOT" }
                        }
                    },
                    { "$replaceRoot": {
                        "newRoot": { "$arrayElemAt": ["$symbols", 0] }
                        }
                    },
                    { "$sort": { "symbol": ASCENDING } }
                ]
        #print( query )

    results = []

    if when == "after":
        results = db.iex_dividends.find( query ).sort("exDate", DESCENDING)
    else:
        results = db.iex_dividends.aggregate( query )

    dividends = pandas.DataFrame()
    for doc in results:
        #print( doc )
        #print( pandas.DataFrame.from_dict(doc, orient='index').T )
        dividends = dividends.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )
        #print( symbols )
        #index = index+1

    dividends.drop("_id", axis=1, errors='ignore', inplace=True)
    #symbols = symbols[symbols.isEnabled != False]
    dividends.reset_index(drop=True, inplace=True)
    #print( dividends )

    return dividends

#when = after
#when = latest
def mdb_get_earnings(ref_symbol, ref_date = "1900-01-01", when = "after"):

    db = get_mongodb()

    query = []

    if when == "after":
        query = { "symbol": { "$in": ref_symbol },
                    "fiscalEndDate": { "$gte": ref_date } }
    else:
        query = [
                    { "$match": { "symbol": { "$in": ref_symbol },
                                    "fiscalEndDate": { "$lte": ref_date } } },
                    { "$sort": { "fiscalEndDate": DESCENDING } },
                    { "$group": {
                        "_id": "$symbol",
                        "symbols": { "$push": "$$ROOT" }
                        }
                    },
                    { "$replaceRoot": {
                        "newRoot": { "$arrayElemAt": ["$symbols", 0] }
                        }
                    },
                    { "$sort": { "symbol": ASCENDING } }
                ]
    #print( query )

    results = []

    if when == "after":
        results = db.iex_earnings.find( query ).sort("fiscalEndDate", DESCENDING)
    else:
        results = db.iex_earnings.aggregate( query )

    earnings = pandas.DataFrame()
    for doc in results:
        #print( doc )
        #print( pandas.DataFrame.from_dict(doc, orient='index').T )
        earnings = earnings.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )
        #print( symbols )
        #index = index+1

    earnings.drop("_id", axis=1, errors='ignore', inplace=True)
    #symbols = symbols[symbols.isEnabled != False]
    earnings.reset_index(drop=True, inplace=True)
    #print( earnings )

    return earnings

#when = after
#when = latest
def mdb_get_financials(ref_symbol, ref_date = "1900-01-01", when = "after"):

    db = get_mongodb()

    query = []

    if when == "after":
        query = { "symbol": { "$in": ref_symbol },
                    "reportDate": { "$gte": ref_date } }
    else:
        query = [
                    { "$match": { "symbol": { "$in": ref_symbol },
                                    "reportDate": { "$lte": ref_date } } },
                    { "$sort": { "reportDate": DESCENDING } },
                    { "$group": {
                        "_id": "$symbol",
                        "symbols": { "$push": "$$ROOT" }
                        }
                    },
                    { "$replaceRoot": {
                        "newRoot": { "$arrayElemAt": ["$symbols", 0] }
                        }
                    },
                    { "$sort": { "symbol": ASCENDING } }
                ]
    #print( query )

    results = []

    if when == "after":
        results = db.iex_financials.find( query ).sort("reportDate", DESCENDING)
    else:
        results = db.iex_financials.aggregate( query )

    financials = pandas.DataFrame()
    for doc in results:
        #print( doc )
        #print( pandas.DataFrame.from_dict(doc, orient='index').T )
        financials = financials.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )
        #print( symbols )
        #index = index+1

    financials.drop("_id", axis=1, errors='ignore', inplace=True)
    #symbols = symbols[symbols.isEnabled != False]
    financials.reset_index(drop=True, inplace=True)
    #print( financials )

    return financials

def mdb_get_portfolios(date):

    db = get_mongodb()

    query = { "inceptionDate": { "$lte": date } }

    results = db.pf_info.find( query ).sort("portfolioID", ASCENDING)

    portfolios = pandas.DataFrame()
    for doc in results:
        portfolios = portfolios.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )

    portfolios.drop("_id", axis=1, inplace=True)
    #symbols = symbols[symbols.isEnabled != False]
    #symbols.reset_index(drop=True, inplace=True)
    #print( symbols )

    return portfolios

def mdb_get_transactions(portfolioID, date, when = "on"):

    db = get_mongodb()

    query = {}

    if when == "on":
        query = { "portfolioID": portfolioID,
                    "date": date }
    else:
        query = { "portfolioID": portfolioID,
                    "date": { "$gte": date } }

    results = db.pf_transactions.find( query )

    transactions = pandas.DataFrame()
    for doc in results:
        transactions = transactions.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )

    if not transactions.empty:
        transactions.drop("_id", axis=1, inplace=True)
    #symbols = symbols[symbols.isEnabled != False]
    #symbols.reset_index(drop=True, inplace=True)
    #print( symbols )

    return transactions

#when = "on" holdings on that date
#when = "after" holdings on or after that date
def mdb_get_holdings(portfolioID, date = " 1990-01-01", when = "on"):

    db = get_mongodb()

    query = []

    if when == "on":
        query = [
                    { "$match": { "portfolioID": portfolioID,
                                    "lastUpdated": { "$lte": date } } },
                    { "$sort": { "lastUpdated": DESCENDING } },
                    { "$group": {
                        "_id": "$symbol",
                        "symbols": { "$push": "$$ROOT" }
                        }
                    },
                    { "$replaceRoot": {
                        "newRoot": { "$arrayElemAt": ["$symbols", 0] }
                        }
                    },
                    { "$sort": { "symbol": ASCENDING } }
                ]
    else:
        query = { "portfolioID": portfolioID,
                    "lastUpdated": { "$gte": date } }

    results = []

    if when == "on":
        results = db.pf_holdings.aggregate( query )
    else:
        results = db.pf_holdings.find( query ).sort("date", ASCENDING)
    #results = results.sort("symbol", ASCENDING)

    holdings = pandas.DataFrame()
    for doc in results:
        #print( doc )
        #print( pandas.DataFrame.from_dict(doc, orient='index').T )
        holdings = holdings.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )
        #print( holdings )
        #index = index+1

    if not holdings.empty:
        holdings.drop("_id", axis=1, inplace=True)
    #print( holdings )

    return holdings

def mdb_get_performance(ref_portfolioID, ref_date = "1990-01-01"):

    query = { "portfolioID": { "$in": ref_portfolioID },
                "date": { "$gte": ref_date } }
    #print( query )

    db = get_mongodb()

    results = db.pf_performance.find( query ).sort("date", DESCENDING)
   
    performance = pandas.DataFrame()
    for doc in results:
        #print( doc )
        #print( pandas.DataFrame.from_dict(doc, orient='index').T )
        performance = performance.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )
        #print( symbols )
        #index = index+1

    performance.drop("_id", axis=1, errors='ignore', inplace=True)
    #symbols = symbols[symbols.isEnabled != False]
    performance.reset_index(drop=True, inplace=True)
    #print( performance )

    return performance
