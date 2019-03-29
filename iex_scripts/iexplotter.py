#!/usr/bin/env python
# Author: John Walker
# Date: March 10th, 2019
# Brief: A script that uses the 'iexplotter_tools' module to 
#        query the diywealth database and plot stock info
# Usage: ./iexplotter -s <> -b <begin date YYYY-MM-DD> -e <end date YYYY-MM-DD>
#  e.g.: ./iexplotter -s AAPL -b 2018-10-03 -e 2019-02-15
#  Would plot stock information for Apple

import iex_tools
import os
import sys
import string
import datetime
import operator
import argparse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
days = mdates.DayLocator()  # every day
yearFmt = mdates.DateFormatter('%Y')
monthFmt = mdates.DateFormatter('%m')
dayFmt = mdates.DateFormatter('%d')

# Check the date format is valid
def valid_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

if __name__ == '__main__':

    # Parse arguments
    #parser = argparse.ArgumentParser()
    #parser.add_argument('-s', "--symbol", dest="symbol", help='Stock symbol e.g. "AW.UN"', required=True)
    #parser.add_argument('-b', "--startdate", dest="startdate", help="The Start Date - format YYYY-MM-DD ", required=True, type=valid_date)
    #parser.add_argument('-e', "--enddate", dest="enddate", help="The End Date - format YYYY-MM-DD (Inclusive)", required=True, type=valid_date)
    #args = parser.parse_args()

    #Get list of portfolios
    portfolios = iex_tools.mdb_get_portfolios("2018-07-02")["portfolioID"].tolist()
    spy_charts = iex_tools.mdb_get_chart(["SPY"],"2018-06-29").sort_values(by="date", ascending=True, axis="index")
    spy_dates = spy_charts["date"].tolist()
    spy_close = spy_charts["close"].tolist()
    spy_return = [100.*((i/spy_close[0])-1.0) for i in spy_close]
    #Loop through portfolios
    for portfolio in portfolios:
        #if portfolio not in ["stocks50mcap50B"]:
        #    continue
        #Get portfolio performance data
        perf_table = iex_tools.mdb_get_performance([portfolio],"2018-07-02")
        #print( perf_table )
        perf_dates = perf_table["date"].tolist()
        perf_dates.insert(0, "2018-06-29")
        perf_close = perf_table["closeValue"].tolist()
        perf_close.insert(0, 100000000)
        #print( perf_dates )
        #print( perf_close )
        perf_return = [100.*((i/perf_close[0])-1.0) for i in perf_close]

        # Plot the graph
        fig, ax = plt.subplots()
        #lines = ax.plot( spy_dates, spy_return, perf_dates, perf_return )
        l1 = ax.plot( spy_dates, spy_return, label="S&P 500" )
        l2 = ax.plot( perf_dates, perf_return, label="Portfolio" )

        # Format lines
        #l1, l2 = lines
        plt.setp(l1, color='orange')
        plt.setp(l2, color='purple')

        #Create legend
        plt.legend(loc="upper left")

        # Format the ticks
        ax.xaxis.set_major_locator(months)
        ax.xaxis.set_major_formatter(monthFmt)
        ax.xaxis.set_minor_locator(days)

        # Set axis limits
        date_min = spy_dates[0]
        date_max = spy_dates[-1]
        ax.set_xlim( date_min, date_max )

        # Format the coords message box
        def price(x):
                return '$%1.2f' % x
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax.format_ydata = price
        ax.grid(True)

        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()

        plt.xlabel( "Date" )
        plt.ylabel( "% Return" )
        plt.title( portfolio )
        #plt.show()
        plt.savefig(portfolio+".png")

    #Plot portfolio performance vs SPY




        #stock_symbol = str(args.symbol) # Stock symbol to request
        #start_date = args.startdate # Start date
        #end_date = args.enddate.replace(hour=23, minute=59, second=59, microsecond=999999) # Set end date to end of day to be inclusive

        #print( "Plotting information for symbol: " + stock_symbol )
        #plotter_tools.plot_open_value( stock_symbol, start_date, end_date )

        #print( "Top ranked stocks:")
        #top_stocks = plotter_tools.top_stocks_list( start_date )
        #for i, stock in enumerate(top_stocks[:10]):
        #    print( stock + ": " + str(i) )

        #print( "Plotting portfolio valuation: " )
        #start_value = [100.0] * 10
        #plotter_tools.plot_portfolio_value( top_stocks[:10], start_value, start_date, end_date )
