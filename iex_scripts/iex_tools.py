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
import bson
from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING
import numpy
import pandas
from iex import reference
from iex import Stock
from utils import printProgressBar

################################################
# General functions
################################################

# reorder columns
def set_column_sequence(dataframe, seq, front=True):
    """
    Takes a dataframe and a subsequence of its columns,
    returns dataframe with seq as first columns if "front" is True,
    and seq as last columns if "front" is False.
    @params:
        dataframe   - Required  : Pandas dataframe to reorder (Pandas.DataFrame)
        seq         - Required  : New order ([Int])
        front       - Optional  : Front or back (Bool)
    """
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
    """
    Get symbols from IEX
    @params:
        ref_symbol  - Optional  : matching symbols (Str)
        ref_type    - Optional  : matching type (Str)
    """

    reference.output_format = 'dataframe'
    symbols = reference.symbols()
    
    #Select only matching symbols
    if ref_symbol is not None:
        symbols = symbols[symbols.symbol == ref_symbol]
    #Select only matching types
    if ref_type is not None:
        symbols = symbols[symbols.type == ref_type]
    
    return symbols

def iex_get_company(ref_symbol):
    """
    Get company information from IEX
    @params:
        ref_symbol  - Required  : symbols ([Str])
    """

    stock = Stock( ref_symbol )
    company = stock.company_table()
    #Remove unnecesary data
    company.drop(["exchange","website","CEO","issueType"], axis=1, errors='ignore', inplace=True)
    #Reorder dataframe
    if not company.empty:
        company = set_column_sequence(company, ["symbol","companyName","industry","description","sector"])
        #print( company )

    return company

def iex_get_chart(ref_symbol, ref_range='1m'):
    """
    Get charts from IEX
    @params:
        ref_symbol  - Required  : symbol (Str)
        ref_range   - Optional  : date range (Str)
    """

    stock = Stock( ref_symbol )
    chart = stock.chart_table(ref_range)
    #Remove unnecesary data
    chart.drop(["volume","change","changePercent","changeOverTime"], axis=1, errors='ignore', inplace=True)
    #Add symbol name column
    if not chart.empty:
        chart_len = len( chart.index )
        chart_arr = [ref_symbol] * chart_len
        chart.insert(loc=0, column='symbol', value=chart_arr)
        #Reorder dataframe
        chart = set_column_sequence(chart, ["symbol","date"])

    return chart

def iex_get_dividends(ref_symbol, ref_range='1m'):
    """
    Get dividends from IEX
    @params:
        ref_symbol  - Required  : symbol (Str)
        ref_range   - Optional  : date range (Str)
    """

    stock = Stock( ref_symbol )
    dividends = stock.dividends_table(ref_range)
    #Remove unnecesary data
    dividends.drop(["recordDate","declaredDate","flag","type","qualified","indicated"], axis=1, errors='ignore', inplace=True)
    #Add symbol name column
    if not dividends.empty:
        dividends_len = len( dividends.index )
        dividends_arr = [ref_symbol] * dividends_len
        dividends.insert(loc=0, column='symbol', value=dividends_arr)
        #Reorder dataframe
        dividends = set_column_sequence(dividends, ["symbol","exDate","paymentDate","amount"])

    return dividends

def iex_get_earnings(ref_symbol):
    """
    Get earnings from IEX
    @params:
        ref_symbol  - Required  : symbol (Str)
    """

    stock = Stock( ref_symbol )
    earnings = stock.earnings_table()
    #Remove unnecesary data
    earnings.drop(["consensusEPS","estimatedEPS","numberOfEstimates","EPSSurpriseDollar","yearAgoChangePercent","estimatedChangePercent","symbolId"], axis=1, errors='ignore', inplace=True)
    #Add symbol name
    if not earnings.empty:
        earnings_len = len( earnings.index )
        earnings_arr = [ref_symbol] * earnings_len
        earnings.insert(loc=0, column='symbol', value=earnings_arr)
        #Reorder dataframe
        earnings = set_column_sequence(earnings, ["symbol","actualEPS","announceTime","EPSReportDate","fiscalPeriod","fiscalEndDate"])

    return earnings

def iex_get_financials(ref_symbol):
    """
    Get financials from IEX
    @params:
        ref_symbol  - Required  : symbol (Str)
    """

    stock = Stock( ref_symbol )
    financials = stock.financials_table()
    #Add symbol name
    if not financials.empty:
        financials_len = len( financials.index )
        financials_arr = [ref_symbol] * financials_len
        financials.insert(loc=0, column='symbol', value=financials_arr)
        #Reorder dataframe
        financials = set_column_sequence(financials, ["symbol","reportDate"])

    return financials


