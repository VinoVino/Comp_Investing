'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 23, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Event Profiler Tutorial
#James Covino
QuantInvesting Homework #2


For the $5.0 event with S&P500 in 2012, we find 176 events. Date Range = 1st Jan,2008 to 31st Dec, 2009.
For the $5.0 event with S&P500 in 2008, we find 326 events. Date Range = 1st Jan,2008 to 31st Dec, 2009.
'''


import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
from sys import argv

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""

# Part 2: Create an event study profile of a specific "known" event on S&P 500 stocks, and compare its impact on two groups of stocks.
# The event is defined as when the actual close of the stock price drops below $5.00, more specifically, when:
# price[t-1] >= 5.0
# price[t] < 5.0
# an event has occurred on date t. Note that just because the price is below 5 it is not an event for every day that it is below 5, only on the day it first drops below 5.

# Evaluate this event for the time period January 1, 2008 to December 31, 2009.
# Compare the results using two lists of S&P 500 stocks: A) The stocks that were in the S&P 500 in 2008 (sp5002008.txt), and B) the stocks that were in the S&P 500
# in 2012 (sp5002012.txt).
# These equity lists are in the directory QSData/Yahoo/Lists. You can read them in using the QSTK call
# dataobj = da.DataAccess('Yahoo')
# symbols = dataobj.get_symbols_from_list("sp5002008")
# symbols.append('SPY')


def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    #df_close = d_data['close']
    df_close = d_data['actual_close']
    ts_market = df_close['SPY']

    print ("Finding Events")

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]

            f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1



            # The event is defined as when the actual close of the stock price drops below $5.00, more specifically, when:
            # price[t-1] >= 5.0
            # price[t] < 5.0
            # an event has occurred on date t. Note that just because the price is below 5 it is not an event for every day that it is below 5, only on the day it first drops below 5.

            if f_symprice_today < 10.0 and f_symprice_yest >=10.0:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

            # original code
                # Event is found if the symbol is down more then 3% while the
                # market is up more then 2%
            #if f_symreturn_today <= -0.03 and f_marketreturn_today >= 0.02:
                #df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events


if __name__ == '__main__':
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    #ls_symbols = dataobj.get_symbols_from_list('sp5002012')

    ls_symbols=[]
    with open(argv[1], "r") as fstream:
        for item in fstream.readlines():
            ls_symbols.append(item.rstrip())

    ls_symbols.append('SPY')

    print (ls_symbols)


    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_events = find_events(ls_symbols, d_data)
    print ("Creating Study")
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='MyEventStudy.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
