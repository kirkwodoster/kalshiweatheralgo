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
    
    # orders = client.get_orders(event_ticker = 'KXHIGHDEN-25FEB16')['orders']
    # print(orders)
    order_id = '6cabcfa7-0479-4da5-95a4-f5620e47e9a4'
    ticker = 'KXHIGHDEN-25FEB16-T39'
    x = trade_to_csv(order_id = order_id, ticker = ticker)
    print(x)
    

    # driver = nws_scrape.initialize_driver()
    # logging_settings()
    # try:
    #     nws_scrape.scrape_dynamicleac_table(driver)
    # except KeyboardInterrupt:
    #     logging.info("Script interrupted by user.")
    # finally:
    #     driver.quit()
    #     logging.info("WebDriver closed.")



