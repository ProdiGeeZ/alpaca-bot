import pandas as pd
import schedule
import time

from config import BotConfig
from data import DataManager
from portfolio import PortfolioManager
from signals import SignalGenerator
from universe import StockUniverse

class MomentumBot:
    def __init__(self, config: BotConfig) -> None:
        self.config = config
        self.data_manager = DataManager(config, StockUniverse(config))
        self.signal_generator = SignalGenerator(config)
        self.portfolio_manager = PortfolioManager(config)

    def run(self):
        df = self.data_manager.get_data()
        df_with_signals = self.signal_generator.get_signals(df)
        self.portfolio_manager.rebalance(df_with_signals)
        rebalance_interval = 24 # hours
        schedule.every(rebalance_interval).hours.do(
            lambda: self.portfolio_manager.rebalance(df_with_signals)
            )
        
        next_run = schedule.next_run()
        print(f"Next rebalance: {next_run}")

        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    config = BotConfig("config.yml")
    config.log_config()
    bot = MomentumBot(config)
    bot.run()