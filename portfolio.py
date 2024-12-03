import math
import pandas as pd

from config import BotConfig
from universe import StockUniverse
from signals import SignalGenerator
from data import DataManager

from alpaca.trading.enums import OrderSide, OrderType, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.models import Order
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.common.exceptions import APIError


class PortfolioManager:
    def __init__(self, config: BotConfig) -> None:
        self.config = config

    def get_target_allocations(self, df: pd.DataFrame) -> pd.DataFrame:
        book_size = self.config.book_size
        allocations = []
        for _, group in df.groupby(level="timestamp"):
            longs = group[group["momentum"] > 0].copy()
            shorts = group[group["momentum"] < 0].copy()
            flats = group[group["momentum"] == 0].copy()

            longs["signal"] = longs["momentum"] / longs["momentum"].abs().sum()
            shorts["signal"] = shorts["momentum"] / shorts["momentum"].abs().sum()
            flats["signal"] = 0

            longs["allocation"] = (book_size / 2) * longs["signal"]
            shorts["allocation"] = (book_size / 2) * shorts["signal"]
            flats["allocation"] = 0

            selected_columns = [
                "close_lookback",
                "close",
                "momentum",
                "signal",
                "allocation",
            ]
            longs = longs[selected_columns]
            shorts = shorts[selected_columns]
            flats = flats[selected_columns]

            allocations.append(pd.concat([longs, shorts, flats]))

        allocations = pd.concat(allocations)

        return allocations

    def notional_to_qty(self, symbol: str, side: OrderSide, notional: float) -> int:
        p = self.config.data_client.get_stock_latest_quote(
            StockLatestQuoteRequest(symbol_or_symbols=symbol)
        )
        bid_price = p[symbol].bid_price
        ask_price = p[symbol].ask_price

        if bid_price == 0 and ask_price == 0:
            return 0
        if bid_price == 0:
            bid_price = ask_price
        if ask_price == 0:
            ask_price = bid_price

        return (
            int(math.floor(notional / ask_price))
            if side == OrderSide.BUY
            else int(math.ceil(notional / bid_price))
        )

    def get_order_requests(
        self, target_positions_notional: dict, active_positions: dict
    ) -> list[MarketOrderRequest]:
        target_positions = {}
        order_sizes = {}
        for symbol, target_position in target_positions_notional.items():
            target_positions[symbol] = self.notional_to_qty(
                symbol,
                OrderSide.BUY if target_position > 0 else OrderSide.SELL,
                target_position,
            )
            order_sizes[symbol] = target_positions[symbol] - active_positions.get(
                symbol, 0
            )

        print(
            pd.DataFrame(
                {
                    "Active Positions": active_positions,
                    "Target Positions": target_positions,
                    "Target Order Sizes": order_sizes,
                }
            )
        )

        order_requests = []
        for symbol, size in order_sizes.items():
            if size > 0:
                order_requests.append(
                    MarketOrderRequest(
                        symbol=symbol,
                        qty=abs(size),
                        side=OrderSide.BUY,
                        type=OrderType.MARKET,
                        time_in_force=TimeInForce.DAY,
                    )
                )
            elif size < 0:
                order_requests.append(
                    MarketOrderRequest(
                        symbol=symbol,
                        qty=abs(size),
                        side=OrderSide.SELL,
                        type=OrderType.MARKET,
                        time_in_force=TimeInForce.DAY,
                    )
                )

        return order_requests

    def get_active_positions_for_universe(
        self, universe: list[str]
    ) -> dict[str, float]:
        positions = {}
        for symbol in universe:
            try:
                positions[symbol] = float(
                    self.config.trading_client.get_open_position(symbol).qty
                )
            except APIError:
                positions[symbol] = 0

        return positions

    def submit_orders(self, order_requests: list[MarketOrderRequest]) -> list[Order]:
        orders = []
        for order_request in order_requests:
            try:
                orders.append(self.config.trading_client.submit_order(order_request))
                print(
                    f"SUCCESS({order_request.side.upper()} {order_request.qty} shares of {order_request.symbol})"
                )
            except APIError as e:
                print(
                    f"ERROR ({order_request.side.upper()} {order_request.qty} shares of {order_request.symbol}): {e}"
                )

        return orders

    def rebalance(self, df_with_signals: pd.DataFrame):
        allocations = self.get_target_allocations(df_with_signals)
        latest_date = str(allocations.index.get_level_values("timestamp").max().date())
        target_positions_notional = (
            allocations.loc[latest_date, "allocation"].droplevel("timestamp").to_dict()
        )
        print(f"{allocations.loc[latest_date, 'signal']}")
        universe = list(df_with_signals.index.get_level_values("symbol").unique())
        active_positions = self.get_active_positions_for_universe(universe)
        order_requests = self.get_order_requests(
            target_positions_notional, active_positions
        )
        orders = self.submit_orders(order_requests)
        return orders


if __name__ == "__main__":
    config = BotConfig("config.yml")
    data_manager = DataManager(config, StockUniverse(config))
    signal_generator = SignalGenerator(config)
    portfolio_manager = PortfolioManager(config)

    df = data_manager.get_data()
    df_with_signals = signal_generator.get_signals(df)

    orders = portfolio_manager.rebalance(df_with_signals)
    print(orders)