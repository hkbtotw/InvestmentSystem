## Automating Stock Investing Technical Analysis With Python
## ref: https://medium.com/fintechexplained/automating-stock-investing-technical-analysis-with-python-81c669e360b2

## RSI period recommended to be set at 14
## ref: https://medium.com/@priceinaction/the-rsi-indicator-explained-e92210d9ffdd

## MACD_1 used to reconfirm the trend up or down to decide if to hold or sell based on other indicators

from ta.momentum import RSIIndicator
from ta.trend import MACD

import numpy as np
import pandas as pd
from ta.volatility import BollingerBands
import math
from datetime import datetime

import os

from matplotlib import pyplot as plt
import numpy as np


class Company:
    def __init__(self, symbol, dfIn, close):
        self.symbol = symbol
        self.technical_indicators = dfIn
        self.prices = dfIn[close]

def set_technical_indicators(config, company):
    company.technical_indicators = pd.DataFrame()
    company.technical_indicators['Close'] = company.prices
    get_macd_2(config,company)
    get_macd(config, company)    
    get_rsi(config, company)
    get_bollinger_bands(config, company)
    
        
def generate_buy_sell_signals(condition_buy, condition_sell, dataframe, strategy):
    last_signal = None
    indicators = []
    buy = []
    sell = []
    for i in range(0, len(dataframe)):
        # if buy condition is true and last signal was not Buy
        if condition_buy(i, dataframe) and last_signal != 'Buy':
            last_signal = 'Buy'
            indicators.append(last_signal)
            buy.append(dataframe['Close'].iloc[i])
            sell.append(np.nan)
        # if sell condition is true and last signal was Buy
        elif condition_sell(i, dataframe)  and last_signal == 'Buy':
            last_signal = 'Sell'
            indicators.append(last_signal)
            buy.append(np.nan)
            sell.append(dataframe['Close'].iloc[i])
        else:
            indicators.append(last_signal)
            buy.append(np.nan)
            sell.append(np.nan)

    dataframe[f'{strategy}_Last_Signal'] = np.array(last_signal)
    dataframe[f'{strategy}_Indicator'] = np.array(indicators)
    dataframe[f'{strategy}_Buy'] = np.array(buy)
    dataframe[f'{strategy}_Sell'] = np.array(sell)
        
def get_macd(config, company):
    close_prices = company.prices
    dataframe = company.technical_indicators
    window_slow = 26
    signal = 9
    window_fast = 12
    macd = MACD(company.prices, window_slow, window_fast, signal)
    dataframe['MACD'] = macd.macd()
    dataframe['MACD_Histogram'] = macd.macd_diff()
    dataframe['MACD_Signal'] = macd.macd_signal()

    generate_buy_sell_signals(
        lambda x, dataframe: dataframe['MACD'].values[x] < dataframe['MACD_Signal'].iloc[x],
        lambda x, dataframe: dataframe['MACD'].values[x] > dataframe['MACD_Signal'].iloc[x],
        dataframe,
        'MACD')
    return dataframe

def get_macd_2(config, company):
    close_prices=company.prices
    dataframe = company.technical_indicators
    
    dfIn_1=dataframe.copy()
    dfIn_1['Close'] = dfIn_1['Close'].replace("null",np.nan)

    dfIn_1=dfIn_1.dropna(subset=['Close'])

    #dfIn_1['Date']=pd.to_datetime(dfIn_1['Date'], format="%Y-%m-%d")
    #dfIn_1=dfIn_1[['Date','Price_inter']].set_index('Date')

    sma_span=200
    sma_50=50
    ema_span=20

    dfIn_1['sma200']=dfIn_1['Close'].rolling(sma_span).mean()
    dfIn_1['sma50']=dfIn_1['Close'].rolling(sma_50).mean()    
    dfIn_1['ema20']=dfIn_1['Close'].ewm(span=ema_span).mean()

    dfIn_1.round(3)
    dfIn_1.dropna(inplace=True)
    dfIn_1.round(3)
    #display(dfIn_1)
    dataframe['sma200'] = dfIn_1['sma200']
    dataframe['sma50']=dfIn_1['sma50']
    dataframe['ema20'] = dfIn_1['ema20']
    generate_buy_sell_signals(
        lambda x, dataframe: dataframe['ema20'].values[x] < dataframe['sma200'].iloc[x],
        lambda x, dataframe: dataframe['ema20'].values[x] > dataframe['sma200'].iloc[x],
        dataframe,
        'MACD_1')
    #display(dataframe)
    return dataframe


