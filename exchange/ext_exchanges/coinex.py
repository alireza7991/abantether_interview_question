from decimal import Decimal

from exchange.ext_exchanges.base import BaseExtExchangeService


class CoinexExchangeService(BaseExtExchangeService):
    # * This implementation is Synchronous, should be implemented as async later ... *
    def buy_from_exchange(self, currency_code: str, amount: Decimal) -> bool:
        print(f"Coinex: Buying {amount} of {currency_code} from Coinex exchange.")
        # Todo: Implement Coinex API integration here
        return True
