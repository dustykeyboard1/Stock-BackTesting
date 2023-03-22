from curses import window
from os import posix_spawn
from webbrowser import get
import alpaca_trade_api as tradeapi
import numpy as np 
import time
from alpaca_trade_api.rest import REST, TimeFrame
from datetime import datetime, timedelta
import pandas as pd 
import math
from config import *
import random
from scipy import stats
import pickle
from tqdm import tqdm
import pandas_ta as ta
import matplotlib.pyplot as plt

SEC_KEY = api_secret
PUB_KEY = api_key
BASE_URL = 'https://paper-api.alpaca.markets' # This is the base URL for paper trading
api = tradeapi.REST(key_id= PUB_KEY, secret_key=SEC_KEY, base_url=BASE_URL) # For real trading, don't enter a base_url


df = pd.DataFrame(columns= ['Percent', 'profit/loss', 'sells', 'buys', 
                                'recent price days', 'long price days', 'vol long days', 'vol recent days', 'crosses', 'shares left', 'price percentile'])

def return_ema(data, long_days, short_days, signal):
    recent_data = []
    for item in data:
        recent_data.append(item.c)
    array = pd.Series(recent_data, dtype='float64')
    fast_ema = array.ewm(span = short_days, adjust = False).mean()
    long_ema = array.ewm(span = long_days, adjust = False).mean()
    MACD = fast_ema - long_ema
    signal_line = MACD.ewm(span = signal, adjust = False).mean()
    
    return (MACD.tail(1).item() - signal_line.tail(1).item())
    

def get_percentile(data, value, percentile):
    recent_prices = []
    if value == 'price':
        for price in data:
            recent_prices.append(price.c)
    elif value == 'vol':
        for price in data:
            recent_prices.append(price.v)
    array = np.array(recent_prices)
    return np.percentile(array, percentile)

def get_std(data):
    recent_data = []
    difference_list = []
    for item in data:
        recent_data.append((item.c + item.l + item.h) / 3)
    
    percentage_list = []
    for i in range(20, len(recent_data)):
        temp_array = np.array(recent_data[i - 20:i + 1])
        std = np.std(temp_array) * 2
        mean = np.average(temp_array)
        value = ((mean + std) - (mean - std)) / mean
        percentage_list.append(value)
    
    percent_array = np.array(percentage_list)
    current_array = np.array(recent_data[40:])
    current_mean = np.average(current_array)
    current_std = np.std(current_array) * 2
    current_value = ((current_mean + current_std) - (current_mean - current_std)) / current_mean

    # print(data[-1].S, data[-1].t)
    # print(percent_array)
    # print(np.min(percent_array))
    # print(current_value)
    # print('\n')

    if current_value <= np.min(percent_array):
        squeeze = False
        expand = True
    elif current_value >= np.max(percent_array):
        squeeze = True
        expand = False
    else:
        squeeze = False
        expand = True
    return squeeze, expand

def get_average(data, value):
    recent_price = []
    if value == 'price':
        for item in data:
            recent_price.append(item.c)
    elif value == 'vol':
        for item in data:
            recent_price.append(item.v)
    array = np.array(recent_price)
    return np.average(array)

def get_cost_average(list):
    array = np.array(list)
    return np.average(array)

def sort_market_data(list):
    total_list = []
    individual_list = []
    previous_symbol = list[0].S
    for item in list:
        if item.S != previous_symbol:
            total_list.append(individual_list)
            individual_list = []
            individual_list.append(item)
            previous_symbol = item.S
        else:
            individual_list.append(item)
    total_list.append(individual_list)
    new_list = []
    for item in total_list:
        if len(item) > 5 and item[0].v + item[1].v + item[2].v >= 300000:
            new_list.append(item)
            
    return new_list

def return_full_MACD(list, long_days, short_days, signal):
    recent_data = []
    for item in list:
        recent_data.append(item.c)
    array = pd.Series(recent_data, dtype='float64')
    fast_ema = array.ewm(span = short_days, adjust = False).mean()
    long_ema = array.ewm(span = long_days, adjust = False).mean()
    MACD = fast_ema - long_ema
    signal_line = MACD.ewm(span = signal, adjust = False).mean()
    new_array = MACD - signal_line
    new_array = new_array.tolist()
    return new_array

