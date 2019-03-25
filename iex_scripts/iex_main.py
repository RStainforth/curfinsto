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
import pandas
import pymongo
#from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING

################################################
################################################

if __name__ == '__main__':

    #Flags for inserting specific data types
    insert_symbols = False
    insert_prices = False
    insert_dividends = False
    insert_earnings = True
    insert_financials = True
    insert_portfolio = False
    insert_holdings = False
    update_holdings = True

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
            if any( x in symbol["symbol"] for x in forbidden):
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
            mdb_dividends = iex_tools.mdb_get_dividends( [mdb_symbol["symbol"]] )
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

    if insert_portfolio:
        #Find last reporting date for earliest quarter
        db = iex_tools.get_mongodb()
        #results = db.iex_earnings.find()
        #earnings = pandas.DataFrame()
        #for doc in results:
        #    earnings = earnings.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True )
        #print( earnings.loc[earnings['fiscalPeriod'].isin( ['Q1 2019','Q4 2018','Q3 2018','Q2 2018','Q1 2018','Q4 2017','Q3 2017'] )].groupby('fiscalPeriod').count() )
        #First fiscalPeriod to use 'Q1 2018'
        test = False
        if test:
            query = { "fiscalPeriod": "Q1 2018" }
            results = db.iex_earnings.find( query ).sort("EPSReportDate", DESCENDING)
            earnings = pandas.DataFrame()
            for doc in results:
                earnings = earnings.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True )
            #print( earnings )
            query = { "fiscalEndDate": "2018-03-31" }
            results = db.iex_earnings.find( query ).sort("EPSReportDate", DESCENDING)
            earnings = pandas.DataFrame()
            for doc in results:
                earnings = earnings.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True )
            #print( earnings )
            query = { "symbol": "AAPL" }
            results = db.iex_earnings.find( query ).sort("EPSReportDate", DESCENDING)
            earnings = pandas.DataFrame()
            for doc in results:
                earnings = earnings.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True )
            #print( earnings )
        #Next day find best stocks for n different mcap portfolios
        #Start portfolio on 2018-07-02 to allow all Q1 2018 results to be reported
        # Get most recent financials, earnings, price
        # Find most recent EPSReportDate in earnings
        # Find corresponding fiscalEndDate in earnings
        # Get matching reportDate in financials
        print( "Query earnings" )
        results = db.iex_earnings.aggregate([
            { "$match": { "EPSReportDate": { "$lt": "2018-07-02" } } },
            { "$sort": { "EPSReportDate": DESCENDING } },
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
        earnings = pandas.DataFrame()
        financials = pandas.DataFrame()
        prices = pandas.DataFrame()
        for doc in results:
            #print( doc.get("symbol") )
            earnings = earnings.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )
            #query = { "symbol": doc.get("symbol"),
            #        "reportDate": doc.get("fiscalEndDate") }
            #financial_result = db.iex_financials.find_one( query )
            #print( financial_result )
            #if financial_result:
            #    financials = financials.append( pandas.DataFrame.from_dict(financial_result, orient='index').T, ignore_index=True )
            #query = { "symbol": doc.get("symbol"),
            #        "date": "2018-07-02" }
            #price_result = db.iex_charts.find_one( query )
            #print( price_result )
            #if price_result:
            #    prices = prices.append( pandas.DataFrame.from_dict(price_result, orient='index').T, ignore_index=True )
        # Join?
        #print( "fiscalEndDate max: " + earnings["fiscalEndDate"].max() )
        print( "Query financials" )
        query = { "reportDate": { "$lte": earnings["fiscalEndDate"].max() },
                "reportDate": { "$gte": "2018-01-01" } }
        #print( query )
        financial_result = db.iex_financials.find( query )
        for doc in financial_result:
            #print( doc )
            financials = financials.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )
        print( "Query prices" )
        query = { "date": "2018-07-02" }
        price_result = db.iex_charts.find( query )
        for doc in price_result:
            prices = prices.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )
        earnings = earnings[["EPSReportDate","actualEPS","fiscalEndDate","fiscalPeriod","symbol"]]
        financials = financials[["symbol","reportDate","netIncome","shareholderEquity"]]
        prices.drop("_id", axis=1, inplace=True)
        #print( earnings )
        #print( financials )
        #print( prices )
        print( "Merge dataframes" )
        merged = pandas.merge(earnings,financials,how='inner',left_on=["symbol","fiscalEndDate"],right_on=["symbol","reportDate"],sort=False)
        #print( merged )
        merged = pandas.merge(merged,prices,how='inner',on="symbol",sort=False)
        #print( merged )
        #Remove any rows with missing values
        merged = merged.dropna(axis=0, subset=["netIncome","actualEPS","open","shareholderEquity"])
        #earnings.to_excel("earnings.xlsx")
        #financials.to_excel("financials.xlsx")
        #prices.to_excel("prices.xlsx")
        #Save tables to file
        #Import tables
        #Count to make sure there aren't more than one entry per symbol
        #print( merged.groupby("symbol").count()["EPSReportDate"].max() )
        # Select stocks above mcap floor
        # price * netIncome / EPS = price * sharesOutstanding = mcap
        # Actually not 100% accurate, should be netIncome - preferred dividend
        # Doesn't perfectly match IEX value or google - probably good enough
        merged["sharesOutstanding"] = merged.netIncome / merged.actualEPS
        merged["marketCap"] = merged.sharesOutstanding * merged.open
        # Calculate PE and ROE
        merged["peRatio"] = merged.open / merged.actualEPS
        merged["returnOnEquity"] = merged.netIncome / merged.shareholderEquity
        merged["peROERatio"] = merged.peRatio / merged.returnOnEquity
        #print( merged )
        # Count number of stocks above mcap value
        #print( "mcap > 50M: " + str(merged[merged["marketCap"] > 50000000].count()["marketCap"]) )
        #print( "mcap > 100M: " + str(merged[merged["marketCap"] > 100000000].count()["marketCap"]) )
        #print( "mcap > 500M: " + str(merged[merged["marketCap"] > 500000000].count()["marketCap"]) )
        #print( "mcap > 1B: " + str(merged[merged["marketCap"] > 1000000000].count()["marketCap"]) )
        #print( "mcap > 5B: " + str(merged[merged["marketCap"] > 5000000000].count()["marketCap"]) )
        #print( "mcap > 10B: " + str(merged[merged["marketCap"] > 10000000000].count()["marketCap"]) )
        #print( "mcap > 50B: " + str(merged[merged["marketCap"] > 50000000000].count()["marketCap"]) )
        #print( "mcap > 100B: " + str(merged[merged["marketCap"] > 100000000000].count()["marketCap"]) )
        # Rank
        #print( "Cut negative PE and ROE" )
        merged = merged[(merged.peRatio > 0) & (merged.returnOnEquity > 0)]
        #print( "mcap > 50M: " + str(merged[merged["marketCap"] > 50000000].count()["marketCap"]) )
        #print( "mcap > 100M: " + str(merged[merged["marketCap"] > 100000000].count()["marketCap"]) )
        #print( "mcap > 500M: " + str(merged[merged["marketCap"] > 500000000].count()["marketCap"]) )
        #print( "mcap > 1B: " + str(merged[merged["marketCap"] > 1000000000].count()["marketCap"]) )
        #print( "mcap > 5B: " + str(merged[merged["marketCap"] > 5000000000].count()["marketCap"]) )
        #print( "mcap > 10B: " + str(merged[merged["marketCap"] > 10000000000].count()["marketCap"]) )
        #print( "mcap > 50B: " + str(merged[merged["marketCap"] > 50000000000].count()["marketCap"]) )
        #print( "mcap > 100B: " + str(merged[merged["marketCap"] > 100000000000].count()["marketCap"]) )
        #Build portfolios for 100M, 500M, 1B, 5B, 10B, 50B mcap stocks
        #Build transaction tables which buy the stocks
        #On day 1 do cash deposit for n different portfolio
        #Portfolios table:
        # portfolio_id, name, description, inception_date
        portfolio_tables = [
                            { "portfolioID": "stocks30mcap100M",
                                "name": "30 stocks, 100M market cap",
                                "description": "Portfolio of 30 stocks above 100M market cap with initial investment of 100M USD",
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks30mcap500M",
                                "name": "30 stocks, 500M market cap",
                                "description": "Portfolio of 30 stocks above 500M market cap with initial investment of 100M USD",
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks30mcap1B",
                                "name": "30 stocks, 1B market cap",
                                "description": "Portfolio of 30 stocks above 1B market cap with initial investment of 100M USD",
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks30mcap5B",
                                "name": "30 stocks, 5B market cap",
                                "description": "Portfolio of 30 stocks above 5B market cap with initial investment of 100M USD",
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks30mcap10B",
                                "name": "30 stocks, 10B market cap",
                                "description": "Portfolio of 30 stocks above 10B market cap with initial investment of 100M USD",
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks30mcap50B",
                                "name": "30 stocks, 50B market cap",
                                "description": "Portfolio of 30 stocks above 50B market cap with initial investment of 100M USD",
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks50mcap100M",
                                "name": "50 stocks, 100M market cap",
                                "description": "Portfolio of 50 stocks above 100M market cap with initial investment of 100M USD",
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks50mcap500M",
                                "name": "50 stocks, 500M market cap",
                                "description": "Portfolio of 50 stocks above 500M market cap with initial investment of 100M USD",
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks50mcap1B",
                                "name": "50 stocks, 1B market cap",
                                "description": "Portfolio of 50 stocks above 1B market cap with initial investment of 100M USD",
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks50mcap5B",
                                "name": "50 stocks, 5B market cap",
                                "description": "Portfolio of 50 stocks above 5B market cap with initial investment of 100M USD",
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks50mcap10B",
                                "name": "50 stocks, 10B market cap",
                                "description": "Portfolio of 50 stocks above 10B market cap with initial investment of 100M USD",
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks50mcap50B",
                                "name": "50 stocks, 50B market cap",
                                "description": "Portfolio of 50 stocks above 50B market cap with initial investment of 100M USD",
                                "inceptionDate": "2018-07-02" }
                            ]
        #print( portfolio_tables )
        insert_pf_info = True
        if insert_pf_info:
            db.pf_info.insert_many( portfolio_tables )
        #Transaction table:
        # portfolio_id, symbol, type (buy/sell/deposit/withdrawal), date, price, volume, commission
        #Find highest ranked stocks
        stocks30mcap100M = merged[merged["marketCap"] > 100000000].sort_values(by="peROERatio", ascending=True, axis="index").head(30).reset_index(drop=True)
        stocks30mcap500M = merged[merged["marketCap"] > 500000000].sort_values(by="peROERatio", ascending=True, axis="index").head(30).reset_index(drop=True)
        stocks30mcap1B = merged[merged["marketCap"] > 1000000000].sort_values(by="peROERatio", ascending=True, axis="index").head(30).reset_index(drop=True)
        stocks30mcap5B = merged[merged["marketCap"] > 5000000000].sort_values(by="peROERatio", ascending=True, axis="index").head(30).reset_index(drop=True)
        stocks30mcap10B = merged[merged["marketCap"] > 10000000000].sort_values(by="peROERatio", ascending=True, axis="index").head(30).reset_index(drop=True)
        stocks30mcap50B = merged[merged["marketCap"] > 50000000000].sort_values(by="peROERatio", ascending=True, axis="index").head(30).reset_index(drop=True)
        stocks50mcap100M = merged[merged["marketCap"] > 100000000].sort_values(by="peROERatio", ascending=True, axis="index").head(50).reset_index(drop=True)
        stocks50mcap500M = merged[merged["marketCap"] > 500000000].sort_values(by="peROERatio", ascending=True, axis="index").head(50).reset_index(drop=True)
        stocks50mcap1B = merged[merged["marketCap"] > 1000000000].sort_values(by="peROERatio", ascending=True, axis="index").head(50).reset_index(drop=True)
        stocks50mcap5B = merged[merged["marketCap"] > 5000000000].sort_values(by="peROERatio", ascending=True, axis="index").head(50).reset_index(drop=True)
        stocks50mcap10B = merged[merged["marketCap"] > 10000000000].sort_values(by="peROERatio", ascending=True, axis="index").head(50).reset_index(drop=True)
        stocks50mcap50B = merged[merged["marketCap"] > 50000000000].sort_values(by="peROERatio", ascending=True, axis="index").head(50).reset_index(drop=True)
        stocks30mcap100M["portfolioID"] = "stocks30mcap100M"
        stocks30mcap500M["portfolioID"] = "stocks30mcap500M"
        stocks30mcap1B["portfolioID"] = "stocks30mcap1B"
        stocks30mcap5B["portfolioID"] = "stocks30mcap5B"
        stocks30mcap10B["portfolioID"] = "stocks30mcap10B"
        stocks30mcap50B["portfolioID"] = "stocks30mcap50B"
        stocks50mcap100M["portfolioID"] = "stocks50mcap100M"
        stocks50mcap500M["portfolioID"] = "stocks50mcap500M"
        stocks50mcap1B["portfolioID"] = "stocks50mcap1B"
        stocks50mcap5B["portfolioID"] = "stocks50mcap5B"
        stocks50mcap10B["portfolioID"] = "stocks50mcap10B"
        stocks50mcap50B["portfolioID"] = "stocks50mcap50B"
        #print( stocks30mcap100M )
        portfolio_dfs = [ stocks30mcap100M, stocks30mcap500M, stocks30mcap1B, stocks30mcap5B, stocks30mcap10B, stocks30mcap50B, stocks50mcap100M, stocks50mcap500M, stocks50mcap1B, stocks50mcap5B, stocks50mcap10B, stocks50mcap50B ] 
        transaction_tables = []
        for portfolio_df in portfolio_dfs:
            transaction_table = { "portfolioID": portfolio_df.iloc[0]["portfolioID"],
                                    "symbol": "USD",
                                    "type": "deposit",
                                    "date": "2018-07-02",
                                    "price": 1.0,
                                    "volume": 100000000,
                                    "commission": 0.0 }
            transaction_tables.append( transaction_table )
        #print( transaction_tables )
        insert_pf_transactions = True
        if insert_pf_transactions:
            db.pf_transactions.insert_many( transaction_tables )
        #Buy stocks
        #For stocks30mcap100M
        # Iterate through dataframe
        # Divide 100M by 30
        # Divide by price of stock and round to integer -> volume
        # symbol = merged.symbol, type = buy, date = 2018-07-02, price = merged.open, commission = 0.0
        transaction_tables = []
        for portfolio_df in portfolio_dfs:
            for index, stock in portfolio_df.iterrows():
                volume = 100000000
                if "stocks30" in portfolio_df.iloc[0]["portfolioID"]:
                    volume = volume / 30
                elif "stocks50" in portfolio_df.iloc[0]["portfolioID"]:
                    volume = volume / 50
                volume = volume / stock.open
                volume = round(volume)
                transaction_table = { "portfolioID": portfolio_df.iloc[0]["portfolioID"],
                                        "symbol": stock.symbol,
                                        "type": "buy",
                                        "date": "2018-07-02",
                                        "price": stock.open,
                                        "volume": volume,
                                        "commission": 0.0 }
                transaction_tables.append( transaction_table )
        #print( transaction_tables )
        insert_pf_transactions = True
        if insert_pf_transactions:
            db.pf_transactions.insert_many( transaction_tables )

    if insert_holdings:    
        #Build holdings table which accumulates based on the addition of a transaction table
        #Calculate portfolio value
        #Monitor dividends and store in cash
        #Get list of portfolios
        portfolios = iex_tools.mdb_get_portfolios("2018-07-02")["portfolioID"]
        #print( portfolios )
        #Loop through portfolios
        for index, portfolio in portfolios.iteritems():
            #Get existing holdings
            holdings = iex_tools.mdb_get_holdings(portfolio,"2018-07-02")
            #If no existing holdings create 0 dollar entry to create table
            if holdings.empty:
                holding_dict = { "portfolioID": portfolio,
                                    "symbol": "USD",
                                    "endOfDayQuantity": 0.0,
                                    "purchaseValue": 0.0,
                                    "lastUpdated": "2018-07-02" }
                holdings = holdings.append( pandas.DataFrame.from_dict(holding_dict, orient='index').T, ignore_index=True )
            #print( holdings )
            #From inception date implement transactions and update holdings table
            #Portfolio, stock symbol, End of day volumes, lastUpdated, purchaseValue
            transactions = iex_tools.mdb_get_transactions(portfolio,"2018-07-02")
            #print( transactions )
            for t_index, transaction in transactions.iterrows():
                holding = holdings[holdings.symbol == transaction.symbol]
                #holding.reset_index(drop=True, inplace=True)
                #print( holdings )
                holdings = holdings[ ~holdings["symbol"].isin([transaction.symbol]) ]
                #print( holdings )
                if transaction.type == "deposit":
                    holding["endOfDayQuantity"] = holding["endOfDayQuantity"] + (transaction.price * transaction.volume) 
                    holding["purchaseValue"] = holding["purchaseValue"] + (transaction.price * transaction.volume)
                    holding["lastUpdated"] = transaction.date
                    holdings = holdings.append( holding, ignore_index=True )
                if transaction.type == "buy":
                    holding_dict = {}
                    if not holding.empty:
                        holding_dict = { "portfolioID": transaction.portfolioID,
                                            "symbol": transaction.symbol,
                                            "endOfDayQuantity": holding["endOfDayQuantity"] + transaction.volume,
                                            "purchaseValue": holding["purchaseValue"] + (transaction.price * transaction.volume),
                                            "lastUpdated": transaction.date }
                    else:
                        holding_dict = { "portfolioID": transaction.portfolioID,
                                            "symbol": transaction.symbol,
                                            "endOfDayQuantity": transaction.volume,
                                            "purchaseValue": (transaction.price * transaction.volume),
                                            "lastUpdated": transaction.date }
                    #holding.iloc[0]["portfolioID"] = transaction.portfolioID
                    #holding.iloc[0]["symbol"] = transaction.symbol
                    #holding.iloc[0]["endOfDayQuantity"] = holding["endOfDayQuantity"] + transaction.volume
                    #holding.iloc[0]["purchaseValue"] = holding["purchaseValue"] + (transaction.price * transaction.volume)
                    #holding.iloc[0]["lastUpdated"] = transaction.date
                    holdings = holdings.append( pandas.DataFrame.from_dict(holding_dict, orient='index').T, ignore_index=True )
                    cash = holdings[holdings.symbol == "USD"]
                    holdings = holdings[ ~holdings["symbol"].isin(["USD"]) ]
                    cash["endOfDayQuantity"] = cash["endOfDayQuantity"] - (transaction.price * transaction.volume)
                    cash["purchaseValue"] = cash["purchaseValue"] - (transaction.price * transaction.volume)
                    cash["lastUpdated"] = transaction.date
                    holdings = holdings.append( cash, ignore_index=True )
            #print( holdings )
            insert_holdings_tx = False
            if insert_holdings_tx:
                db.pf_holdings.insert_many( holdings.to_dict('records') )
            
    if update_holdings:    
        #Update holdings tables to account for dividends paid
        #Calculate portfolio value
        #Monitor dividends and store in cash
        #Get list of portfolios
        portfolios = iex_tools.mdb_get_portfolios("2018-07-02")["portfolioID"]
        #print( portfolios )
        #Loop through portfolios
        for index, portfolio in portfolios.iteritems():
            #if index > 0:
            #    continue
            #Get existing holdings           
            #If any dividend paid add to USD
            holdings = iex_tools.mdb_get_holdings(portfolio,"2018-07-02")
            print( holdings["symbol"].tolist() )
            #Look for dividends paid after lastUpdated date
            dividends = iex_tools.mdb_get_dividends(holdings["symbol"].tolist(), "2018-07-02")
            print( dividends )
            #Find all dividends after date for array of stocks
            #Sort them in date order







        #Calculate portfolio value - close of day prices for holdings
        #Calculate portfolio return - (close of day holdings - (close of previous day holding + purchases))/(close of previous day holding + purchases)

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
