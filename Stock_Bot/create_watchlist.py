import alpaca_trade_api as tradeapi
import numpy as np 
import time
from alpaca_trade_api.rest import REST, TimeFrame
from datetime import datetime, timedelta
import pandas as pd 

api_key = 'PKYNQ6ORG11ETJX5AED0'
api_secret = 'REeW2fjtXQpXC793q8uxfujI6NWR8BdEcjzt8trU'

SEC_KEY = api_secret
PUB_KEY = api_key
BASE_URL = 'https://paper-api.alpaca.markets' # This is the base URL for paper trading
api = tradeapi.REST(key_id= PUB_KEY, secret_key=SEC_KEY, base_url=BASE_URL) # For real trading, don't enter a base_url

# stocks = pd.read_excel('/Users/michaelscoleri/Desktop/Quant Trading/Code/Alpaca/Stock_Bot/s&p500.xlsx')
# stocks
# stocks = stocks['Ticker'].tolist()

hours_to_test = 4320 #6months  

stocks = ['TSP', 'TCRX', 'TNP', 'AAAU', 'NX', 'FSTR', 'OALC', 'GBR',
          'CLDL', 'YCL', 'BIZD', 'AGIH', 'OB', 'OBE', 'FEDU', 'PLAO', "PLAT",
           "HOWL", 'IGI', 'BB']

watch_list = api.create_watchlist('My List', stocks)
