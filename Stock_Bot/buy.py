import alpaca_trade_api as tradeapi
import random
from alpaca_trade_api.rest import REST, TimeFrame
from datetime import datetime, timedelta
import math
from config import *


SEC_KEY = api_secret
PUB_KEY = api_key
BASE_URL = 'https://paper-api.alpaca.markets' # This is the base URL for paper trading
api = tradeapi.REST(key_id= PUB_KEY, secret_key=SEC_KEY, base_url=BASE_URL) # For real trading, don't enter a base_url

weekdays = [0,1,2,3,4]
diff = 2
old_date = datetime.today() - timedelta(diff)

today = datetime.today()
today_formatted = today.strftime ('20%y-%m-%dT%012:00:00Z')
today_formatted = str(today_formatted)

print(old_date.weekday())
while old_date.weekday() not in weekdays:
    diff += 1
    old_date = datetime.today() - timedelta(diff)

old_date = datetime.today() - timedelta(diff + 2)
#old_date = datetime.today() - timedelta(5)
old_date_formatted = old_date.strftime ('20%y-%m-%dT%012:00:00Z')
old_date_formatted = str(old_date_formatted)
obv_previous = 0
obv = 0

print(today_formatted)
print(old_date_formatted)


def get_symbols():
    random.seed(10)
    return_list = []

    assets = api.list_assets(status= 'active')
    #print(assets)
    for a in assets[:300]:
        if a.exchange == 'NYSE' or a.exchange == 'NASDAQ':
            try:
                quote = api.get_latest_bar(a.symbol)
            #print(quote)
            except:
                pass
            if quote.c > 5 and quote.c < 35:
                return_list.append(a.symbol)
    if len(return_list) > 40:
        return random.sample(return_list, 40)
    return return_list

#print(symb_list)
def sort_second(val):
    return val[1]

def calculate_trade(request):

    symb_list = get_symbols()
    print(symb_list)

    obv_vals = []
    short_list = []
    #print(old_date_formatted, today_formatted)
    for symb in symb_list:
        market_data = api.get_bars(symb, TimeFrame.Day, old_date_formatted,
                                   today_formatted, limit = 3)
        
       
        if len(market_data) == 3:
            
            #print(symb, market_data[2].t)
            if market_data[1].c > market_data[0].c:
                obv_previous = market_data[1].v
            elif market_data[1].c < market_data[0].c:
                obv_previous = -(market_data[1].v)

            if market_data[2].c > market_data[1].c:
                obv = obv_previous + market_data[2].v
            elif market_data[2].c < market_data[1].c:
                obv = obv_previous - market_data[2].v

            #print('obv: ', obv)
            #print('previous: ', obv_previous)
            if obv > obv_previous:
                #print(obv, obv_previous, symb)
                pair = []
                pair.append(symb)
                pair.append(obv - obv_previous)
                pair.append(market_data[2].c)
                obv_vals.append(pair)
            elif obv <= obv_previous and market_data[2].c > market_data[2].o:
                #print('triggy')
                pair = []
                print(pair)
                pair.append(symb)
                pair.append(market_data[2].c)
                print(pair)
                short_list.append(pair)
    print(market_data)
    if len(short_list) > 3:
        short_list = short_list[:2]  
    
    print('short list: ') 
    print(short_list)     
    obv_vals.sort(key=sort_second, reverse=True)
    #print(obv_vals[:5])
    message = 'Success'
    #print('here')
    print(obv_vals)
    for items in obv_vals[:5]:
        shares = math.floor(180 / items[2])
        #print('here')
        #print(items[0])
        try:
            print('order submit')
            order = api.submit_order(
                        items[0], # Replace with the ticker of the stock you want to buy
                        shares,
                        'buy',
                        'market', 
                        time_in_force='opg' # Good 'til cancelled
                )
            print(order.status)
            #print('hi')
            
        except Exception as e:
            #print('except')
            print(str(e))

    for items in short_list:
        #print(items[0])
        shares = math.floor(180 / items[1])
        try:
            order = api.submit_order(
                        items[0], # Replace with the ticker of the stock you want to buy
                        shares,
                        'sell',
                        'market', 
                        time_in_force='opg' # Good 'til cancelled
                )
            print(order.status)
        except Exception as e:
            print(str(e))


    return {
        'Message' : message,
        'Success' : 'YES!'
    }

calculate_trade(1)