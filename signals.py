from config import BotConfig
import pandas as pd
from universe import StockUniverse
from data import DataManager


class SignalGenerator:
    def __init__(self, config: BotConfig) -> None:
        self.config = config

    def get_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        LOOKBACK_WINDOW= self.config.signal_lookback_days
        df["close_lookback"] = (
            df["close"].groupby("symbol").shift(LOOKBACK_WINDOW)
            )
        df["momentum"] = (df["close"] - df["close_lookback"]) / df["close_lookback"]
        df.fillna(0, inplace=True)
        return df
    
if __name__ == "__main__":
    config = BotConfig("config.yml")
    universe = StockUniverse(config)
    data_manager = DataManager(config, universe)
    df = data_manager.get_data()
    signal_generator = SignalGenerator(config)
    df_with_signals = signal_generator.get_signals(df)
    print(df_with_signals)