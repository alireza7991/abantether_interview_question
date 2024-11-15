from django.conf import settings
from exchange.ext_exchanges.base import BaseExtExchangeService
from exchange.ext_exchanges.binance import BinanceExchangeService
from exchange.ext_exchanges.coinex import CoinexExchangeService


def get_exchange_service() -> BaseExtExchangeService:
    """
    Returns target exchange service based on django settings
    """
    exchange = settings.DEFAULT_EXCHANGE_SERVICE.lower()
    if exchange == "binance":
        return BinanceExchangeService()
    elif exchange == "coinbase":
        return CoinexExchangeService()
    else:
        raise ValueError(f"Unsupported exchange service: {exchange}")