def get_rsi(config, company):
    close_prices = company.prices
    dataframe = company.technical_indicators
    rsi_time_period = 14
    #rsi_time_period = 20

    rsi_indicator = RSIIndicator(close_prices, rsi_time_period)
    dataframe['RSI'] = rsi_indicator.rsi()

    low_rsi = 40
    high_rsi = 70

    generate_buy_sell_signals(
        lambda x, dataframe: dataframe['RSI'].values[x] < low_rsi,
        lambda x, dataframe: dataframe['RSI'].values[x] > high_rsi,
    dataframe, 'RSI')

    return dataframe

def get_bollinger_bands(config, company):

    close_prices = company.prices
    dataframe = company.technical_indicators

    window = 20

    indicator_bb = BollingerBands(close=close_prices, window=window, window_dev=2)

    # Add Bollinger Bands features
    dataframe['Bollinger_Bands_Middle'] = indicator_bb.bollinger_mavg()
    dataframe['Bollinger_Bands_Upper'] = indicator_bb.bollinger_hband()
    dataframe['Bollinger_Bands_Lower'] = indicator_bb.bollinger_lband()


    generate_buy_sell_signals(
        lambda x, signal: signal['Close'].values[x] < signal['Bollinger_Bands_Lower'].values[x],
        lambda x, signal: signal['Close'].values[x] > signal['Bollinger_Bands_Upper'].values[x],
        dataframe, 'Bollinger_Bands')

    return dataframe

def plot_price_and_signals(fig, company, data, strategy, axs):
    last_signal_val = data[f'{strategy}_Last_Signal'].values[-1]
    last_signal = 'Unknown' if not last_signal_val else last_signal_val
    title = f'Close Price Buy/Sell Signals using {strategy}.  Last Signal: {last_signal}'
    fig.suptitle(f'Top: {company.symbol} Stock Price. Bottom: {strategy}')
    

    if not data[f'{strategy}_Buy'].isnull().all():
        axs[0].scatter(data.index, data[f'{strategy}_Buy'], color='green', label='Buy Signal', marker='^', alpha=1)       
    if not data[f'{strategy}_Sell'].isnull().all():
        axs[0].scatter(data.index, data[f'{strategy}_Sell'], color='red', label='Sell Signal', marker='v', alpha=1)
    axs[0].plot(company.prices, label='Close Price', color='blue', alpha=0.35)

    
    buyDict=dict(zip(data[f'{strategy}_Buy'],data.index ))   
    sellDict=dict(zip(data[f'{strategy}_Sell'],data.index ))   
    buyList=[]
    buyDateList=[]
    for n in data[f'{strategy}_Buy']:
        if(not math.isnan(n)):            
            buyList.append(buyDict[n])
            buyDateList.append(n)
    for y,x in zip(buyDateList, buyList):
        #label = "{:.2f}".format(float(y))        
        label = x.strftime("%m-%d")
        axs[0].annotate(label, # this is the text
                 (x,y), # this is the point to label
                 textcoords="offset points", # how to position the text
                 color='g',
                 xytext=(0,10), # distance from text to points (x,y)
                 ha='center') # horizontal alignment can be left, right or center
    buyList=[]
    buyDateList=[]
    for n in data[f'{strategy}_Sell']:
        if(not math.isnan(n)):            
            buyList.append(sellDict[n])
            buyDateList.append(n)
    for y,x in zip(buyDateList, buyList):
        #label = "{:.2f}".format(float(y))        
        label = x.strftime("%m-%d")
        axs[0].annotate(label, # this is the text
                 (x,y), # this is the point to label
                 textcoords="offset points", # how to position the text
                 color='r',
                 xytext=(0,10), # distance from text to points (x,y)
                 ha='center') # horizontal alignment can be left, right or center
        
        
    plt.xticks(rotation=45)
    axs[0].set_title(title)
    axs[0].set_xlabel('Date', fontsize=18)
    axs[0].set_ylabel('Close Price', fontsize=18)
    axs[0].legend(loc='upper left')
    axs[0].grid()


