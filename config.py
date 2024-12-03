from alpaca.data.historical import StockHistoricalDataClient
from alpaca.trading.client import TradingClient
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv

import logging
import yaml
import os

load_dotenv()

api_key = os.getenv("ALPACA_API_KEY")
api_secret = os.getenv("ALPACA_SECRET_KEY")

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO
)

class BotConfig:
    api_key: str
    api_secret: str
    data_interval: TimeFrame
    data_start_date: str
    signal_lookback_days: int
    book_size: int
    use_testing_universe: bool
    data_client: StockHistoricalDataClient
    trading_client: TradingClient

    def __init__(self, config_file: str) -> None:
        try:
            with open(config_file, "r") as file:
                self.config = yaml.safe_load(file)
                logger.info("Configuration loaded successfully.")
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}")

        interval = self.config.get("interval")
        if interval == "Day":
            self.data_interval = TimeFrame.Day
        elif interval == "Hour":
            self.data_interval = TimeFrame.Hour
        else:
            raise ValueError(f"Invalid interval: {interval}")
        
        self.data_start_date = self.config.get("data_start_date")
        self.book_size = self.config.get("book_size")
        self.signal_lookback_days = self.config.get("lookback_days")
        self.use_testing_universe = self.config.get("use_testing_universe")

        self.load_api_keys()

        self.data_client = StockHistoricalDataClient(self.api_key, self.api_secret)
        self.trading_client = TradingClient(self.api_key, self.api_secret)

    def load_api_keys(self, api_key: str | None = None, api_secret: str | None = None):
        self.api_key = api_key or os.getenv("APCA-API-KEY-ID")
        self.api_secret = api_secret or os.getenv("APCA-API-SECRET-KEY")

        if self.api_key is None:
            raise ValueError("API Key not defined. Please set APCA-API-KEY-ID environment variable.")
        if self.api_secret is None:
            raise ValueError("API Secret not defined. Please set APCA-API-SECRET-KEY environment variable.")

    def log_config(self):
        logger.info(f">> Data Interval: {self.data_interval}")
        logger.info(f">> Data Start Date: {self.data_start_date}")
        logger.info(f">> Signal Lookback Days: {self.signal_lookback_days}")
        logger.info(f">> Book Size: {self.book_size}")
        logger.info(f">> Use Testing Universe: {self.use_testing_universe}")
        logger.info(">> API keys loaded successfully.")

if __name__ == "__main__":
    try:
        config = BotConfig("config.yml")
        config.log_config()
    except Exception as e:
        logger.error(f"Error initialising botConfig: {e}")
