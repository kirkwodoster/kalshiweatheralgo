#from nws_scrape_2nd import check_ema_downtrend
from clients import KalshiClient
import logging
from util import order_pipeline, weather_config
import uuid
import numpy as np
from util import trade_to_csv
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from selenium.webdriver.common.by import By
from datetime import datetime
import requests
from input_variables import *
import xml.etree.ElementTree as ET
import time


kalshi_client = KalshiClient()
client = kalshi_client.get_client()

def trade_execution(market: str, temperatures: list):
    try:
        highest_temp = np.array(temperatures).max()
        highest_temp = int(highest_temp)
        market_ticker = order_pipeline(highest_temp=highest_temp, market=market)
        if market_ticker:
            return 'Market Ticker'
        balance = client.get_balance()['balance'] > 100
        if balance:          
            logging.info('order_pipeline worked')
            order_id = str(uuid.uuid4())
            client.create_order(ticker=market_ticker, client_order_id=order_id)
            logging.info(f'Order Submitted {market_ticker}')
            trade_to_csv(order_id=order_id, ticker=market_ticker)
            logging.info('Trade Saved')
            return True
        else:
            return False
       
    except Exception as e:
        logging.info(f'trade_execution : {e}')
    
def if_temp_reaches_max(current_temp: int, market: str):
    try:
        market_temp_max = list(weather_config(market).items())[-1][1]
        if current_temp >= market_temp_max:
            market_ticker = order_pipeline(highest_temp=current_temp, market=market)
            order_id = str(uuid.uuid4())
            client.create_order(ticker=market_ticker, client_order_id=order_id)
            logging.info(f"Max temp reached and bet made {current_temp}")
            trade_to_csv(order_id=order_id, ticker=market_ticker)
            logging.info('Trade Saved')
            
            return True
    except Exception as e:
        logging.info(f'if_temp_reaches_max : {e}')
    
def xml_scrape(xml_url):

  try: 
    
    response = requests.get(xml_url)
    root = ET.fromstring(response.content)

    start_times = root.findall('.//start-valid-time')
    dates = [time.text for time in start_times]

    temperature_element = root.find('.//temperature[@type="hourly"]')
    value_elements = temperature_element.findall('.//value')
    temp = [int(value.text) for value in value_elements]

    forecasted = pd.DataFrame({'DateTime': dates, 'Temperature': temp})
    forecasted['DateTime'] = pd.to_datetime(forecasted['DateTime'])
    forecasted = forecasted.sort_values(by='DateTime')

    denver_today = datetime.now(TIMEZONE).day

    next_day_high = forecasted[forecasted['DateTime'].dt.day == denver_today]['Temperature'].idxmax()
    date = forecasted['DateTime'].iloc[next_day_high]
    hour_of_high = forecasted['DateTime'].iloc[next_day_high].hour
    temp_high = forecasted['Temperature'].iloc[next_day_high]
    
    return [date, hour_of_high, temp_high]


  except Exception as e:
    logging.error(f"Error scraping XML: {e}")

    
def trade_criteria_met(temperatures, lr_length=LR_LENGTH):
    
    try:
        current_time = datetime.now(TIMEZONE).hour
        hour_max_temp = xml_scrape(xml_url=XML_URL)[1]

        start_scrape = hour_max_temp - 1 >= current_time
        length = len(temperatures) >= lr_length

        if start_scrape and length:
            x = np.arange(0, lr_length).reshape(-1,1)
            temp_length = temperatures[-lr_length:]
            regressor = LinearRegression().fit(x, temp_length)
            slope = regressor.coef_
            if slope <= 0:
                return True
    except Exception as e:
        logging.error(f"Error in trade_criteria_met")
        
def begin_scrape():
    try:
        current_time = datetime.now(TIMEZONE).hour
        
        start_scrape = current_time >= 10
        end_scrape = current_time <= 17
  
        if start_scrape and end_scrape:
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Error in begin_scrape: {e}")
    

# Scrape temperature data from the website
def scrape_temperature(driver):
    
    try:
        driver.get(URL)

        time.sleep(20)  # Wait for the page to load
        tbody = driver.find_element(By.XPATH, "//table[@id='OBS_DATA']/tbody")
        first_row = tbody.find_elements(By.TAG_NAME, "tr")[0]
        cells = first_row.find_elements(By.TAG_NAME, "td")
        
        current_denver_time = datetime.now(TIMEZONE)
        denver_strip = datetime.strftime(current_denver_time, "%A").split(',')
        denver_date = denver_strip[0]
    
        date_scrape = [cell.text.strip() for cell in cells][:2][0]

        date_scrape_format = datetime.strptime(date_scrape, '%b %d, %I:%M %p').strftime('%b %d, %I:%M %p')
       
        final_date = f'{denver_date}, {date_scrape_format},'

        path_element = driver.find_element(By.CSS_SELECTOR, f'path[aria-label*="{final_date}"]')
        aria_label = path_element.get_attribute('aria-label')
        temp = float(aria_label.split(' ')[5][:-1])
      

        return [date_scrape, temp]  # Return date and temperature
        
    except Exception as e:
        logging.error(f"Error scrape_temperature: {e}")
        return None