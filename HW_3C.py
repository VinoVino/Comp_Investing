import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import itertools
import seaborn as sns

def update_prices(Indexed_DF,start_date,end_date,TradeDates_dt,Cash):
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(start_date, end_date, dt_timeofday)
    ls_keys = ['close']
    c_dataobj = da.DataAccess('Yahoo')
    stock_list = Indexed_DF['stock'].values
    stock_listSet=set(stock_list)
    print stock_listSet
    ldf_data = c_dataobj.get_data(ldt_timestamps, stock_listSet, ls_keys)
    
    # get data for stocks in time range for keys
    d_data = dict(zip(ls_keys, ldf_data))
    stock_prices=pd.DataFrame(d_data['close'])
    stockprices_copy=stock_prices.copy()
    
    #create trade matrix
    trade_matrix=stockprices_copy.replace(to_replace=stock_prices.values, value=0)
    
    # update trading matrix- holds quantity of trades, + for buy, - for sell
    i=0
    for line in Indexed_DF.index:
        date=pd.to_datetime(line)
        stock=  Indexed_DF.iloc[i][0]
        buysell=Indexed_DF.iloc[i][1]
        quantity=Indexed_DF.iloc[i][2]
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
  
    # take any rows that are above 0 or less than 0 (buy or sell from trade matrix)
    #buys= trade_matrix[(trade_matrix > 0).any(axis=1)]
    #sells= trade_matrix[(trade_matrix < 0).any(axis=1)]
  
    # update cash holdings 
    i=1
    for line in matrix.index[1:]:
        date=line
        updateCash=matrix.iloc[i-1]['cash']
        for stock in stock_listSet:
            purchasePrice= stock_prices.get_value(date,stock)*trade_matrix.get_value(date,stock)
            #purchasePrice= matrix.get_value(date,stock)
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
    matrix.to_csv('/Users/jcovino/Desktop/Computational_Investing/HW_3/final_matrix.csv')
    #graph the plot
    plt.plot(matrix.index, matrix['sum'])
    #plt.xticks(matrix.index, rotation='vertical')
###########################################################################################################################################
# 0      1      2       3   4           5
# year, month, day, stock, buy/sell, # shares

Cash = 1e6
Data_Frame= pd.read_csv("/Users/jcovino/Desktop/Computational_Investing/HW_3/Orders-files/orders2.csv", index_col=0,names=['','Month','Day','stock','order','Quantity'])
startyear= Data_Frame.index[0]
endyear=Data_Frame.index[-1]
start_date = dt.datetime(int(startyear), 1, 1)
end_date = dt.datetime(int(endyear), 12, 31)
## update date in DataFrame -------------year month day
i=0
TradeDates=[]
for line in Data_Frame.index:
    temp=[]
    year=line
    month=Data_Frame.values[i][0]
    day=Data_Frame.values[i][1]
    i=i+1
    TradingDate=str(year) + '-' + str(month) + '-' + str(day) + ' 16:00:00'
    temp.append(TradingDate)
    TradeDates.append(temp[0])
    
# update data frame
#Data_Frame['Date']=TradeDates

TradeDates_dt=pd.to_datetime(TradeDates)
Indexed_DF=Data_Frame.set_index([TradeDates])

Indexed_DF.drop('Day',axis=1,inplace=True)
Indexed_DF.drop('Month',axis=1,inplace=True)
print Indexed_DF

priced_DataFrame=update_prices(Indexed_DF,start_date,end_date,TradeDates_dt,Cash)


