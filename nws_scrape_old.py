import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime, date
import pytz
import pandas as pd
import logging
from clients import KalshiClient
import numpy as np
import uuid
from util import trade_to_csv, order_pipeline
from fake_useragent import UserAgent


kalshi_client = KalshiClient()
client = kalshi_client.get_client()

market = 'KXHIGHDEN'


def logging_settings():
    return logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Define the log format
    handlers=[logging.StreamHandler()]  # Output logs to the terminal
)

# Configuration
URL = "https://www.weather.gov/wrh/timeseries?site=KDEN&hours=1"
TIMEZONE = pytz.timezone("America/Denver")
SCRAPE_INTERVAL = 30  # Seconds
EMA_COM = 15  # EMA span
SCRAPING_HOURS = (8, 16)  # Hours to consider for trading (6 AM to 4 PM)
TRADE_EXECUTION_HOURS = (10, 15)



# Initialize Selenium WebDriver
def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-data")
    chrome_options.add_argument("--headless")
    ua = UserAgent()
    chrome_options.add_argument(f"user-agent={ua.random}")
    
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

# Scrape temperature data from the website
def scrape_temperature(driver):
    try:
        driver.get(URL)
        time.sleep(20)  # Wait for the page to load
        tbody = driver.find_element(By.XPATH, "//table[@id='OBS_DATA']/tbody")
        first_row = tbody.find_elements(By.TAG_NAME, "tr")[0]
        cells = first_row.find_elements(By.TAG_NAME, "td")
        return [cell.text.strip() for cell in cells][:2]  # Return date and temperature
    except Exception as e:
        logging.error(f"Error scraping temperature: {e}")
        return None

# Check if the current time is within working hours
def is_within_working_hours():
    current_time = datetime.now(TIMEZONE)
    return SCRAPING_HOURS[0] <= current_time.hour <= SCRAPING_HOURS[1]

# Calculate EMA and check for a downtrend
def check_ema_downtrend(temperatures):
    if len(temperatures) < 2:
        return False
    ema = pd.DataFrame(temperatures).ewm(com=EMA_COM).mean()
    return ema.iloc[-1].values[0] < ema.iloc[-2].values[0]

# Grab ticker based on highest temperature
    
# Main function to scrape and process data
def scrape_dynamic_table(driver):
    logging_settings()
    temperatures = []
    dates = []
    emaList = []
    TRADE_TODAY = None
    
    restart_threshold = 50  # Restart WebDriver every 50 iterations
    loop_counter = 0

    while True:
        try:
            data = scrape_temperature(driver)
            logging.info('data = scrape_temperature')
            if data and date.today() != TRADE_TODAY:
                
                current_date, current_temp = data
                if not dates or dates[-1] != current_date:
                    dates.append(current_date)
                    temperatures.append(float(current_temp))
                    logging.info(f"Date List: {dates}")
                    logging.info(f"Temp List: {temperatures}")
          
                
                    if is_within_working_hours() and check_ema_downtrend(temperatures):
                        highest_temp = np.array(temperatures).max()
                        logging.info(f"Highest Temperature: {highest_temp}")
                        emaList = pd.DataFrame(temperatures).ewm(com=EMA_COM).mean()
                        logging.info(f'EMA List: {emaList}')

                        if client.get_balance()['balance'] > 100:
                            logging.info(f'Balance Enough')
                            market_ticker = order_pipeline(highest_temp=highest_temp, market=market)
                            logging.info(f'Market Ticker: {market_ticker}')
                            order_id = str(uuid.uuid4())
                            client.create_order(ticker=market_ticker, client_order_id=order_id)
                            TRADE_TODAY = date.today()
                            temperatures = []
                            dates = []
                            emaList = []
                            logging.info(f'Order Submitted Maybe {market_ticker}')
                            trade_to_csv(order_id=order_id, ticker=market_ticker)
                            
            else:
                if  date.today() == TRADE_TODAY:
                    logging.info('waiting until tomorrow for next trade')
            
                else:
                    logging.warning("No data scraped, restarting WebDriver...")
                    driver.quit()
                    driver = initialize_driver()  # Restart WebDriver

        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            driver.quit()
            driver = initialize_driver()  # Restart WebDriver on failure

        # Restart WebDriver every 50 iterations to prevent memory issues
        loop_counter += 1
        if loop_counter >= restart_threshold:
            logging.info("Restarting WebDriver to prevent stale sessions...")
            driver.quit()
            driver = initialize_driver()
            loop_counter = 0  # Reset counter

        time.sleep(SCRAPE_INTERVAL)




# Entry point
if __name__ == "__main__":
    
    driver = initialize_driver()
    try:
        scrape_dynamic_table(driver)
    except KeyboardInterrupt:
        logging.info("Script interrupted by user.")
    finally:
        driver.quit()
        logging.info("WebDriver closed.")