################################################
# MongoDB interfacing functions
################################################

def get_mongodb():
    """
    Return MongoDB database object
    """

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
    """
    Is symbol already in MongoDB?
    @params:
        symbol  - Required  : symbol (Dataframe)
    """

    query = { "symbol": symbol["symbol"] }

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

    return not entry_match

def mdb_get_symbols():
    """
    Return symbols from MongoDB
    """

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

    symbols = pandas.DataFrame()
    for doc in results:
        symbols = symbols.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )

    if not symbols.empty:
        symbols.drop("_id", axis=1, inplace=True)
        symbols = symbols[symbols.isEnabled != False]
        symbols.reset_index(drop=True, inplace=True)

    return symbols

def mdb_get_company(symbol):
    """
    Return company information from MongoDB
    @params:
        symbol  - Required  : symbol list ([Str])
    """

    db = get_mongodb()

    query = { "symbol": { "$in": symbol } }

    results = db.iex_company.find( query ).sort("symbol", ASCENDING)

    company = pandas.DataFrame()
    for doc in results:
        company = company.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )

    company.drop("_id", axis=1, errors='ignore', inplace=True)
    company.reset_index(drop=True, inplace=True)

    return company

def mdb_get_chart(ref_symbol, ref_date = "1990-01-01", when = "after"):
    """
    Return company charts from MongoDB
    @params:
        ref_symbol  - Required  : symbol list ([Str])
        ref_date    - Optional  : date YYYY-MM-DD (Str)
        when        - Optional  : after, on, latest (Str)
    """

    db = get_mongodb()

    query = []

    #No more than 30 days ago
    gte_date = (pandas.Timestamp(ref_date) + pandas.DateOffset(days=-210)).strftime('%Y-%m-%d')

    if when == "after":
        query = { "symbol": { "$in": ref_symbol },
                    "date": { "$gte": ref_date } }
    elif when == "on":
        query = { "symbol": { "$in": ref_symbol },
                    "date": ref_date }
    elif when == "latest":
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
    else:
        sys.exit("when not in [after, on, latest]!")

    results = []

    if when == "after" or when == "on":
        results = db.iex_charts.find( query ).sort("date", DESCENDING)
    else:
        results = db.iex_charts.aggregate( query )

    chart = pandas.DataFrame()
    for doc in results:
        #chart = chart.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )
        chart = pandas.concat( [chart,pandas.DataFrame.from_dict(doc, orient='index').T], axis=0, ignore_index=True, sort=False )

    chart.drop("_id", axis=1, errors='ignore', inplace=True)
    chart.reset_index(drop=True, inplace=True)

    return chart

def mdb_get_dividends(ref_symbol, ref_date = "1900-01-01", when = "after"):
    """
    Return company dividends from MongoDB
    @params:
        ref_symbol  - Required  : symbol list ([Str])
        ref_date    - Optional  : date YYYY-MM-DD (Str)
        when        - Optional  : after, latest (Str)
    """

    db = get_mongodb()

    query = []

    if when == "after":
        query = { "symbol": { "$in": ref_symbol },
                    "exDate": { "$gte": ref_date } }
    elif when == "latest":
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
    else:
        sys.exit("when not in [after, latest]")

    results = []

    if when == "after":
        results = db.iex_dividends.find( query ).sort("exDate", DESCENDING)
    else:
        results = db.iex_dividends.aggregate( query )

    dividends = pandas.DataFrame()
    for doc in results:
        dividends = dividends.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )

    dividends.drop("_id", axis=1, errors='ignore', inplace=True)
    dividends.reset_index(drop=True, inplace=True)

    return dividends

def mdb_get_earnings(ref_symbol, ref_date = "1900-01-01", when = "after", date_type = "fiscalEndDate"):
    """
    Return company earnings from MongoDB
    @params:
        ref_symbol  - Required  : symbol list ([Str])
        ref_date    - Optional  : date YYYY-MM-DD (Str)
        when        - Optional  : after, latest (Str)
        date_type   - Optional  : fiscalEndDate, EPSReportDate (Str)
    """

    db = get_mongodb()

    query = []

    if when == "after":
        query = { "symbol": { "$in": ref_symbol },
                    date_type: { "$gte": ref_date } }
    elif when == "latest":
        query = [
                    { "$match": { "symbol": { "$in": ref_symbol },
                                    date_type: { "$lte": ref_date } } },
                    { "$sort": { date_type: DESCENDING } },
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
        sys.exit("when not in [after, latest]")

    results = []

    if when == "after":
        results = db.iex_earnings.find( query ).sort(date_type, DESCENDING)
    else:
        results = db.iex_earnings.aggregate( query )

    earnings = pandas.DataFrame()
    for doc in results:
        earnings = earnings.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )

    earnings.drop("_id", axis=1, errors='ignore', inplace=True)
    earnings.reset_index(drop=True, inplace=True)

    return earnings

