from config import botConfig
from alpaca.data.requests import StockLatestQuoteRequest

class StockUniverse:
    def __init__(self, config: botConfig) -> None:
        self.config = config
        self.universe = []
        if self.config.use_testing_universe:
            self.load_development_universe()
        else:
            self.load_symbols_from_alpacas()

    def load_development_universe(self) -> None:
        self.universe = [
            "AAPL", "MSFT", "GOOG", "TSLA", "AMZN", "FB", "NFLX", "NVDA", "AMD", "INTC"
        ]

    def load_symbols_from_alpacas(self) -> None:
        universe = [
            x.symbol for x in self.config.trading_client.get_all_assets()
                    if x.tradable 
                    and x.fractionable 
                    and x.shortable 
                    and x.easy_to_borrow 
                    and x.status == "active"
                ]
        self.universe = self.get_symbols_by_price(universe, 25)

    def get_symbols_by_price(self, symbols: list[str], midprice) -> list[str]:
        latest_quotes = self.config.data_client.get_stock_latest_quote(
        StockLatestQuoteRequest(symbol_or_symbols=symbols)
        )
        symbols_to_prices = {
            symbol: (quote.bid_price + quote.ask_price) / 2
            for symbol, quote in latest_quotes.items()
        }
        return [symbol for symbol, price in symbols_to_prices.items() if price > midprice]

if __name__ == "__main__":
    config = botConfig("config.yml")
    universe = StockUniverse(config)
    print(len(universe.universe))  