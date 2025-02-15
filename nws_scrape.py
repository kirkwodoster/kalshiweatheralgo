import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

import logging
from clients import KalshiClient
from datetime import date
from fake_useragent import UserAgent
from random import randint
from trade_execution_functions import *
from input_variables import *
from util import trade_today

kalshi_client = KalshiClient()
client = kalshi_client.get_client()


def logging_settings():
    return logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Define the log format
    handlers=[logging.StreamHandler()]  # Output logs to the terminal
)


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

# Main function to scrape and process data
def scrape_dynamic_table(driver):
    logging_settings()
    temperatures = []
    dates = []
    
    restart_threshold = 50  # Restart WebDriver every 50 iterations
    loop_counter = 0
    begin_scraping = begin_scrape()
    trade_made_today = trade_today(market=MARKET)

    while True:
        try:
            if begin_scraping and trade_made_today:
                
                scrape_temp = scrape_temperature(driver)
                current_date = scrape_temp[0]
                current_temp = scrape_temp[1]

                if len(dates) == 0 or dates[-1] != current_date:
                    
                    dates.append(current_date)
                    temperatures.append(current_temp)
                    print(f'Dates: {dates}')
                    print(f'Temperatures: {temperatures}')

                    #checks to see if currentc temp is at max of available markets then makes bet
                
                    current_temp_is_max = if_temp_reaches_max(current_temp=current_temp, market = MARKET)
                    if current_temp_is_max:
                        logging.info('Max Temperature Reached')
                       
                        temperatures = []
                        dates = []
                      
                            

                    trade_criteria = trade_criteria_met(temperatures=temperatures, lr_length=LR_LENGTH)
                    if trade_criteria:
                        
                        trade_execute = trade_execution(temperatures=temperatures,market=MARKET)
                        if trade_execute:
                            logging.info('Trade Criteria True')
                            
                           
                            temperatures = []
                            dates = []
                
                else:
                    rand = randint(10, 25)
                    time.sleep(rand)
                    logging.info('to_append is False')
            

        except Exception as e:
            logging.error(f"Error in main loop: {e}")

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
        
