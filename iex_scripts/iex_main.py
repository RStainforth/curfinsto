#!/usr/bin/env python
# Author: J. Walker
# Date: Feb 11th, 2019
# Brief: A short script that uses the 'iex_tools' module to 
#        extract stock information from the IEX API
# Usage: python3 iex_main.py

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
    insert_symbols = False
    insert_company = False
    delete_prices = False
    delete_duplicates = False
    insert_prices = False
    insert_dividends = False
    insert_earnings = False
    insert_financials = False
    insert_portfolio = False
    insert_transactions = False
    insert_holdings = False
    update_holdings = False
    insert_performance = False
    insert_stock_list = False
    export_stock_list = False
    export_performance = True

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
                printProgressBar(index+1, len(symbols.index), prefix = 'Progress:', suffix = "Symbol contains forbidden character: " + symbol["symbol"] + "                     ", length = 50)
                continue
            #If MongoDB empty insert symbol
            if mdb_symbols.empty:
                #Update progress bar
                printProgressBar(index+1, len(symbols.index), prefix = 'Progress:', suffix = "Inserting new symbol: " + symbol["symbol"] + "                     ", length = 50)
                db.iex_symbols.insert_one( symbol.to_dict() )
            #Is symbol already in MongoDB
            mask = (mdb_symbols['iexId'] == symbol['iexId']) & (mdb_symbols['isEnabled'] == symbol['isEnabled']) & (mdb_symbols['name'] == symbol['name']) & (mdb_symbols['type'] == symbol['type']) 
            #Insert if not in MongoDB
            if mdb_symbols.loc[mask].empty:
                #Update progress bar
                printProgressBar(index+1, len(symbols.index), prefix = 'Progress:', suffix = "Inserting new symbol: " + symbol["symbol"] + "                     ", length = 50)
                db.iex_symbols.insert_one( symbol.to_dict() )
            else:
                #Update progress bar
                printProgressBar(index+1, len(symbols.index), prefix = 'Progress:', suffix = "Symbol " + symbol["symbol"] + " already exists                     ", length = 50)

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

    #Delete duplicate entries from prices which were accidentally introduced
    if delete_duplicates:
        iex_tools.mdb_delete_duplicates()

    #If new prices exist then upload them
    if insert_prices:
        print( "Insert new charts" )
        #Get all symbols in MongoDB
        mdb_symbols_full = iex_tools.mdb_get_symbols()
        #Get current date
        currDate = datetime.datetime.now().strftime("%Y-%m-%d")
        #Initial call to print 0% progress
        printProgressBar(0, len(mdb_symbols_full.index), prefix = 'Progress:', suffix = '', length = 50)
        idx_min = 0
        query_num = 1000
        #flag = False
        while idx_min < len(mdb_symbols_full.index):
            #if idx_min > 1:
            #    break
            idx_max = idx_min + query_num
            if idx_max > len(mdb_symbols_full.index):
                idx_max = len(mdb_symbols_full.index)
            mdb_symbols = mdb_symbols_full.iloc[ idx_min:idx_max , : ]
            mdb_symbols.reset_index(drop=True, inplace=True)
            #Get latest price in MongoDB for each symbol up to 50 days ago
            mdb_charts = iex_tools.mdb_get_chart( mdb_symbols["symbol"].tolist(), currDate, "latest" )
            #print( mdb_charts )
            #break
            #Loop through symbols
            for index, mdb_symbol in mdb_symbols.iterrows():
                #Get 1y of charts from IEX
                #print( mdb_symbol )
                #print( mdb_symbol["symbol"] )
                #if mdb_symbol["symbol"] == "ZZZZZZZZZ":
                #    flag = True
                #if not flag:
                #    continue
                iex_chart = iex_tools.iex_get_chart( mdb_symbol["symbol"], ref_range='5d' )
                #Get matching chart in MongoDB
                mdb_chart = mdb_charts[ mdb_charts['symbol'] == mdb_symbol["symbol"] ]
                #Select charts more recent than MongoDB
                if not iex_chart.empty and not mdb_chart.empty:
                    mask = iex_chart['date'] > mdb_chart['date'].iloc[0]
                    iex_chart = iex_chart.loc[mask]
                #Insert if charts exist
                #print( iex_chart )
                if not iex_chart.empty:
                    #Update progress bar
                    printProgressBar(idx_min+index+1, len(mdb_symbols_full.index), prefix = 'Progress:', suffix = "Inserting chart for " + mdb_symbol["symbol"] + "      ", length = 50)
                    #Print write error if couldn't insert charts
                    try:
                        db.iex_charts.insert_many( iex_chart.to_dict('records') )
                    except BulkWriteError as bwe:
                        print( bwe.details )
                        raise
                else:
                    #Update progress bar
                    printProgressBar(idx_min+index+1, len(mdb_symbols_full.index), prefix = 'Progress:', suffix = "No new data for " + mdb_symbol["symbol"] + "      ", length = 50)
            idx_min = idx_min + query_num

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
        flag = False
        #Loop through symbols
        for index, mdb_symbol in mdb_symbols.iterrows():
            if mdb_symbol["symbol"] == "ZZZZZZZZZ":
                flag = True
            if not flag:
                continue
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

    if insert_transactions:
        print( "Create portfolio transaction tables" )
        transactionDate = "2018-07-02"
        dayBeforeDate = (pandas.Timestamp(transactionDate) + pandas.DateOffset(days=-1)).strftime('%Y-%m-%d')
        print( dayBeforeDate )
        #Get ranked stock list for current date
        merged = iex_tools.mdb_calculate_top_stocks(dayBeforeDate)
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
                volume = volume / stock.close
                volume = round(volume)
                transaction_table = { "portfolioID": portfolio_df.iloc[0]["portfolioID"],
                                        "symbol": stock.symbol,
                                        "type": "buy",
                                        "date": "2018-07-02",
                                        "price": stock.close,
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

                #Insert dividends to transactions database and update transactions table
                #Dividends will be ahead of time so will be ready to be added on the correct date
                #Get portfolios
                #Loop through portfolios
                #Get the transactions from inception
                #Get list of all stocks in transactions
                #Loop from inception to current date
                #Get dividends for stocks
                #On exDate get number of shares
                #Add all buys
                #Subtract all sells
                #Is paymentDate in transactions?
                #If not add dividend on paymentDate

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

        #Add this all to insert_holdings
        #Dividends will be ahead of time so will be ready to be added on the correct date
        #Get portfolios
        #Loop through portfolios
        #Get the transactions from inception
        #Get list of all stocks in transactions
        #Loop from inception to current date
        #Get dividends for stocks
        #On exDate get number of shares
        #Add all buys
        #Subtract all sells
        #Is paymentDate in transactions?
        #If not add dividend on paymentDate


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
            #print( holdings )
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
            #print( prices )
            #If there are no prices then can't calculate performance
            if prices.empty:
                print( "No prices!" )
                continue
            #Get any transactions after date
            transactions = iex_tools.mdb_get_transactions(portfolio, date, "after")
            #print( transactions )
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
                #print( holdings_date )
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
                #print( deposits )
                #print( withdrawals )
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
            #print( perf_tables )
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
        #Get ranked stock list for current date
        merged = iex_tools.mdb_calculate_top_stocks(currDate) 
        #Skip if latest date already in database
        latestDate = merged.sort_values(by="date", ascending=False, axis="index")
        latestDate = latestDate.iloc[0]["date"]
        latestStockList = iex_tools.mdb_get_stock_list(latestDate, "on")
        if latestStockList.empty and not merged.empty:
            print( "Inserting stock list" )
            db.stock_list.insert_many( merged.to_dict('records') )

    #Export latest stock lists
    if export_stock_list:
        print( "Exportiing stock list to json" )
        #currDate = datetime.datetime.now().strftime("%Y-%m-%d")
        currDate = "2019-05-01"
        #latestStockList = iex_tools.mdb_get_stock_list(currDate, "latest")
        latestStockList = iex_tools.mdb_calculate_top_stocks(currDate)
        #Check that list is ordered correctly!
        #Export stock list dataframe to json file
        latestStockList.to_json(path_or_buf="stock_list.json", orient="records")

    #Export latest performance
    if export_performance:
        print( "Exporting performance tables to json" )
        #Start date
        startDate = "2018-07-02"
        #Get list of portfolios
        portfolios = iex_tools.mdb_get_portfolios(startDate)["portfolioID"].tolist()
        #Export SPY performance
        spy_charts = iex_tools.mdb_get_chart(["SPY"]).sort_values(by="date", ascending=True, axis="index")
        spy_charts.reset_index(drop=True, inplace=True)
        fst_index = spy_charts[spy_charts.date >= startDate].index[0]-1
        spy_charts = spy_charts[spy_charts.index >= fst_index]
        spy_dates = spy_charts["date"].tolist()
        spy_close = spy_charts["close"].tolist()
        spy_return_vals = [100.*((i/spy_close[0])-1.0) for i in spy_close]
        spy_return = pandas.DataFrame()
        for index, date in enumerate(spy_dates):
            doc = { "date": date, "return": spy_return_vals[index] }
            spy_return = spy_return.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )
        #spy_charts["return"] = 100.*(spy_charts["close"]/spy_charts["close"].iloc[0])-1.0)
        #spy_charts = spy_charts[["date","return"]]
        spy_charts.to_json(path_or_buf="spy_performance.json", orient="records")
        #Get list of portfolios
        portfolios = iex_tools.mdb_get_portfolios(startDate)["portfolioID"].tolist()
        #Loop through portfolios
        for portfolio in portfolios:
            #Get portfolio performance data
            perf_table = iex_tools.mdb_get_performance([portfolio], startDate).sort_values(by="date", ascending=True, axis="index")
            #print( perf_table )
            perf_dates = perf_table["date"].tolist()
            perf_dates.insert(0, spy_charts["date"].iloc[0])
            perf_percent = perf_table["percentReturn"].tolist()
            #perf_close.insert(0, 0.0)
            #print( perf_dates )
            #print( perf_close )
            #print( len(perf_dates) )
            #print( len(perf_close) )
            #for i in range( len(perf_dates) ):
            #    print( '%s %d' % (perf_dates[i], perf_close[i]) )
            perf_return = [0.0]
            for percent in perf_percent:
                perf_return.append( ((((100.0+percent)/100.0)*((100.0+perf_return[-1])/100.0))-1.0)*100.0 )
            #perf_return = [100.*((i/perf_close[0])-1.0) for i in perf_close]
            #print( perf_return )
            #print( len( perf_return ) )
            #print( len( perf_dates ) )
            pf_return = pandas.DataFrame()
            for index, date in enumerate(perf_dates):
                doc = { "date": date, "return": perf_return[index] }
                pf_return = pf_return.append( pandas.DataFrame.from_dict(doc, orient='index').T, ignore_index=True, sort=False )
            pf_return.to_json(path_or_buf=portfolio+"_performance.json", orient="records")
