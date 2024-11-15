from abc import ABC, abstractmethod
from decimal import Decimal


class BaseExtExchangeService(ABC):
    @abstractmethod
    def buy_from_exchange(self, currency_code: str, amount: Decimal) -> bool:
        """
        * This implementation is Synchronous, should be implemented as async later ... *
        Buy a specified amount of a currency from this external exchange (e.g. Binance).
        Return True if successful, else False.
        """
        pass
