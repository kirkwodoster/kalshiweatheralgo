import pytz

# input variables for nws_scrape
URL = "https://www.weather.gov/wrh/timeseries?site=KDEN&hours=3"
XML_URL = 'https://forecast.weather.gov/MapClick.php?lat=39.8589&lon=-104.6733&FcstType=digitalDWML'
TIMEZONE = pytz.timezone("America/Denver")
SCRAPE_INTERVAL = 30  # Seconds
EMA_COM = 15  # EMA span
SCRAPING_HOURS = (8, 23)  # Hours to consider for trading (6 AM to 4 PM)
TRADE_EXECUTION_HOURS = (10, 15)
MARKET = 'KXHIGHDEN'
LR_LENGTH = 5



