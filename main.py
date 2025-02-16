#from cryptography.hazmat.primitives import serialization
#import asyncio
from clients import  KalshiWebSocketClient, KalshiClient
import logging
import nws_scrape
from util import *
from trade_execution_functions import *
import time
from datetime import datetime


kalshi_client = KalshiClient()
client = kalshi_client.get_client()

# Initialize the WebSocket client
ws_client = KalshiWebSocketClient(
    key_id=client.key_id,
    private_key=client.private_key,
    environment=client.environment
)

# Connect via WebSocket
# asyncio.run(ws_client.connect())

if __name__ == "__main__":
    
    
    driver = nws_scrape.initialize_driver()
    logging_settings()
    try:
        nws_scrape.scrape_dynamicleac_table(driver)
    except KeyboardInterrupt:
        logging.info("Script interrupted by user.")
    finally:
        driver.quit()
        logging.info("WebDriver closed.")



