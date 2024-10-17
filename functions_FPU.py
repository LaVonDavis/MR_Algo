import pandas as pd
import warnings
from alpaca_trade_api.rest import REST
from alpaca.data.historical import CryptoHistoricalDataClient
import alpaca
import time
import math
from alpaca.data.live.crypto import *
from alpaca.data.historical.crypto import *
from alpaca.data.requests import *
from alpaca.data.timeframe import *
from alpaca.trading.client import *
from alpaca.trading.stream import *
from alpaca.trading.requests import *
from alpaca.trading.enums import *
from alpaca.common.exceptions import APIError
warnings.simplefilter(action='ignore')
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

B_URL = "https://paper-api.alpaca.markets"
P_KEY = '' #public key here
S_KEY = '' #secret key here

trade_client = TradingClient(P_KEY, S_KEY, paper=True)
client = CryptoHistoricalDataClient()
api = REST(key_id=P_KEY,secret_key=S_KEY,base_url=B_URL)
req = GetAssetsRequest(asset_class=AssetClass.CRYPTO,status=AssetStatus.ACTIVE)
assets = trade_client.get_all_assets(req)
account = trade_client.get_account()

print(str(account).split(' ')[15].split("'")[0],str(account).split(' ')[15].split("'")[1])
print(str(account).split(' ')[11].split("'")[0],str(account).split(' ')[11].split("'")[1])
b = str(account).split(' ')[11].split("'")[1]
ttl_cash = float(b) - 10
b_cursion = 5
b_amnt = ttl_cash/b_cursion
b_met = (ttl_cash, b_cursion, b_amnt)

s_lst = []
for i in range(len(assets)):
    cleave = re.split("\s", str(assets[i]))
    dismantle = cleave[5]
    s_lst.append(str(dismantle[8:-1]))

s_lst2 = []
for i in s_lst:
    x = i.split('/')
    if x[1] == 'USD':
        s_lst2.append(i)

for i in s_lst2:
    x = i.split('/')
    if x[0] == "USDT":  
        s_lst2.remove(i)
    elif x[0] == 'USDC':
        s_lst2.remove(i)


def get_data(time_int, get_amount, get_symbl):
    crypto_historical_data_client = CryptoHistoricalDataClient()
    opn = []
    opn_fn = []

    for i in range(get_amount):
        x = datetime.now() - timedelta(minutes= i * time_int)
        req = CryptoBarsRequest(
                symbol_or_symbols = [get_symbl],
                timeframe=TimeFrame(amount = 1, unit = TimeFrameUnit.Minute), # specify timeframe
                start = x,                          # specify start datetime, default=the beginning of the current day.
                #end_date=,                                        # specify end datetime, default=now
                limit = 1,                                               # specify limit
                )
        p1 = crypto_historical_data_client.get_crypto_bars(req).df
        opn.append(float(p1.iloc[0][0]))
        '''
        The final list is reversed so that the list is in chronological order, since values are retrieved starting with the newest
        '''
    opn_fn = opn[::-1] 
    return opn_fn

def get_current_price(symbl):
    request_params = CryptoLatestQuoteRequest(symbol_or_symbols=symbl)
    latest_quote = client.get_crypto_latest_quote(request_params)
    return latest_quote[symbl].ask_price

def buy(coin, amount):
    request_params = CryptoLatestQuoteRequest(symbol_or_symbols=coin)
    latest_quote = client.get_crypto_latest_quote(request_params)
    fee = (amount * .0025) * 3 # I multipy the fee by 3 here as a precaution, it's not essential to the algorithm
    purse = ()
    api.submit_order(coin, amount, 'buy', 'market', 'gtc')
    purse += (coin, amount - fee, latest_quote[coin].ask_price)
    f = open("out.txt", "a")
    f.write(str(purse) + '\n')
    f.close()
    return purse

'''
A quick note about Alpaca sell orders, if you choose to use an IOC (immediate or cancel) order instead of
GTC (good till canceled) be aware that a small portion of your coins may remain after you sell
'''

def sell(coin, amount):
   api.submit_order(coin, amount, 'sell', 'market', 'gtc') 

def read_from_txt(input):
    f = open(input, "r")
    rst = f.read()
    f.close()
    rst2 = rst.splitlines()
    return rst2

def put_back_lst(output, lst):
    open(output, 'w').close()
    f = open(output, "a")
    for i in lst:
        f.write(str(i) + '\n' )
    f.close()

def percent_change(num1, num2):
    return (num1 - num2)/num1 * 100

def avrg_percent_change(lst):
    prc_mn = 0
    for i in range(1, len(lst)):
       prc_mn += percent_change(lst[i-1], lst[i])
    return prc_mn/ (len(lst) - 1)

def mean(lst):
    mn = 0
    for i in range(len(lst)):
       mn += lst[i]
    return mn/ len(lst)

def standard_dev(lst):
    mn = mean(lst)
    stnd_dev_in = 0
    for i in range(len(lst)):
        stnd_dev_in += (lst[i] - mn)**2
    return math.sqrt(stnd_dev_in/len(lst))

def order_change_list(data, data2):
    sym_lst = []
    chang_lst = []
    ordered_sym_lst = []
    ordered_chang_lst = []
    fn_lst = []
    for i in s_lst2:
        x = get_data(data, data2, i)
        sym_lst.append(i)
        chang_lst.append(percent_change(x[-1], x[0]))

    while len(chang_lst) > 0:
        x = chang_lst[chang_lst.index(max(chang_lst))]
        ordered_chang_lst.append(x)
        ordered_sym_lst.append(sym_lst[chang_lst.index(max(chang_lst))])
        sym_lst.remove(sym_lst[chang_lst.index(max(chang_lst))])
        chang_lst.remove(x)
    fn_lst.append(ordered_sym_lst)
    fn_lst.append(ordered_chang_lst)
    return fn_lst