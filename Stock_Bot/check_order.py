from config import *
import alpaca_trade_api as tradeapi

SEC_KEY = api_secret
PUB_KEY = api_key
BASE_URL = 'https://paper-api.alpaca.markets' # This is the base URL for paper trading
api = tradeapi.REST(key_id= PUB_KEY, secret_key=SEC_KEY, base_url=BASE_URL) # For real trading, don't enter a base_url

                   

order_info = api.get_order('5e6efa20-0a3b-4d6a-aa32-f5c9bf601e31')

print(order_info)