def create_string_of_stocks(list):
    string = str(list[0][0].S)
    for item in list[1:]:
        string = string + ',' + str(item[0].S)
    return string



stocks_bought = []

for i in tqdm(range(100)):
    startBal = 800
    balance = startBal

    todays_date = datetime.today()
    while todays_date.weekday() != 4:
        todays_date = todays_date - timedelta(1)
    todays_date_formatted = todays_date.strftime ('20%y-%m-%dT%4:00:00Z')
    todays_date_formatted = str(todays_date_formatted)
    
    old_date = datetime.today() - timedelta(290)
    while old_date.weekday() != 0:
        old_date = old_date - timedelta(1)
    old_date_formatted = old_date.strftime ('20%y-%m-%dT%4:00:00Z')
    old_date_formatted = str(old_date_formatted)

    # print(todays_date_formatted)
    # print(old_date_formatted)

    sells = 0
    buys = 0
    shares = 0

    open_file = open('/Users/michaelscoleri/Desktop/QuantTrading/Code/Alpaca/Stock_Bot/full_assets.pkl', "rb")
    full_list = pickle.load(open_file)
    open_file.close()

    if len(full_list) > 95:
        selected_stocks = random.sample(full_list, 95)
    else:
        selected_stocks = full_list

    file2 = open('/Users/michaelscoleri/Desktop/QuantTrading/Code/Alpaca/Stock_Bot/five_assets.pkl', "rb")
    my_stocks = pickle.load(file2)
    file2.close()

    ewm_distance = 30

    recent_average = 3
    long_average = 30

    price_percentile_days = 15
    price_percentile = 25

    recent_vol_days = 3
    long_vol_days = 30

    upper_sell_limit = 1.045
    lower_sell_limit = .85

    std_date_back = 60

    my_list = ['IVV', 'QQQ', 'IJH', 'IJR', 'SUSA', 'VXUS', 'SCHD', 'VIG', 'DNL', 'PDBC', 'RYF', 'RYH', 'PBW', 'XLK', 'VGK',
                'FBND', 'BSCQ', 'TOTL', 'ICSH', 'BKLN', 'VTEB']
    my_list = random.sample(my_list, 8)
    market_data = api.get_bars(my_list, TimeFrame.Day, start = old_date_formatted, 
                end = todays_date_formatted, limit=15000)
    full_list = sort_market_data(market_data)
    
    lists_of_data = []
    for item in full_list:
        if len(item) >= 195:
            lists_of_data.append(item)

    if len(lists_of_data) > 50:
        selected_stocks = random.sample(lists_of_data, 50)
    else:
        selected_stocks = full_list
    
    portfolio = {}
    crosses = 0

    #stock_string = create_string_of_stocks(lists_of_data)
    MACD_dict = {}
    for stock in lists_of_data:
        MACD_dict[stock[0].S] = return_full_MACD(stock, 26, 12, 9)

    for week in range(0,26):
        week_buys = 0
        for day in range(0,5):
            index = week * 5 + day + 62
            for stock in lists_of_data:
                # if index == 62:
                #     print(stock[index].t)
                symbol = stock[0].S
                #Calculate Each statistic
                #Yesterdays Price Averages
                yest_recent_price_average = get_average(stock[index - recent_average - 1:index], 'price')
                yest_long_price_average = get_average(stock[index - long_average - 1:index], 'price')
            
                #Todays Price Averages
                recent_price_average = get_average(stock[index - recent_average:index + 1], 'price')
                long_price_average = get_average(stock[index - long_average:index + 1], 'price')

                #Percentile Price Average
                percentile_price = get_percentile(stock[index - price_percentile_days:index + 1], 'price', price_percentile)

                #Volume Averages
                recent_vol_average = get_average(stock[index - recent_average:index + 1], 'vol')
                long_vol_average = get_average(stock[index - long_average:index + 1], 'vol')
                
                #Standard Deviation
                squeeze, expand = get_std(stock[index - std_date_back:index + 1])
                # if squeeze == True:
                #     print(symbol, stock[index].t)

                #Expoential moving average
                MACD = MACD_dict[symbol][index]
                yesterday_MACD = MACD_dict[symbol][index - 1]
                previous_MACD = MACD_dict[symbol][index - 2]

                # print(symbol)
                # print(stock[index].t)
                # print(MACD, yesterday_MACD)
                #Check for sell
                if symbol in portfolio:
                    if (stock[index].c > (portfolio[symbol][0] * upper_sell_limit) or 
                    squeeze == True):
                        print('date bought: ', portfolio[symbol][2])
                        print('date sold: ',stock[index].t)
                        print('symbol: ', symbol)
                        print('sold: ', stock[index].c)
                        print('bought: ', portfolio[symbol][0])
                        # print('shares sold: ', portfolio[symbol][1])
                        # print(MACD, yesterday_MACD)
                        print('\n')
                        sells +=1
                        balance += stock[index].c * portfolio[symbol][1]
                        del portfolio[symbol]

                #If not already owned, check for buy
                else:
                    if (MACD > yesterday_MACD and expand == True and previous_MACD < yesterday_MACD
                        and week_buys < 4 and balance > 300 and MACD < 0):
                        #print(stock[index].t, symbol, stock[index].c)
                        buys += 1
                        shares = (300 / stock[index].c)
                        balance -= shares * stock[index].c
                        portfolio[symbol] = [stock[index].c, shares, stock[index].t]
                        crosses += 1
                        week_buys += 1
                        stocks_bought.append(symbol)
    
    #Empty portfolio
    shares_held = 0
    for stock in portfolio:
        x = 0
        stocks_bought.append(stock)
        shares_held += 1
        while lists_of_data[x][0].S != stock:
            x += 1

        # print('date bought: ', portfolio[stock][2])
        # print('date sold: ',lists_of_data[x][index].t)
        # print('symbol: ', lists_of_data[x][0].S)
        # print('sold: ', lists_of_data[x][index].c)
        # print('bought: ', portfolio[stock][0])
        balance += lists_of_data[x][index].c * portfolio[stock][1]
        

    #Calulate and append current run results
    total_diff = balance - startBal
    if balance > startBal:
        percent = balance/startBal - 1
    elif (balance < startBal):
        percent = -(1 - balance/startBal)
    else:
        percent = 0

    temp_list = [percent, total_diff, sells, buys, recent_average, long_average,
                long_vol_days, recent_vol_days, crosses, shares_held, price_percentile]
    temp_array = np.array(temp_list)
    df.loc[len(df)] = temp_array

