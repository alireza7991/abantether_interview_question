from decimal import Decimal
import redis
import logging

from django.db import transaction
from django.db.models import Sum, DecimalField
from exchange.models.currency import Currency
from exchange.models.order import Order
from django.contrib.auth.models import User
from django.core.cache import cache
from django_redis import get_redis_connection

from wallet.models import Wallet
from exchange.ext_exchanges import get_exchange_service


class OrderProcessService:
    MINIMUM_EXTERNAL_BUY_AMOUNT_USD = Decimal("10.00")
    exchange_service = get_exchange_service()
    redis_client = get_redis_connection("default")
    CACHE_TTL = 3600  # Cache timeout in seconds (e.g., 1 hour)

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_pending_amount_key(self, currency_code: str) -> str:
        return f"pending_amount_{currency_code}"

    def update_pending_amount_cache(self, currency_code: str, delta: Decimal) -> None:
        """
        Update total pending amount of orders in cache with new delta value
        """
        key = self.get_pending_amount_key(currency_code)
        with self.redis_client.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(key)
                    current_value = pipe.get(key) or b"0.00"
                    current_value = Decimal(current_value.decode("utf-8"))
                    new_value = current_value + delta
                    pipe.multi()
                    pipe.set(key, str(new_value), ex=self.CACHE_TTL)
                    pipe.execute()
                    break
                except redis.WatchError:
                    continue
                except Exception as e:
                    self.logger.error(f"Error updating cache for {currency_code}: {e}")
                    break

    def get_pending_amount_cache(self, currency_code: str):
        """
        Get total pending amount of orders from cache
        """
        key = self.get_pending_amount_key(currency_code)
        pending_amount = self.redis_client.get(key)
        if pending_amount is None:
            # Recalculate if cache is not set
            pending_amount = Order.objects.filter(
                currency__code=currency_code, state=Order.STATE_PENDING
            ).aggregate(total=Sum("amount", output_field=DecimalField()))[
                "total"
            ] or Decimal(
                "0.00"
            )
            self.redis_client.set(key, str(pending_amount), ex=self.CACHE_TTL)
        else:
            pending_amount = Decimal(pending_amount.decode("utf-8"))
        return pending_amount

    def handle_order(self, order: Order):
        """
        Place a new order in queue of pending orders (we just need this to update cache)
        """
        currency_code = order.currency.code
        self.update_pending_amount_cache(
            currency_code=currency_code, delta=order.amount
        )
        self.process_orders(currency_code=currency_code)

    def process_orders(self, currency_code: str):
        """
        Process orders with the external exchange.
         If orders have less than min amount we will wait until we have a min of 10$ total orders.
        """
        with transaction.atomic():
            try:
                # TODO: Since we are getting cached pending amount from redis,
                #  and then we do some ops and set it to zero, we may have race conditions here
                #  thus we should handle this later using pipelines.
                pending_amount = self.get_pending_amount_cache(
                    currency_code=currency_code
                )
                currency = Currency.objects.get(code=currency_code)
                currency_price_in_usd = currency.price_usd
                pending_amount_in_usd = pending_amount * currency_price_in_usd
                if pending_amount_in_usd >= self.MINIMUM_EXTERNAL_BUY_AMOUNT_USD:
                    pending_orders = Order.objects.filter(
                        currency=currency, state=Order.STATE_PENDING
                    ).select_for_update()
                    # Recalculate total pending amount to ensure consistency (e.g. when price changes)
                    total_pending_amount = pending_orders.aggregate(
                        total=Sum("amount", output_field=DecimalField())
                    )["total"] or Decimal("0.00")
                    success = self.exchange_service.buy_from_exchange(
                        currency_code=currency_code, amount=total_pending_amount
                    )
                    if success:
                        pending_orders.update(state=Order.STATE_DONE)
                    else:
                        pending_orders.update(state=Order.STATE_FAILED)
                    self.redis_client.set(
                        self.get_pending_amount_key(currency_code), "0.00"
                    )
            except Exception as e:
                self.logger.error(f"Error processing orders for {currency_code}: {e}")
