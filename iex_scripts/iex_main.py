#!/usr/bin/env python
# Author: J. Walker
# Date: Feb 11th, 2019
# Brief: A short script that uses the 'iex_tools' module to 
#        extract stock information from the IEX API
# Usage: ./iex_main
# Would get all new stock information

import iex_tools
from utils import printProgressBar
import os
import sys
import pandas
import pymongo
#from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import BulkWriteError
import datetime

################################################
################################################

if __name__ == '__main__':

    #Flags for inserting specific data types
    insert_symbols = True
    insert_company = True
    delete_prices = False
    insert_prices = True
    insert_dividends = True
    insert_earnings = True
    insert_financials = True
    insert_portfolio = False
    insert_holdings = True
    update_holdings = True
    insert_performance = True
    insert_stock_list = True

    #Get database connection
    db = iex_tools.get_mongodb()

    #If new symbol exists then upload it
    if insert_symbols:
        print( "Insert new symbols" )
        #Get all common stocks from IEX
        symbols = iex_tools.iex_get_symbols(ref_type="cs")
        #Get SPY (S&P500 exchange traded index) from IEX
        symbols_spy = iex_tools.iex_get_symbols(ref_symbol="SPY")
        #Reset indices (probably not necessary)
        symbols.reset_index(drop=True, inplace=True)
        symbols_spy.reset_index(drop=True, inplace=True)
        #Append SPY to stocks
        symbols = symbols.append(symbols_spy, ignore_index=True, sort=False)
        symbols.reset_index(drop=True, inplace=True)
        #Get symbols already in MongoDB
        mdb_symbols = iex_tools.mdb_get_symbols()
        #Initial call to print 0% progress
        printProgressBar(0, len(symbols.index), prefix = 'Progress:', suffix = '', length = 50)
        #Loop through symbols
        for index, symbol in symbols.iterrows():
            #Exclude forbidden characters
            forbidden = ["#"]
            if any( x in symbol["symbol"] for x in forbidden):
                #Update progress bar
                printProgressBar(index+1, len(symbols.index), prefix = 'Progress:', suffix = "Symbol contains forbidden character: " + symbol["symbol"] + "      ", length = 50)
                continue
            #Is symbol already in MongoDB
            mask = (mdb_symbols['iexId'] == symbol['iexId']) & (mdb_symbols['isEnabled'] == symbol['isEnabled']) & (mdb_symbols['name'] == symbol['name']) & (mdb_symbols['type'] == symbol['type']) 
            #Insert if not in MongoDB
            if mdb_symbols.loc[mask].empty:
                #Update progress bar
                printProgressBar(index+1, len(symbols.index), prefix = 'Progress:', suffix = "Inserting new symbol: " + symbol["symbol"] + "      ", length = 50)
                db.iex_symbols.insert_one( symbol.to_dict() )
            else:
                #Update progress bar
                printProgressBar(index+1, len(symbols.index), prefix = 'Progress:', suffix = "Symbol " + symbol["symbol"] + " already exists      ", length = 50)

    #If new company exists then upload them
    if insert_company:
        print( "Insert new company information" )
        #Get all symbols in MongoDB
        mdb_symbols = iex_tools.mdb_get_symbols()
        #Get companies already in MongoDB
        mdb_companies = iex_tools.mdb_get_company( mdb_symbols['symbol'].tolist() )
        #Initial call to print 0% progress
        printProgressBar(0, len(mdb_symbols.index), prefix = 'Progress:', suffix = '', length = 50)
        #Loop through symbols
        for index, mdb_symbol in mdb_symbols.iterrows():
            #Skip company if already in MongoDB
            if not mdb_companies[ mdb_companies['symbol'] == mdb_symbol['symbol'] ].empty:
                #Update progress bar
                printProgressBar(index+1, len(mdb_symbols.index), prefix = 'Progress:', suffix = "No new data for " + mdb_symbol["symbol"] + "      ", length = 50)
                continue
            #Get company data from IEX
            iex_company = iex_tools.iex_get_company( mdb_symbol["symbol"] )
            #Insert if company data exists
            if not iex_company.empty:
                #Update progress bar
                printProgressBar(index+1, len(mdb_symbols.index), prefix = 'Progress:', suffix = "Inserting company for " + mdb_symbol["symbol"] + "      ", length = 50)
                db.iex_company.insert_many( iex_company.to_dict('records') )
            else:
                #Update progress bar
                printProgressBar(index+1, len(mdb_symbols.index), prefix = 'Progress:', suffix = "No data for " + mdb_symbol["symbol"] + "      ", length = 50)

    #Delete prices before 2018 from MongoDB because it was full
    if delete_prices:
        query = { "date": { "$lt": "2018-01-01" } }
        db.iex_charts.delete_many( query )

    #If new prices exist then upload them
    if insert_prices:
        print( "Insert new charts" )
        #Get all symbols in MongoDB
        mdb_symbols = iex_tools.mdb_get_symbols()
        #Get current date
        currDate = datetime.datetime.now().strftime("%Y-%m-%d")
        #Get latest price in MongoDB for each symbol up to 50 days ago
        mdb_charts = iex_tools.mdb_get_chart( mdb_symbols["symbol"].tolist(), currDate, "latest" )
        #Initial call to print 0% progress
        printProgressBar(0, len(mdb_symbols.index), prefix = 'Progress:', suffix = '', length = 50)
        #Loop through symbols
        for index, mdb_symbol in mdb_symbols.iterrows():
            #Get 1y of charts from IEX
            iex_chart = iex_tools.iex_get_chart( mdb_symbol["symbol"], ref_range='1y' )
            #Get matching chart in MongoDB
            mdb_chart = mdb_charts[ mdb_charts['symbol'] == mdb_symbol["symbol"] ]
            #Select charts more recent than MongoDB
            if not iex_chart.empty and not mdb_chart.empty:
                mask = iex_chart['date'] > mdb_chart['date'].iloc[0]
                iex_chart = iex_chart.loc[mask]
            #Insert if charts exist
            if not iex_chart.empty:
                #Update progress bar
                printProgressBar(index+1, len(mdb_symbols.index), prefix = 'Progress:', suffix = "Inserting chart for " + mdb_symbol["symbol"] + "      ", length = 50)
                #Print write error if couldn't insert charts
                try:
                    db.iex_charts.insert_many( iex_chart.to_dict('records') )
                except BulkWriteError as bwe:
                    print( bwe.details )
                    raise
            else:
                #Update progress bar
                printProgressBar(index+1, len(mdb_symbols.index), prefix = 'Progress:', suffix = "No new data for " + mdb_symbol["symbol"] + "      ", length = 50)

    #If new dividends exist then upload them
    if insert_dividends:
        print( "Insert new dividends" )
        #Get all symbols in MongoDB
        mdb_symbols = iex_tools.mdb_get_symbols()
        #Get current date
        currDate = datetime.datetime.now().strftime("%Y-%m-%d")
        #Get latest dividend in MongoDB for each symbol
        mdb_dividends = iex_tools.mdb_get_dividends( mdb_symbols['symbol'].tolist(), currDate, "latest" )
        #Initial call to print 0% progress
        printProgressBar(0, len(mdb_symbols.index), prefix = 'Progress:', suffix = '', length = 50)
        #Loop through symbols
        for index, mdb_symbol in mdb_symbols.iterrows():
            #Get 1y of dividends from IEX
            iex_dividends = iex_tools.iex_get_dividends( mdb_symbol["symbol"], ref_range='1y' )
            #Get matching dividend in MongoDB
            mdb_dividend = mdb_dividends[ mdb_dividends['symbol'] == mdb_symbol['symbol'] ]
            #Select dividends more recent than MongoDB
            if not mdb_dividend.empty and not iex_dividends.empty:
                mask = iex_dividends['exDate'] > mdb_dividend['exDate'].iloc[0]
                iex_dividends = iex_dividends.loc[mask]
            #Insert if dividends exist
            if not iex_dividends.empty:
                #Update progress bar
                printProgressBar(index+1, len(mdb_symbols.index), prefix = 'Progress:', suffix = "Inserting dividend for " + mdb_symbol["symbol"] + "      ", length = 50)
                db.iex_dividends.insert_many( iex_dividends.to_dict('records') )
            else:
                #Update progress bar
                printProgressBar(index+1, len(mdb_symbols.index), prefix = 'Progress:', suffix = "No new data for " + mdb_symbol["symbol"] + "      ", length = 50)
    
    #If new earnings exist then upload them
    if insert_earnings:
        print( "Insert new earnings" )
        #Get all symbols in MongoDB
        mdb_symbols = iex_tools.mdb_get_symbols()
        #Get current date
        currDate = datetime.datetime.now().strftime("%Y-%m-%d")
        #Get latest earnings in MongoDB for each symbol
        mdb_earnings = iex_tools.mdb_get_earnings( mdb_symbols['symbol'].tolist(), currDate, "latest" )
        #Initial call to print 0% progress
        printProgressBar(0, len(mdb_symbols.index), prefix = 'Progress:', suffix = '', length = 50)
        #Loop through symbols
        for index, mdb_symbol in mdb_symbols.iterrows():
            #Get earnings from IEX
            iex_earnings = iex_tools.iex_get_earnings( mdb_symbol["symbol"] )
            #Get matching earning in MongoDB
            mdb_earning = mdb_earnings[ mdb_earnings['symbol'] == mdb_symbol['symbol'] ]
            #Select earnings more recent than MongoDB
            if not mdb_earning.empty and not iex_earnings.empty:
                mask = iex_earnings['fiscalEndDate'] > mdb_earning['fiscalEndDate'].iloc[0]
                iex_earnings = iex_earnings.loc[mask]
            #Insert if earnings exist
            if not iex_earnings.empty:
                #Update progress bar
                printProgressBar(index+1, len(mdb_symbols.index), prefix = 'Progress:', suffix = "Inserting earnings for " + mdb_symbol["symbol"] + "      ", length = 50)
                db.iex_earnings.insert_many( iex_earnings.to_dict('records') )
            else:
                #Update progress bar
                printProgressBar(index+1, len(mdb_symbols.index), prefix = 'Progress:', suffix = "No new data for " + mdb_symbol["symbol"] + "      ", length = 50)

    #If new financials exist then upload them
    if insert_financials:
        print( "Insert new financials" )
        #Get all symbols in MongoDB
        mdb_symbols = iex_tools.mdb_get_symbols()
        #Get current date
        currDate = datetime.datetime.now().strftime("%Y-%m-%d")
        #Get latest financials in MongoDB for each symbol
        mdb_financials = iex_tools.mdb_get_financials( mdb_symbols['symbol'].tolist(), currDate, "latest" )
        #Initial call to print 0% progress
        printProgressBar(0, len(mdb_symbols.index), prefix = 'Progress:', suffix = '', length = 50)
        #Loop through symbols
        for index, mdb_symbol in mdb_symbols.iterrows():
            #Get financials from IEX
            iex_financials = iex_tools.iex_get_financials( mdb_symbol["symbol"] )
            #Get matching financial in MongoDB
            mdb_financial = mdb_financials[ mdb_financials['symbol'] == mdb_symbol['symbol'] ]
            #Select financials more recent than MongoDB
            if not mdb_financial.empty and not iex_financials.empty:
                mask = iex_financials['reportDate'] > mdb_financial['reportDate'].iloc[0]
                iex_financials = iex_financials.loc[mask]
            #Insert if financials exist
            if not iex_financials.empty:
                #Update progress bar
                printProgressBar(index+1, len(mdb_symbols.index), prefix = 'Progress:', suffix = "Inserting financials for " + mdb_symbol["symbol"] + "      ", length = 50)
                db.iex_financials.insert_many( iex_financials.to_dict('records') )
            else:
                #Update progress bar
                printProgressBar(index+1, len(mdb_symbols.index), prefix = 'Progress:', suffix = "No new data for " + mdb_symbol["symbol"] + "      ", length = 50)

    #TODO:
    #Keep track of corporate actions
    #/ref-data/daily-list/corporate-actions

    #For a given date find the top ranked stocks
    #Insert tables defining the portfolios
    #Insert transactions to deposit cash
    #Insert transactions to buy top ranked stocks
    if insert_portfolio:
        #Build portfolios for 100M, 500M, 1B, 5B, 10B, 50B mcap stocks
        #Insert tables describing the portfolios
        portfolio_tables = [
                            { "portfolioID": "stocks30mcap100M",
                                "name": "30 stocks, 100M market cap",
                                "description": "Portfolio of 30 stocks above 100M market cap with initial investment of 100M USD",
                                "nStocks": 30,
                                "mcapMinimum": 100000000,
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks30mcap500M",
                                "name": "30 stocks, 500M market cap",
                                "description": "Portfolio of 30 stocks above 500M market cap with initial investment of 100M USD",
                                "nStocks": 30,
                                "mcapMinimum": 500000000,
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks30mcap1B",
                                "name": "30 stocks, 1B market cap",
                                "description": "Portfolio of 30 stocks above 1B market cap with initial investment of 100M USD",
                                "nStocks": 30,
                                "mcapMinimum": 1000000000,
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks30mcap5B",
                                "name": "30 stocks, 5B market cap",
                                "description": "Portfolio of 30 stocks above 5B market cap with initial investment of 100M USD",
                                "nStocks": 30,
                                "mcapMinimum": 5000000000,
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks30mcap10B",
                                "name": "30 stocks, 10B market cap",
                                "description": "Portfolio of 30 stocks above 10B market cap with initial investment of 100M USD",
                                "nStocks": 30,
                                "mcapMinimum": 10000000000,
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks30mcap50B",
                                "name": "30 stocks, 50B market cap",
                                "description": "Portfolio of 30 stocks above 50B market cap with initial investment of 100M USD",
                                "nStocks": 30,
                                "mcapMinimum": 50000000000,
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks50mcap100M",
                                "name": "50 stocks, 100M market cap",
                                "description": "Portfolio of 50 stocks above 100M market cap with initial investment of 100M USD",
                                "nStocks": 50,
                                "mcapMinimum": 100000000,
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks50mcap500M",
                                "name": "50 stocks, 500M market cap",
                                "description": "Portfolio of 50 stocks above 500M market cap with initial investment of 100M USD",
                                "nStocks": 50,
                                "mcapMinimum": 500000000,
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks50mcap1B",
                                "name": "50 stocks, 1B market cap",
                                "description": "Portfolio of 50 stocks above 1B market cap with initial investment of 100M USD",
                                "nStocks": 50,
                                "mcapMinimum": 1000000000,
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks50mcap5B",
                                "name": "50 stocks, 5B market cap",
                                "description": "Portfolio of 50 stocks above 5B market cap with initial investment of 100M USD",
                                "nStocks": 50,
                                "mcapMinimum": 5000000000,
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks50mcap10B",
                                "name": "50 stocks, 10B market cap",
                                "description": "Portfolio of 50 stocks above 10B market cap with initial investment of 100M USD",
                                "nStocks": 50,
                                "mcapMinimum": 10000000000,
                                "inceptionDate": "2018-07-02" },
                            { "portfolioID": "stocks50mcap50B",
                                "name": "50 stocks, 50B market cap",
                                "description": "Portfolio of 50 stocks above 50B market cap with initial investment of 100M USD",
                                "nStocks": 50,
                                "mcapMinimum": 50000000000,
                                "inceptionDate": "2018-07-02" }
                            ]
        insert_pf_info = True
        if insert_pf_info:
            print( "Inserting portfolio tables" )
            db.pf_info.insert_many( portfolio_tables )
        print( "Create portfolio transaction tables" )
        #Get latest set of earnings for given date
        #Start portfolio on 2018-07-02 to allow all Q1 2018 results to be reported
        symbols = iex_tools.mdb_get_symbols()['symbol'].tolist()
        print( "Query earnings" )
        earnings = iex_tools.mdb_get_earnings(symbols, "2018-07-02", "latest", "EPSReportDate")
        earnings = earnings[["EPSReportDate","actualEPS","fiscalEndDate","fiscalPeriod","symbol"]]
        #Get financials within 6 months of inception date
        print( "Query financials" )
        financials = iex_tools.mdb_get_financials(symbols, "2018-01-01", "after")
        financials = financials[ financials['reportDate'] <= earnings['fiscalEndDate'].max() ]
        financials = financials[["symbol","reportDate","netIncome","shareholderEquity"]]
        #Get prices for inception date
        print( "Query prices" )
        prices = iex_tools.mdb_get_chart(symbols, "2018-07-02", "on")
        #Get company data
        company = iex_tools.mdb_get_company( symbols )
        company = company[['symbol','companyName','industry','sector']]
        #Merge dataframes together
        print( "Merge dataframes" )
        merged = pandas.merge(earnings,financials,how='inner',left_on=["symbol","fiscalEndDate"],right_on=["symbol","reportDate"],sort=False)
        merged = pandas.merge(merged,prices,how='inner',on="symbol",sort=False)
        merged = pandas.merge(merged,company,how='inner',on='symbol',sort=False)
        #Remove any rows with missing values
        merged = merged.dropna(axis=0, subset=["netIncome","actualEPS","open","shareholderEquity"])
        #Calculate marketCap value
        # price * netIncome / EPS = price * sharesOutstanding = mcap
        # Actually not 100% accurate, should be netIncome - preferred dividend
        # Doesn't perfectly match IEX value or google - probably good enough
        merged["sharesOutstanding"] = merged.netIncome / merged.actualEPS
        merged["marketCap"] = merged.sharesOutstanding * merged.open
        #Calculate PE, ROE, and ratio
        merged["peRatio"] = merged.open / merged.actualEPS
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
        #Define dataframes containing stocks to be bought
        stocks30mcap100M = merged[merged["marketCap"] > 100000000].head(30).reset_index(drop=True)
        stocks30mcap500M = merged[merged["marketCap"] > 500000000].head(30).reset_index(drop=True)
        stocks30mcap1B = merged[merged["marketCap"] > 1000000000].head(30).reset_index(drop=True)
        stocks30mcap5B = merged[merged["marketCap"] > 5000000000].head(30).reset_index(drop=True)
        stocks30mcap10B = merged[merged["marketCap"] > 10000000000].head(30).reset_index(drop=True)
        stocks30mcap50B = merged[merged["marketCap"] > 50000000000].head(30).reset_index(drop=True)
        stocks50mcap100M = merged[merged["marketCap"] > 100000000].head(50).reset_index(drop=True)
        stocks50mcap500M = merged[merged["marketCap"] > 500000000].head(50).reset_index(drop=True)
        stocks50mcap1B = merged[merged["marketCap"] > 1000000000].head(50).reset_index(drop=True)
        stocks50mcap5B = merged[merged["marketCap"] > 5000000000].head(50).reset_index(drop=True)
        stocks50mcap10B = merged[merged["marketCap"] > 10000000000].head(50).reset_index(drop=True)
        stocks50mcap50B = merged[merged["marketCap"] > 50000000000].head(50).reset_index(drop=True)
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
        portfolio_dfs = [ stocks30mcap100M, stocks30mcap500M, stocks30mcap1B, stocks30mcap5B, stocks30mcap10B, stocks30mcap50B, stocks50mcap100M, stocks50mcap500M, stocks50mcap1B, stocks50mcap5B, stocks50mcap10B, stocks50mcap50B ]
        #Build transaction tables to deposit cash into the portfolio
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
        insert_pf_transactions = True
        if insert_pf_transactions:
            db.pf_transactions.insert_many( transaction_tables )
        #Build transaction tables which buy the stocks
        transaction_tables = []
        #Loop through portfolio dataframes
        for portfolio_df in portfolio_dfs:
            #Loop through stocks to be purchased
            for index, stock in portfolio_df.iterrows():
                #Calculate volume of stock to be purchased
                #(Deposit/No. of stocks)/Price rounded to integer
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
        insert_pf_transactions = True
        if insert_pf_transactions:
            db.pf_transactions.insert_many( transaction_tables )

    #Insert holdings table and update when a new transaction is inserted
    #At the moment this won't pick up if more transactions are made on the same day as the last update
    if insert_holdings:
        print( "Calculate portfolio holdings" )
        #Get current date
        currDate = datetime.datetime.now().strftime("%Y-%m-%d")
        #Get existing portfolios
        portfolios = iex_tools.mdb_get_portfolios(currDate)[["portfolioID","inceptionDate"]]
        #Loop through portfolios
        for portfolio_index, portfolio_row in portfolios.iterrows():
            #Get portfolioID and inceptionDate
            portfolio = portfolio_row['portfolioID']
            inceptionDate = portfolio_row['inceptionDate']
            #Default to calculating holdings from inception
            date = inceptionDate
            #Get current holdings table
            holdings = iex_tools.mdb_get_holdings(portfolio, currDate, "on")
            #If holdings exist then calculate holdings from next date
            if not holdings.empty:
                date = holdings['lastUpdated'].max()
                date = (pandas.Timestamp(date) + pandas.DateOffset(days=1)).strftime('%Y-%m-%d')
            #If no existing holdings create 0 dollar entry to create table
            if holdings.empty:
                holding_dict = { "portfolioID": portfolio,
                                    "symbol": "USD",
                                    "endOfDayQuantity": 0.0,
                                    "purchaseValue": 0.0,
                                    "lastUpdated": inceptionDate }
                holdings = pandas.DataFrame.from_dict(holding_dict, orient='index').T
            #Get all new transactions
            transactions = iex_tools.mdb_get_transactions(portfolio, date, "after")
            #Continue if no new transactions
            if transactions.empty:
                print( "No new transactions for " + portfolio )
                continue
            #Loop through dates and update holdings table
            while date <= currDate:
                transactions_date = transactions[transactions.date == date]
                #Loop through transactions
                for t_index, transaction in transactions_date.iterrows():
                    #Get any existing holding for the transaction symbol
                    holding = holdings[holdings.symbol == transaction.symbol]
                    #Remove that holding from holdings table
                    holdings = holdings[ ~holdings["symbol"].isin([transaction.symbol]) ]
                    #Add any deposits to the holdings table
                    if transaction.type == "deposit":
                        holding["endOfDayQuantity"] = holding["endOfDayQuantity"] + (transaction.price * transaction.volume) 
                        holding["purchaseValue"] = holding["purchaseValue"] + (transaction.price * transaction.volume)
                        holding["lastUpdated"] = date
                        holdings = holdings.append( holding, ignore_index=True, sort=False )
                    #Add any stocks purchased to the holdings table
                    if transaction.type == "buy":
                        holding_dict = {}
                        if not holding.empty:
                            holding_dict = { "portfolioID": transaction.portfolioID,
                                            "symbol": transaction.symbol,
                                            "endOfDayQuantity": holding["endOfDayQuantity"] + transaction.volume,
                                            "purchaseValue": holding["purchaseValue"] + (transaction.price * transaction.volume),
                                            "lastUpdated": date }
                        else:
                            holding_dict = { "portfolioID": transaction.portfolioID,
                                            "symbol": transaction.symbol,
                                            "endOfDayQuantity": transaction.volume,
                                            "purchaseValue": (transaction.price * transaction.volume),
                                            "lastUpdated": date }
                        holdings = holdings.append( pandas.DataFrame.from_dict(holding_dict, orient='index').T, ignore_index=True, sort=False )
                        #Adjust cash entry accordingly
                        cash = holdings[holdings.symbol == "USD"]
                        holdings = holdings[ ~holdings["symbol"].isin(["USD"]) ]
                        cash["endOfDayQuantity"] = cash["endOfDayQuantity"] - (transaction.price * transaction.volume)
                        cash["purchaseValue"] = cash["purchaseValue"] - (transaction.price * transaction.volume)
                        cash["lastUpdated"] = date
                        holdings = holdings.append( cash, ignore_index=True, sort=False )
                #Upload new holdings entries to MongoDB
                holdings_date = holdings[holdings.lastUpdated == date]
                if not holdings_date.empty:
                    insert_holdings_tx = True
                    if insert_holdings_tx:
                        print( "Inserting holdings for " + portfolio )
                        db.pf_holdings.insert_many( holdings_date.to_dict('records') )
                #Increment date
                date = (pandas.Timestamp(date) + pandas.DateOffset(days=1)).strftime('%Y-%m-%d')

    #Find out if any dividends were paid to portfolio
    if update_holdings:
        print( "Print if any dividends to be applied" )
        #Update holdings tables to account for dividends paid
        #Calculate portfolio value
        #Monitor dividends and store in cash
        #Get list of portfolios
        portfolios = iex_tools.mdb_get_portfolios("2018-07-02")
        #Loop through portfolios
        for index, portfolio in portfolios.iterrows():
            #Get existing holdings           
            #If any dividend paid add to USD
            portfolioID = portfolio.portfolioID
            inceptionDate = portfolio.inceptionDate
            holdings = iex_tools.mdb_get_holdings(portfolioID, inceptionDate)
            #Look for dividends paid after lastUpdated date
            dividends = iex_tools.mdb_get_dividends(holdings["symbol"].unique().tolist(), inceptionDate, "after")
            if not dividends.empty:
                print( dividends )
            #Find all dividends after date for array of stocks
            #Sort them in date order

    #Insert portfolio performance table
    #Calculate portfolio value - close of day prices for holdings
    #Calculate portfolio return - (close of day holdings - (close of previous day holding + purchases))/(close of previous day holding + purchases)
    if insert_performance:
        print( "Insert portfolio performance tables" )
        #Get current date
        currDate = datetime.datetime.now().strftime("%Y-%m-%d")
        #Get existing portfolios
        portfolios = iex_tools.mdb_get_portfolios(currDate)[["portfolioID","inceptionDate"]]
        #Loop through portfolios
        for portfolio_index, portfolio_row in portfolios.iterrows():
            #Get portfolioID and inceptionDate
            portfolio = portfolio_row.portfolioID
            inceptionDate = portfolio_row.inceptionDate
            print( 'Inserting performance tables for ' + portfolio )
            #Get holdings tables from inception
            holdings = iex_tools.mdb_get_holdings(portfolio, inceptionDate, "after").sort_values(by="lastUpdated", ascending=False, axis="index")
            #Default to calculating performance from inception
            date = inceptionDate
            #Get list of symbols in holdings table
            symbols = holdings["symbol"].unique().tolist()
            #Get existing performance table for portfolio sorted by date
            performance = iex_tools.mdb_get_performance([portfolio], inceptionDate)
            if not performance.empty:
                performance.sort_values(by="date", ascending=False, axis="index", inplace=True)
            #Get close value from last date and increment the date
            perf_tables = []
            prevCloseValue = 0
            adjPrevCloseValue = 0
            if not performance.empty:
                date = performance.iloc[0]["date"]
                date = (pandas.Timestamp(date) + pandas.DateOffset(days=1)).strftime('%Y-%m-%d')
                adjPrevCloseValue = performance.iloc[0]["closeValue"]
                prevCloseValue = performance.iloc[0]["closeValue"]
            #Get prices for symbols in portfolio after date
            prices = iex_tools.mdb_get_chart(symbols, date, "after")
            #If there are no prices then can't calculate performance
            if prices.empty:
                print( "No prices!" )
                continue
            #Get any transactions after date
            transactions = iex_tools.mdb_get_transactions(portfolio, date, "after")
            #Loop through dates
            while date <= currDate:
                #Initialize portfolio close of day values
                closeValue = 0
                adjCloseValue = 0
                #Get latest holding for each symbol on date
                holdings_date = holdings[holdings.lastUpdated <= date]
                holdings_date = holdings_date[holdings_date.groupby(['symbol'], sort=False)['lastUpdated'].transform(max) == holdings['lastUpdated']]
                #Merge with stock prices
                holdings_date = pandas.merge(holdings_date,prices[prices.date == date],how='left',left_on=["symbol"],right_on=["symbol"],sort=False)
                #Skip any day where there aren't prices for all stocks
                if holdings_date[holdings_date.symbol != "USD"].isnull().values.any():
                    date = (pandas.Timestamp(date) + pandas.DateOffset(days=1)).strftime('%Y-%m-%d')
                    continue
                #Calculate portfolio close of day value from close of day stock prices
                if not holdings_date.empty:
                    for index, holding in holdings_date.iterrows():
                        if holding.symbol == "USD":
                            closeValue = closeValue + (holding.endOfDayQuantity)
                        else:
                            closeValue = closeValue + (holding.endOfDayQuantity * holding.close)
                #Get any deposits or withdrawals
                deposits = pandas.DataFrame()
                withdrawals = pandas.DataFrame()
                if not transactions.empty:
                    deposits = transactions[(transactions.date == date) & (transactions.type == "deposit")]
                    withdrawals = transactions[(transactions.date == date) & (transactions.type == "withdrawal")]
                #Adjust close or previous close for withdrawals/deposits
                adjPrevCloseValue = prevCloseValue
                adjCloseValue = closeValue
                if not deposits.empty:
                    for index, deposit in deposits.iterrows():
                        adjPrevCloseValue = adjPrevCloseValue + (deposit.volume * deposit.price)
                if not withdrawals.empty:
                    for index, withdrawal in withdrawals.iterrows():
                        adjCloseValue = adjCloseValue + (withdrawal.volume * withdrawal.price)
                #If portfolio has no holdings or deposits yet then continue
                if adjPrevCloseValue == 0:
                    date = (pandas.Timestamp(date) + pandas.DateOffset(days=1)).strftime('%Y-%m-%d')
                    continue
                #Build portfolio performance table
                perf_table = { "portfolioID": portfolio,
                                "date": date,
                                "prevCloseValue": prevCloseValue,
                                "closeValue": closeValue,
                                "adjPrevCloseValue": adjPrevCloseValue,
                                "adjCloseValue": adjCloseValue,
                                "percentReturn": 100.*((adjCloseValue-adjPrevCloseValue)/adjPrevCloseValue) }
                perf_tables.append( perf_table )
                #Reset previous close values
                prevCloseValue = closeValue
                adjPrevCloseValue = closeValue
                #Increment date
                date = (pandas.Timestamp(date) + pandas.DateOffset(days=1)).strftime('%Y-%m-%d')
            #Insert performance table
            insert_pf_performance = True
            if insert_pf_performance:
                db.pf_performance.insert_many( perf_tables )

    #Store the top ranked stocks for the last week
    if insert_stock_list:
        print( "Insert ranked stock list" )
        #Get current date
        currDate = datetime.datetime.now().strftime("%Y-%m-%d")
        #Delete stock lists older than one week
        #No reason to keep them
        weekBeforeDate = (pandas.Timestamp(currDate) + pandas.DateOffset(days=-7)).strftime('%Y-%m-%d')
        query = { "date": { "$lt": weekBeforeDate } }
        db.pf_stock_list.delete_many( query )
        #Get latest set of earnings for current date
        #print( iex_tools.mdb_get_symbols() )
        symbols = iex_tools.mdb_get_symbols()['symbol'].tolist()
        print( "Query earnings" )
        earnings = iex_tools.mdb_get_earnings(symbols, currDate, "latest", "EPSReportDate")
        earnings = earnings[["EPSReportDate","actualEPS","fiscalEndDate","fiscalPeriod","symbol"]]
        #Get financials within 6 months
        print( "Query financials" )
        sixMonthsBeforeDate = (pandas.Timestamp(currDate) + pandas.DateOffset(months=-6)).strftime('%Y-%m-%d')
        financials = iex_tools.mdb_get_financials(symbols, sixMonthsBeforeDate, "after")
        financials = financials[ financials['reportDate'] <= earnings['fiscalEndDate'].max() ]
        financials = financials[["symbol","reportDate","netIncome","shareholderEquity"]]
        #Get prices for inception date
        print( "Query prices" )
        prices = iex_tools.mdb_get_chart(symbols, currDate, "latest")
        #Skip if latest date already in database
        prices = prices.sort_values(by="date", ascending=False, axis="index")
        pricesDate = prices.iloc[0]["date"]
        latest_stock_list = iex_tools.mdb_get_stock_list(pricesDate, "latest")
        if not latest_stock_list.empty:
            print( "Stock list for today already exists" )
        else:
            #Get company data
            company = iex_tools.mdb_get_company( symbols )
            company = company[['symbol','companyName','industry','sector']]
            #Merge dataframes together
            print( "Merge dataframes" )
            merged = pandas.merge(earnings,financials,how='inner',left_on=["symbol","fiscalEndDate"],right_on=["symbol","reportDate"],sort=False)
            merged = pandas.merge(merged,prices,how='inner',on="symbol",sort=False)
            merged = pandas.merge(merged,company,how='inner',on='symbol',sort=False)
            #Remove any rows with missing values
            merged = merged.dropna(axis=0, subset=["netIncome","actualEPS","open","shareholderEquity"])
            #Calculate marketCap value
            # price * netIncome / EPS = price * sharesOutstanding = mcap
            # Actually not 100% accurate, should be netIncome - preferred dividend
            # Doesn't perfectly match IEX value or google - probably good enough
            merged["sharesOutstanding"] = merged.netIncome / merged.actualEPS
            merged["marketCap"] = merged.sharesOutstanding * merged.open
            #Calculate PE, ROE, and ratio
            merged["peRatio"] = merged.open / merged.actualEPS
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
            insert_pf_stock_list = True
            if insert_pf_stock_list:
                print( "Inserting stock list" )
                db.mdb_stock_list.insert_many( merged.to_dict('records') )