#Create Plot
fig, axis = plt.subplots(3, 2)
fig.set_size_inches(10,10)

axis[0,0].hist(df['profit/loss'], bins = 25)
axis[0,0].set_title('profit/loss')

axis[0,1].hist(df['Percent'], bins = 25)
axis[0,1].set_title('Percent')

axis[1,0].hist(df['buys'], bins = 25)
axis[1,0].set_title('buys')

axis[1,1].boxplot(df['profit/loss'], vert = False)
axis[1,1].set_title('profit/loss')

axis[2,0].boxplot(df['buys'], vert = False)
axis[2,0].set_title('buys')

axis[2,1].boxplot(df['shares left'], vert = False)
axis[2,1].set_title('shares at end')

line3 = ('Recent Days: ' + str(df.loc[1]['recent price days']) + 'Long Days: ' + str(df.loc[1]['long price days']) +
            '\n' + 'lower sell limit: ' + str(lower_sell_limit) + '     upper sell limit: ' + str(upper_sell_limit) +
            '\n' + 'Average Profit/loss: ' + str(df['profit/loss'].mean()) + '\n' +
            'median P/L: ' + str(df['profit/loss'].median()) + '\n' + 'Price Percentile Days: ' + str(df.loc[1]['price percentile']))
plt.suptitle(line3, fontsize = 10)
plt.savefig('/Users/michaelscoleri/Desktop/QuantTrading/Code/Alpaca/Graphs/strat102.png', bbox_inches='tight')

stocks_bought = [*set(stocks_bought)]
print(stocks_bought)