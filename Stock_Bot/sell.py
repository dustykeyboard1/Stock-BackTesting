import alpaca_trade_api as tradeapi
import random
from alpaca_trade_api.rest import REST, TimeFrame
from datetime import datetime, timedelta
import math
from config import *


SEC_KEY = api_secret
PUB_KEY = api_key
BASE_URL = 'https://paper-api.alpaca.markets' # This is the base URL for paper trading
api = tradeapi.REST(key_id= PUB_KEY, secret_key=SEC_KEY, base_url=BASE_URL)


def sell_stock(request):

    positions = api.list_positions()
    #print(positions)
    for spot in positions:
        try:
            if int(spot.qty) > 0:
                order = api.submit_order(
                            spot.symbol, # Replace with the ticker of the stock you want to buy
                            spot.qty,
                            'sell',
                            'market', 
                            'opg' # Good 'til cancelled
                )
            elif int(spot.qty) < 0:
                order = api.submit_order(
                            spot.symbol, # Replace with the ticker of the stock you want to buy
                            abs(int(spot.qty)),
                            'buy',
                            'market', 
                            'opg' # Good 'til cancelled
                )
        

        except Exception as e:
            print(spot.symbol)
            print(str(e))
sell_stock(1)