def plot_macd(company):
    image = f'images/{company.symbol}_macd.png'
    macd = company.technical_indicators
    #display(macd)

    # Create and plot the graph
    fig, axs = plt.subplots(2, sharex=True, figsize=(13,9))
    plot_price_and_signals(fig, company, macd, 'MACD', axs)

    axs[1].plot(macd['MACD'], label=company.symbol+' MACD', color = 'green')
    axs[1].plot(macd['MACD_Signal'], label='Signal Line', color='orange')
    positive = macd['MACD_Histogram'][(macd['MACD_Histogram'] >= 0)]
    negative = macd['MACD_Histogram'][(macd['MACD_Histogram'] < 0)]
    axs[1].bar(positive.index, positive, color='green')
    axs[1].bar(negative.index, negative, color='red')    
    axs[1].legend(loc='upper left')
    axs[1].grid()
    #print(os.path.abspath(image))
    plt.show()    

def plot_macd_2(company):
    image = f'images/{company.symbol}_macd_1.png'
    macd_1 = company.technical_indicators
    #display(macd)

    # Create and plot the graph
    fig, axs = plt.subplots(2, sharex=True, figsize=(13,9))
    plot_price_and_signals(fig, company, macd_1, 'MACD_1', axs)
    
    axs[1].plot(company.prices, label='Close Price', color='black', alpha=0.35)
    axs[1].plot(macd_1['ema20'], label=company.symbol+' ema20', color = 'green')
    axs[1].plot(macd_1['sma50'], label='sma50', color='blue')
    axs[1].plot(macd_1['sma200'], label='sma200', color='orange')
    axs[1].legend(loc='upper left')
    axs[1].grid()
    #print(os.path.abspath(image))
    plt.show()  
    
def plot_rsi(company):
    image = f'images/{company.symbol}_rsi.png'
    rsi = company.technical_indicators
    low_rsi = 40
    high_rsi = 70

    #plt.style.use('default')
    fig, axs = plt.subplots(2, sharex=True, figsize=(13, 9))
    plot_price_and_signals(fig, company, rsi, 'RSI', axs)
    axs[1].fill_between(rsi.index, y1=low_rsi, y2=high_rsi, color='#adccff', alpha=0.3)
    axs[1].plot(rsi['RSI'], label='RSI', color='blue', alpha=0.35)
    axs[1].legend(loc='upper left')
    axs[1].grid()
    plt.show()

def plot_bollinger_bands(company):
    image = f'images/{company.symbol}_bb.png'
    bollinger_bands = company.technical_indicators

    fig, axs = plt.subplots(2, sharex=True, figsize=(13, 9))

    plot_price_and_signals(fig, company, bollinger_bands, 'Bollinger_Bands', axs)

    axs[1].plot(company.prices, label='Close Price', color='black', alpha=0.35)
    #axs[1].plot(bollinger_bands['Bollinger_Bands_Middle'], label='Middle', color='blue', alpha=0.35)
    axs[1].plot(bollinger_bands['Bollinger_Bands_Upper'], label='Upper', color='green', alpha=0.35)
    axs[1].plot(bollinger_bands['Bollinger_Bands_Lower'], label='Lower', color='red', alpha=0.35)
    axs[1].fill_between(bollinger_bands.index, bollinger_bands['Bollinger_Bands_Lower'], bollinger_bands['Bollinger_Bands_Upper'], alpha=0.1)
    axs[1].legend(loc='upper left')
    axs[1].grid()
    plt.show()    