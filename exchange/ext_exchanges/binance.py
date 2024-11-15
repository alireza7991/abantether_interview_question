from decimal import Decimal

from exchange.ext_exchanges.base import BaseExtExchangeService


class BinanceExchangeService(BaseExtExchangeService):
    # * This implementation is Synchronous, should be implemented as async later ... *
    def buy_from_exchange(self, currency_code: str, amount: Decimal) -> bool:
        print(f"Binance: Buying {amount} of {currency_code} from Binance exchange.")
        # Todo: Implement Binance API integration here
        return True