def mdb_get_financials(ref_symbol, ref_date = "1900-01-01", when = "after"):
    """
    Return company financials from MongoDB
    @params:
        ref_symbol  - Required  : symbol list ([Str])
        ref_date    - Optional  : date YYYY-MM-DD (Str)
        when        - Optional  : after, latest (Str)
    """

    db = get_mongodb()

    query = []

    if when == "after":
        query = { "symbol": { "$in": ref_symbol },
                    "reportDate": { "$gte": ref_date } }
    elif when == "latest":
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
    else:
        sys.exit("when not in [after, latest]")

    results = []

    if when == "after":
        results = db.iex_financials.find( query ).sort("reportDate", DESCENDING)
    else:
        results = db.iex_financials.aggregate( query )

    financials = pandas.DataFrame()
    for doc in results:
        financials = financials.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )

    financials.drop("_id", axis=1, errors='ignore', inplace=True)
    financials.reset_index(drop=True, inplace=True)

    return financials

def mdb_get_portfolios(date):
    """
    Return portfolio information from MongoDB
    @params:
        date    - Required  : date YYYY-MM-DD (Str)
    """

    db = get_mongodb()

    query = { "inceptionDate": { "$lte": date } }

    results = db.pf_info.find( query ).sort("portfolioID", ASCENDING)

    portfolios = pandas.DataFrame()
    for doc in results:
        portfolios = portfolios.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )

    portfolios.drop("_id", axis=1, inplace=True)

    return portfolios

def mdb_get_transactions(portfolioID, date, when = "on"):
    """
    Return portfolio transactions from MongoDB
    @params:
        portfolioID - Required  : portfolio ID (Str)
        date        - Required  : date YYYY-MM-DD (Str)
        when        - Optional  : on, after (Str)
    """

    db = get_mongodb()

    query = {}

    if when == "on":
        query = { "portfolioID": portfolioID,
                    "date": date }
    elif when == "after":
        query = { "portfolioID": portfolioID,
                    "date": { "$gte": date } }
    else:
        sys.exit("when not in [on, after]")

    results = db.pf_transactions.find( query )

    transactions = pandas.DataFrame()
    for doc in results:
        transactions = transactions.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )

    if not transactions.empty:
        transactions.drop("_id", axis=1, inplace=True)

    return transactions

def mdb_get_holdings(portfolioID, date = " 1990-01-01", when = "on"):
    """
    Return portfolio holdings from MongoDB
    @params:
        portfolioID - Required  : portfolio ID (Str)
        date        - Optional  : date YYYY-MM-DD (Str)
        when        - Optional  : on, after (Str)
    """

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
    elif when == "after":
        query = { "portfolioID": portfolioID,
                    "lastUpdated": { "$gte": date } }
    else:
        sys.exit("when not in [on, after]")

    results = []

    if when == "on":
        results = db.pf_holdings.aggregate( query )
    else:
        results = db.pf_holdings.find( query ).sort("date", ASCENDING)

    holdings = pandas.DataFrame()
    for doc in results:
        holdings = holdings.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )

    if not holdings.empty:
        holdings.drop("_id", axis=1, inplace=True)

    return holdings

def mdb_get_performance(ref_portfolioID, ref_date = "1990-01-01"):
    """
    Return portfolio performance from MongoDB
    @params:
        ref_portfolioID - Required  : portfolio ID (Str)
        ref_date        - Optional  : date YYYY-MM-DD (Str)
    """

    query = { "portfolioID": { "$in": ref_portfolioID },
                "date": { "$gte": ref_date } }

    db = get_mongodb()

    results = db.pf_performance.find( query ).sort("date", DESCENDING)
   
    performance = pandas.DataFrame()
    for doc in results:
        performance = performance.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )

    performance.drop("_id", axis=1, errors='ignore', inplace=True)
    performance.reset_index(drop=True, inplace=True)

    return performance

