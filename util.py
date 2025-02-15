import datetime as dt
from clients import KalshiClient
import csv
import logging
from input_variables import *
from datetime import datetime


kalshi_client = KalshiClient()
client = kalshi_client.get_client()

def trade_to_csv(order_id : str, ticker: str):
    try:
        trade_data = client.get_fills(order_id = order_id)['fills'][0]
        #Formatting Time
        raw_date = trade_data['created_time']
        raw_date = dt.datetime.strptime(raw_date, '%Y-%m-%dT%H:%M:%S.%fZ')  
        year = raw_date.strftime('%Y-%m-%d')
        time = raw_date.strftime('%H:%M:%S')
        #Ticker
        ticker = trade_data['ticker']
        #Side
        side = trade_data['side']
        #fees
        take_fees = client.get_orders(ticker=ticker)['orders'][0]['taker_fees']
        taker_fill_cost = client.get_orders(ticker=ticker)['orders'][0]['taker_fill_cost']
        fees = take_fees + taker_fill_cost
        #Price
        if side == 'yes':
            price = trade_data['yes_price']
        else:
            price = trade_data['no_price']
        #Portfolio Total
        portfolio_total = client.get_balance()['balance']

        data_to_csv = {
            'year': year,
            'time': time,
            'order_id': order_id,
            'ticker': ticker,
            'side': side,
            'price': price,
            'fees': fees,
            'revenue': None,
            'portfolio_total': portfolio_total
                        }
        column_names = data_to_csv.keys()

        with open('data/trade_data.csv', 'a', newline='') as file:
            writer = csv.DictWriter(file, column_names)
            writer.writerow(data_to_csv)

        return None
    except Exception as e:
        logging.error(f"Error in CSV Write: {e}")

def weather_config(market):
        try:
            today = dt.date.today()
            todays_date = today.strftime('%y%b%d').upper()
            event_ticker = f'{market}-{todays_date}'
                
            event_list = []
            events = client.get_event(event_ticker)  # Ensure getEvent is defined or imported
            for i in range(len(events['markets'])):
                event_list.append(events['markets'][i]['ticker'])

            #temp_adj = []
            temp_adj = []

            event_list = [i.split('-', 2)[-1] for i in event_list]
            counter = 0
            for i in event_list:
                if "T" in i:
                    counter += 1
                    remove_t = i.strip('T')
                    if counter == 1:
                        temp_adj.append(int(remove_t)-2)
                    elif counter == 2:
                        temp_adj.append(int(remove_t)+2) # adjust for rounding error
                        
                elif "B" in i:
                    remove_b = i.strip('B')
                    temp_minus_5 = float(remove_b) - .5
                    #temp_add_5 = float(remove_b) + .5
                    #degree_range = [int(temp_minus_5) , int(temp_add_5)]
                    temp_adj.append(int(temp_minus_5))
            
            degree_dictionary = {k: v for k, v in zip(event_list, temp_adj)}
            return degree_dictionary
        
        except Exception as e:
            logging.info(f'weather_config: {e}')

def order_pipeline(highest_temp: int, market: str):
    
    try:
        today = dt.date.today()
        todaysDate = today.strftime('%y%b%d').upper()
        event = f'{market}-{todaysDate}'

       # tempMarket = None
        listofMarkets = weather_config(market)
        minMarketTemp = list(listofMarkets.values())[0]
        maxMarketTemp = list(listofMarkets.values())[-1]
        listofMarketsAdj = dict(list(listofMarkets.items())[1:-1])

        if highest_temp <= minMarketTemp:
            tempMarket = list(listofMarkets)[0]
        elif highest_temp >= maxMarketTemp:
            tempMarket = list(listofMarkets)[-1]
        else:
            for key, value in listofMarketsAdj.items():
                if highest_temp == value:
                    tempMarket = key
                  
          
        return f'{event}-{tempMarket}'
    except Exception as e:
        logging.info(f"order_pipeline {e}")


def trade_today(market=MARKET):
    try:
        today = datetime.now(TIMEZONE)
        todaysDate = today.strftime('%y%b%d').upper()
        event = f'{market}-{todaysDate}'
        orders = client.get_orders(event_ticker = event)['orders']
        if orders == 0:
            return True

    except Exception as e:
        logging.error(f"Error Trade Today: {e}")

        
def logging_settings():
    return logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Define the log format
    handlers=[logging.StreamHandler()]  # Output logs to the terminal
)


########## old ##############

# def order_pipeline(highest_temp: int, market: str):

#     today = dt.date.today()
#     todaysDate = today.strftime('%y%b%d').upper()
#     event = f'{market}-{todaysDate}'

#     listofMarkets = weather_config(market)
#     minMarketTemp = list(listofMarkets.values())[0]
#     maxMarketTemp = list(listofMarkets.values())[-1]
#     listofMarketsAdj = dict(list(listofMarkets.items())[1:-1])

#     if highest_temp < minMarketTemp:
#         tempMarket = list(listofMarkets)[0]
#     elif highest_temp > maxMarketTemp:
#         tempMarket = list(listofMarkets)[-1]
#     else:
#         for key, value in listofMarketsAdj.items():
#             if highest_temp in value:
#                 tempMarket = key

#     return f'{event}-{tempMarket}'


# def trade_today(market=MARKET):
#     try:
#         today = datetime.now(TIMEZONE)
#         todaysDate = today.strftime('%y%b%d').upper()
#         event = f'{market}-{todaysDate}'
#         orders = client.get_orders(event_ticker = event)['orders']
#         if orders == 0:
#             return True

#     except Exception as e:
#         logging.error(f"Error Trade Today: {e}")