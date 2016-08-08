import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import itertools
import seaborn as sns
import copy

#simulation function
def update_prices(ID_df_StockEvents,start_date,end_date,Cash):
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(start_date, end_date, dt_timeofday)
    ls_keys = ['close']
    c_dataobj = da.DataAccess('Yahoo')
    stock_list = ID_df_StockEvents['stock'].values
    stock_listSet=set(stock_list)
    ldf_data = c_dataobj.get_data(ldt_timestamps, stock_listSet, ls_keys)
    
    # get data for stocks in time range for keys
    d_data = dict(zip(ls_keys, ldf_data))
    #'actual_close'
    stock_prices=pd.DataFrame(d_data['close'])
    stockprices_copy=stock_prices.copy()
    
    #create trade matrix
    trade_matrix=stockprices_copy.replace(to_replace=stock_prices.values, value=0)
    ID_df_StockEvents.sort_index(inplace=True)
    # update trading matrix- holds quantity of trades, + for buy, - for sell
    i=0
    for line in ID_df_StockEvents.index:
        date=pd.to_datetime(line)
        stock=  ID_df_StockEvents.iloc[i][0]
        buysell=ID_df_StockEvents.iloc[i][1]
        quantity=ID_df_StockEvents.iloc[i][2]
        #print date, stock, buysell, quantity
        currentValue= trade_matrix.get_value(date,stock)
        if buysell=='Buy':
            replace=quantity+currentValue
            trade_matrix.set_value(date,stock,replace)
        else:
            replace=(quantity*-1)+currentValue
            trade_matrix.set_value(date,stock,replace)
        i = i+1
                                                                                           
    # creat and update hold matrix
    hold_matrix=trade_matrix.copy()
    hold_matrix=hold_matrix.cumsum()
    
    #Update Value from hold_matrix, stock_prices and cash
    matrix= hold_matrix * stock_prices
    matrix['cash']=0
    indexes=list( matrix.index)
    place= indexes[0]
    matrix.set_value(place,'cash',Cash)
  
    # update cash holdings 
    i=1
    for line in matrix.index[1:]:
        date=line
        updateCash=matrix.iloc[i-1]['cash']
        for stock in stock_listSet:
            purchasePrice= stock_prices.get_value(date,stock)*trade_matrix.get_value(date,stock)
            #if buying
            if trade_matrix.get_value(date,stock) >0: 
                updateCash=updateCash-purchasePrice

            # if selling
            elif trade_matrix.get_value(date,stock) < 0: 
                updateCash=updateCash+(purchasePrice*-1)
        
            matrix.set_value(date,'cash', updateCash)
            updateCash=matrix.iloc[i]['cash'] 
        i=i+1    
    
    matrix['sum']=matrix.sum(axis=1)
    #print matrix
  
    #graph the plot
    plt.plot(matrix.index, matrix['sum'])
    plt.savefig("Portfolio_Returns.png", dpi=500)

    # caluclate daily returns
    daily_returns=matrix['sum'].copy()
    #daily return function
    tsu.returnize0(daily_returns)
    matrix['DailyReturns']=daily_returns

    returns=matrix['sum'].copy()
    TotalReturn = returns[-1] / returns[0]

    hold_matrix.to_csv('/Users/jcovino/Desktop/Computational_Investing/HW_3/hold_matrix.csv')
    trade_matrix.to_csv('/Users/jcovino/Desktop/Computational_Investing/HW_3/trade_matrix.csv')
    matrix.to_csv('/Users/jcovino/Desktop/Computational_Investing/HW_3/final_matrix.csv')

    stdev=np.std(daily_returns)
    mean=np.mean(daily_returns)
    SharpeRatio=np.sqrt(252)*(mean/stdev)
    #SharpeRatio = np.sqrt(504) * mean / stdev

    print 'mean ', mean
    print 'stdev ', stdev
    print 'Sharp Ratio ', SharpeRatio
    print 'Total Return', TotalReturn
##############################

def find_events(ls_symbols, d_data):
    #df_close = d_data['close']
    df_close = d_data['actual_close']
    ts_market = df_close['SPY']

    print ("Finding Events")

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    #ldt_timestamps[i]
    #for i in range(1, len(ldt_timestamps) - 5)

    # Time stamps for the event range
    ldt_timestamps = df_close.index
    StockEvents=[]
    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)-5):
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
            
            if f_symprice_today < 10 and f_symprice_yest >=10:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1
                #df_events[s_sym].ix[ldt_timestamps[i]]    
                temp=[]
                temp.append(ldt_timestamps[i])
                temp.append(s_sym)
                temp.append('Buy')
                StockEvents.append(temp)
                # add sell events 5 days later
                temp=[]
                temp.append(ldt_timestamps[i+5])
                temp.append(s_sym)
                temp.append('Sell')
                StockEvents.append(temp)
    #print StockEvents
    return df_events, StockEvents

###########################################################################################################################################
# 0      1      2       3   4           5
# year, month, day, stock, buy/sell, # shares
dt_start = dt.datetime(2008, 1, 1)
dt_end = dt.datetime(2009, 12, 31)
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

dataobj = da.DataAccess('Yahoo')
ls_symbols = dataobj.get_symbols_from_list('sp5002012')
ls_symbols.append('SPY')
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))

for s_key in ls_keys:
    d_data[s_key] = d_data[s_key].fillna(method='ffill')
    d_data[s_key] = d_data[s_key].fillna(method='bfill')
    d_data[s_key] = d_data[s_key].fillna(1.0)

df_events,StockEvents = find_events(ls_symbols, d_data)
Cash = 50000
Order=100

df_StockEvents=pd.DataFrame(StockEvents)
df_StockEvents.to_csv('/Users/jcovino/Desktop/Computational_Investing/HW_3/StockEvents.csv')

cols=['Date','stock','Order']
df_StockEvents.columns=cols

#ID_df_StockEvents=df_StockEvents.set_index([TradeDates])
EventDates= df_StockEvents['Date']
ID_df_StockEvents=df_StockEvents.set_index([EventDates])
ID_df_StockEvents.drop('Date',axis=1,inplace=True)

ID_df_StockEvents['Quantity']=Order

# EventProfiler Graph
# ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
#             s_filename='MyEventStudy.pdf', b_market_neutral=True, b_errorbars=True,
#             s_market_sym='SPY')

############Code from HW_3

#print ID_df_StockEvents
priced_DataFrame=update_prices(ID_df_StockEvents,dt_start,dt_end,Cash)


