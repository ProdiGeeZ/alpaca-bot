import pandas as pd

from config import BotConfig
from universe import StockUniverse

from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from datetime import datetime


class DataManager:
    def __init__(self, config: BotConfig, universe: StockUniverse):
        self.config = config
        self.universe = universe

    def get_data(self) -> pd.DataFrame:
        interval, start, end = (
            self.config.data_interval,
            pd.to_datetime(self.config.data_start_date).tz_localize("UTC"),
            datetime.now() - pd.Timedelta(minutes=15),
        )
        df = self.get_data_from_alpaca(interval, start, end)
        df = self.fill_missing_dates(df)
        return df

    def get_data_from_alpaca(
        self, interval: TimeFrame, start: datetime, end: datetime
    ) -> pd.DataFrame:
        request_params = StockBarsRequest(
            symbol_or_symbols=self.universe.to_list(),
            timeframe=interval,
            start=start,
            end=end,
        )
        return self.config.data_client.get_stock_bars(request_params).df.swaplevel()

    def fill_missing_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        df_copy = df.copy()
        df_copy = df_copy.sort_index()
        all_timestamps = df_copy.index.get_level_values("timestamp").unique()
        new_index = pd.MultiIndex.from_product(
            [all_timestamps, self.universe.to_list()], names=["timestamp", "symbol"]
        )
        filled_df = df_copy.reindex(new_index)
        return filled_df


if __name__ == "__main__":
    config = BotConfig("config.yml")
    universe = StockUniverse(config)
    data_manager = DataManager(config, universe)
    df = data_manager.get_data()
    df = df.sort_index()
    print(df)