def mdb_get_stock_list(ref_date = "1990-01-01", when = "on"):
    """
    Return ranked list of stocks from MongoDB
    @params:
        ref_date    - Optional  : date YYYY-MM-DD (Str)
        when        - Optional  : on, latest (Str)
    """

    db = get_mongodb()

    query = []

    gte_date = (pandas.Timestamp(ref_date) + pandas.DateOffset(days=-50)).strftime('%Y-%m-%d')

    if when == "on":
        query = { "date": ref_date }
    elif when == "latest":
        query = [
                    { "$match": { "date": { "$lte": ref_date },
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
    else:
        sys.exit("when not in [on, latest]")

    results = []

    if when == "on":
        results = db.stock_list.find( query )
    elif when == "latest":
        results = db.stock_list.aggregate( query )

    stock_list = pandas.DataFrame()
    for doc in results:
        stock_list = stock_list.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )

    stock_list.drop("_id", axis=1, errors='ignore', inplace=True)
    stock_list.reset_index(drop=True, inplace=True)

    return stock_list

def mdb_calculate_top_stocks(ref_date):
    """
    Calculate ranked list of stocks
    @params:
        ref_date    - Required  : date YYYY-MM-DD (Str)
    """

    #Get ranked stock list for given date
    symbols = mdb_get_symbols()['symbol'].tolist()
    print( "Query earnings" )
    earnings = mdb_get_earnings(symbols, ref_date, "latest", "EPSReportDate")
    earnings = earnings[["EPSReportDate","actualEPS","fiscalEndDate","fiscalPeriod","symbol"]]
    #Get financials within 6 months
    print( "Query financials" )
    sixMonthsBeforeDate = (pandas.Timestamp(ref_date) + pandas.DateOffset(months=-6)).strftime('%Y-%m-%d')
    financials = mdb_get_financials(symbols, sixMonthsBeforeDate, "after")
    financials = financials[ financials['reportDate'] <= earnings['fiscalEndDate'].max() ]
    financials = financials[["symbol","reportDate","netIncome","shareholderEquity"]]
    #Get prices for inception date
    print( "Query prices" )
    prices = mdb_get_chart(symbols, ref_date, "latest")
    #Get company data
    company = mdb_get_company( symbols )
    company = company[['symbol','companyName','industry','sector']]
    #Merge dataframes together
    print( "Merge dataframes" )
    merged = pandas.merge(earnings,financials,how='inner',left_on=["symbol","fiscalEndDate"],right_on=["symbol","reportDate"],sort=False)
    merged = pandas.merge(merged,prices,how='inner',on="symbol",sort=False)
    merged = pandas.merge(merged,company,how='inner',on='symbol',sort=False)
    #Remove any rows with missing values
    merged = merged.dropna(axis=0, subset=["netIncome","actualEPS","close","shareholderEquity"])
    #Calculate marketCap value
    # price * netIncome / EPS = price * sharesOutstanding = mcap
    # Actually not 100% accurate, should be netIncome - preferred dividend
    # Doesn't perfectly match IEX value or google - probably good enough
    merged["sharesOutstanding"] = merged.netIncome / merged.actualEPS
    merged["marketCap"] = merged.sharesOutstanding * merged.close
    #Calculate PE, ROE, and ratio
    merged["peRatio"] = merged.close / merged.actualEPS
    merged["returnOnEquity"] = merged.netIncome / merged.shareholderEquity
    merged["peROERatio"] = merged.peRatio / merged.returnOnEquity
    #Count number of stocks above mcap value
    # A useful indicator of how universe compares to S&P500
    print( "Universe before cuts..." )
    print( "mcap > 50M: " + str(merged[merged["marketCap"] > 50000000].count()["marketCap"]) )
    print( "mcap > 100M: " + str(merged[merged["marketCap"] > 100000000].count()["marketCap"]) )
    print( "mcap > 500M: " + str(merged[merged["marketCap"] > 500000000].count()["marketCap"]) )
    print( "mcap > 1B: " + str(merged[merged["marketCap"] > 1000000000].count()["marketCap"]) )
    print( "mcap > 5B: " + str(merged[merged["marketCap"] > 5000000000].count()["marketCap"]) )
    print( "mcap > 10B: " + str(merged[merged["marketCap"] > 10000000000].count()["marketCap"]) )
    print( "mcap > 50B: " + str(merged[merged["marketCap"] > 50000000000].count()["marketCap"]) )
    print( "mcap > 100B: " + str(merged[merged["marketCap"] > 100000000000].count()["marketCap"]) )
    #Rank stocks
    #Cut negative PE and ROE
    merged = merged[(merged.peRatio > 0) & (merged.returnOnEquity > 0)]
    #Remove invalid stock symbols, and different voting options
    # Do the different voting options affect marketCap?
    forbidden = [ "#", ".", "-" ]
    merged = merged[ merged.apply( lambda x: not any( s in x['symbol'] for s in forbidden ), axis=1 ) ]
    #Remove American Depositary Shares
    ads_str = 'American Depositary Shares'
    merged = merged[ merged.apply( lambda x: ads_str not in x['companyName'], axis=1 ) ]
    #Remove industries that do not compare well
    # e.g. Companies that have investments as assets
    forbidden_industry = ['Brokers & Exchanges','REITs','Asset Management','Banks']
    merged = merged[ ~merged.industry.isin( forbidden_industry ) ]
    #Count number of stocks after cuts
    print( "Universe after cuts..." )
    print( "mcap > 50M: " + str(merged[merged["marketCap"] > 50000000].count()["marketCap"]) )
    print( "mcap > 100M: " + str(merged[merged["marketCap"] > 100000000].count()["marketCap"]) )
    print( "mcap > 500M: " + str(merged[merged["marketCap"] > 500000000].count()["marketCap"]) )
    print( "mcap > 1B: " + str(merged[merged["marketCap"] > 1000000000].count()["marketCap"]) )
    print( "mcap > 5B: " + str(merged[merged["marketCap"] > 5000000000].count()["marketCap"]) )
    print( "mcap > 10B: " + str(merged[merged["marketCap"] > 10000000000].count()["marketCap"]) )
    print( "mcap > 50B: " + str(merged[merged["marketCap"] > 50000000000].count()["marketCap"]) )
    print( "mcap > 100B: " + str(merged[merged["marketCap"] > 100000000000].count()["marketCap"]) )
    #Order by peROERatio
    merged = merged.sort_values(by="peROERatio", ascending=True, axis="index")

    return merged

def mdb_delete_duplicates(ref_date = "1990-01-01", when = "on"):
    """
    Delete duplicates prices in MongoDB
    @params:
        ref_date    - Optional  : date YYYY-MM-DD (Str)
        when        - Optional  : on, latest (Str)
    """

    mdb_symbols = mdb_get_symbols()
    mdb_symbols = mdb_symbols.iloc[ 999: , : ]
    mdb_symbols.reset_index(drop=True, inplace=True)
    #mdb_symbols = ["A"]
    #print( mdb_symbols )
    printProgressBar(0, len(mdb_symbols.index), prefix = 'Progress:', suffix = '', length = 50)
    for index, symbol in mdb_symbols.iterrows():
        #if index > 10:
        #    break
        #print( symbol )
        db = get_mongodb()
        query = { "symbol": { "$in": [symbol["symbol"]] },
                    "date": { "$gte": "2017-01-01" } }
        results = db.iex_charts.find( query ).sort("date", DESCENDING)
        chart = pandas.DataFrame()
        for doc in results:
            chart = chart.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )
        duplicates = chart[chart.duplicated(['date'])]
        #print( duplicates )
    
        # Remove all duplicates in one go    
        #if not duplicates.empty:
        #    db.iex_charts.delete_many({"_id":{"$in":duplicates['_id'].tolist()}})
        # Remove duplicates if they exist
        if not duplicates.empty:
            #Update progress bar
            printProgressBar(index+1, len(mdb_symbols.index), prefix = 'Progress:', suffix = "Deleting duplicates for " + symbol["symbol"] + "      ", length = 50)
            db.iex_charts.delete_many({"_id":{"$in":duplicates['_id'].tolist()}})
        else:
            #Update progress bar
            printProgressBar(index+1, len(mdb_symbols.index), prefix = 'Progress:', suffix = "No duplicates for " + symbol["symbol"] + "      ", length = 50)


    #query = []

    #Loop through symbols
    #Get prices for symbol
    #Find dublicates
    #Delete duplicates

    #db = get_mongodb()

    #duplicates = []
    #
    #db.iex_charts.aggregate([
    #    { "$match": { 
    #        "symbol": { "$ne": "" }  # discard selection criteria
    #        }},
    #    { "$group": { 
    #        "_id": { "symbol": "$symbol", "date": "$date" }, # can be grouped on multiple properties 
    #        "dups": { "$addToSet": "$_id" }, 
    #        "count": { "$sum": 1 } 
    #        }}, 
    #    { "$match": { 
    #        "count": { "$gt": 1 }    # Duplicates considered as count greater than one
    #        }}
    #    ],
    #    {"allowDiskUse": true}       # For faster processing if set is larger
    ## You can display result until this and check duplicates 
    #).forEach(bson.Code('''function(doc){
    #    doc.dups.shift();      # First element skipped for deleting
    #    doc.dups.forEach( function(dupId){ 
    #        duplicates.push(dupId);   # Getting all duplicate ids
    #    })    
    #}''')
    #
    ## If you want to Check all "_id" which you are deleting else print statement not needed
    #print(duplicates) 
    
    # Remove all duplicates in one go    
    #db.collectionName.remove({_id:{$in:duplicates}})
