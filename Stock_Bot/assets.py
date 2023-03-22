import pickle
from turtle import pos
from config import *
import alpaca_trade_api as tradeapi
import random
import numpy as np

SEC_KEY = api_secret
PUB_KEY = api_key
BASE_URL = 'https://paper-api.alpaca.markets' # This is the base URL for paper trading
api = tradeapi.REST(key_id= PUB_KEY, secret_key=SEC_KEY, base_url=BASE_URL) # For real trading, don't enter a base_url

assets = api.list_assets(status= 'active')
possible_list = []
quote_list = []
for a in assets:
    if a.exchange == 'NYSE' or a.exchange == 'NASDAQ':
        try:
            quote = api.get_latest_bar(a.symbol)
        except:
            pass
        quote_list.append(quote.v)
        if quote.c < 50 and quote.v > 250:
            possible_list.append(a.symbol)

if len(possible_list) > 5:
    selected_stocks = random.sample(possible_list, 5)
else:
    selected_stocks = possible_list


open_file = open('/Users/michaelscoleri/Desktop/QuantTrading/Code/Alpaca/Stock_Bot/full_assets.pkl', "wb")
pickle.dump(possible_list, open_file)
open_file.close()

open_file = open('/Users/michaelscoleri/Desktop/QuantTrading/Code/Alpaca/Stock_Bot/five_assets.pkl', "wb")
pickle.dump(selected_stocks, open_file)
open_file.close()
