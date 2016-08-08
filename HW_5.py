'''
HW_5 Computational Investing
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
import matplotlib.pyplot as plt


def BBands(Symbols, d_data):
    #df_close = d_data['close']
    df_close = d_data['close']


    # Creating an empty dataframe
    temp_data_set = copy.deepcopy(df_close)

    for symbol in Symbols:


        temp_data_set[symbol+'20d_ma'] = pd.rolling_mean(temp_data_set[symbol], window=20)
        temp_data_set[symbol+'50d_ma'] = pd.rolling_mean(temp_data_set[symbol], window=50)

        temp_data_set[symbol+'Bol_upper'] = pd.rolling_mean(temp_data_set[symbol], window=20) + 2 * pd.rolling_std(temp_data_set[symbol], 20, min_periods=20)
        temp_data_set[symbol+'Bol_lower'] = pd.rolling_mean(temp_data_set[symbol], window=20) - 2 * pd.rolling_std(temp_data_set[symbol], 20, min_periods=20)

        #bolinger Widths
        #temp_data_set[symbol+'Bol_BW'] = ((temp_data_set[symbol+'Bol_upper'] - temp_data_set[symbol+'Bol_lower']) / temp_data_set[symbol+'20d_ma']) * 100
        #temp_data_set[symbol+'Bol_BW_200MA'] = pd.rolling_mean(temp_data_set[symbol+'Bol_BW'], window=50)  # cant get the 200 daa
        #temp_data_set[symbol+'Bol_BW_200MA'] = temp_data_set[symbol+'Bol_BW_200MA'].fillna(method='backfill')  ##?? ,may not be good
    #'To convert present value of Bollinger bands into -1 to 1:'
        temp_data_set[symbol+'BB_norm']= 2 * (temp_data_set[symbol]-temp_data_set[symbol+'Bol_lower'])/ (temp_data_set[symbol+'Bol_upper']-temp_data_set[symbol+'Bol_lower'])-1
    #boll_val = 2 * ((current_price - lower_band) / (upper_band - lower_band)) - 1
    #temp_data_set.plot(x=temp_data_set.index, y=[symbol, symbol + '20d_ma', symbol + 'Bol_upper', symbol + 'Bol_lower'])
        temp_data_set.plot(x=temp_data_set.index, y=[symbol+'BB_norm'])
        plt.show()


    temp_data_set.to_csv('/Users/jcovino/Desktop/dataSet.csv')
def main(argv):


    #'Implement an indicator in Python using Pandas:
    #Symbol: IBM
    #Startdate: 1 Jan 2009
    #Enddate: 1 Jan 2010
    #20 period lookback'

    dt_start = dt.datetime(2010, 1, 1)
    dt_end = dt.datetime(2011, 1, 1)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')

    Symbols=['MSFT']
    ls_keys = ['close']
    ldf_data = dataobj.get_data(ldt_timestamps, Symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    print d_data


    BBands(Symbols,d_data)

if __name__== "__main__":
    main(argv)
