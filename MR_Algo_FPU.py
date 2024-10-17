from functions_FPU import *

b_count = 0
bd_lst = []
trade_client = TradingClient(P_KEY, S_KEY)
#trade_client = TradingClient(P_KEY, S_KEY, paper=False) to trade real money you'd switch the current trade client variable for this one

account = trade_client.get_account()
b2 = str(account).split(' ')[11].split("'")[1] # parses account info to get the portfolio value
b3 = str(account).split(' ')[15].split("'")[1]# parses account info to get the cash total
folio_value = float(b3)
ttl_cash2 = float(b2)
'''
The above code is present multiple times throughout the program, it gets the current portfolio value and cash available
in your Alpaca account
'''


while folio_value > 145:
    ord_lst = order_change_list(5, 50)
    for i in range(len(ord_lst[0])):
        # I had problems with the Shib float being too small so I just chose to avoid it
        if ord_lst[0][i] != 'SHIB/USD':
            a = get_data(5, 50, ord_lst[0][i])
            print('Symbol:', ord_lst[0][i], 'percent change:', ord_lst[1][i])
            x = mean(a)
            y = standard_dev(a)
            avrg_chng = avrg_percent_change(a)
            t1 = get_current_price(ord_lst[0][i])
            k_buy = (x + (x * avrg_chng)) - (y * 1.25) # lower bound aka buy
            if ttl_cash2 > b_met[2] and b_count + 1 <= b_cursion and t1 < k_buy:
                b_count += 1
                buy(ord_lst[0][i], math.floor(b_met[2])/t1)
                account = trade_client.get_account()
                b2 = str(account).split(' ')[11].split("'")[1]
                b3 = str(account).split(' ')[15].split("'")[1]
                folio_value = float(b3)
                ttl_cash2 = float(b2)
    time.sleep(5) 
    '''
    The above sleep timer is necessary because it prevents the algorithm from buying an asset and then immediately trying to sell it,
    Alpaca API doesn't allow these kinds of trades 
    '''
    for i in read_from_txt("out.txt"):
        e = i.strip()
        e2 = e.strip("( )")
        rst3 = e2.split(',')
        m = float(rst3[1])
        m2 = float(rst3[2])
        sell_str = rst3[0][1:-1]
        b = get_current_price(sell_str)
        prof = ((m -  (m * .0025)) * b) - b_met[2]
        if prof > 0.01:
            b_count -= 1
            sell(sell_str, m)
            account = trade_client.get_account()
            b2 = str(account).split(' ')[11].split("'")[1]
            b3 = str(account).split(' ')[15].split("'")[1]
            folio_value = float(b3)
            ttl_cash2 = float(b2)
        else:
            bd_lst.append(i)
    put_back_lst("glue_3_out.txt", bd_lst)
    bd_lst.clear()
    time.sleep(500)
    '''
    The above sleep timer determines how long the program waits before being he loop again
    ''' 
    account = trade_client.get_account()
    b2 = str(account).split(' ')[11].split("'")[1]
    b3 = str(account).split(' ')[15].split("'")[1]
    folio_value = float(b3)
    ttl_cash2 = float(b2)

# in the event that portfolio value falls below 145 all assets are sold to prevent further losses
if folio_value <= 145:
    for i in read_from_txt("glue_3_out.txt"):
        e = i.strip()
        e2 = e.strip("( )")
        rst3 = e2.split(',')
        m = float(rst3[1])
        m2 = float(rst3[2])
        sell_str = rst3[0][1:-1]
        sell(sell_str, m)