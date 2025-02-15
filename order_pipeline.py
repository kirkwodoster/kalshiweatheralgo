import datetime as dt
import pandas as pd
import numpy as np


def order_pipeline(maxTemp):

    today = dt.date.today()
    todaysDate = today.strftime('%y%b%d').upper()
    market = 'KXHIGHDEN'
    event = f'{market}-{todaysDate}'

    listofMarkets = weather_config(market)
    minMarketTemp = list(listofMarkets.values())[0]
    maxMarketTemp = list(listofMarkets.values())[-1]
    listofMarketsAdj = dict(list(listofMarkets.items())[1:-1])

    if maxTemp < minMarketTemp:
        tempMarket = list(listofMarkets)[0]
    elif maxTemp > maxMarketTemp:
        tempMarket = list(listofMarkets)[-1]
    else:
        for key, value in listofMarketsAdj.items():
            if maxTemp in value:
                tempMarket = key

    return f'{event}-{tempMarket}'



