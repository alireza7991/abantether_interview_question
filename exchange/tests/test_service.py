from unittest.mock import patch
from django.test import TestCase
from decimal import Decimal
from exchange.models.currency import Currency
from exchange.models.order import Order
from django.contrib.auth.models import User
from exchange.services import OrderProcessService
from django_redis import get_redis_connection


class OrderProcessServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.currency = Currency.objects.create(
            title="Aban", code="ABAN", price_usd=Decimal("1000.00")
        )
        self.order_service = OrderProcessService()
        self.redis_client = get_redis_connection("default")
        self.pending_amount_key = self.order_service.get_pending_amount_key("ABAN")

    def tearDown(self):
        self.redis_client.flushdb()

    def get_cached_pending_amount(self):
        return Decimal(self.redis_client.get(self.pending_amount_key).decode("utf-8"))

    def test_handle_order_and_cache_update(self):
        order = Order.objects.create(
            user=self.user, currency=self.currency, amount=Decimal("0.00001")
        )
        self.order_service.handle_order(order)
        self.assertEqual(self.get_cached_pending_amount(), order.amount)

    @patch("exchange.services.OrderProcessService.exchange_service")
    def test_handle_order_with_sufficient_amount(self, mock_exchange_service):
        mock_exchange_service.buy_from_exchange.return_value = True
        order = Order.objects.create(
            user=self.user, currency=self.currency, amount=Decimal("0.1")
        )
        self.order_service.handle_order(order=order)
        self.assertEqual(self.get_cached_pending_amount(), Decimal("0.00"))
        order.refresh_from_db()
        self.assertEqual(order.state, Order.STATE_DONE)

    @patch("exchange.services.OrderProcessService.exchange_service")
    def test_process_orders_with_insufficient_amount(self, mock_exchange_service):
        mock_exchange_service.buy_from_exchange.return_value = True
        order = Order.objects.create(
            user=self.user, currency=self.currency, amount=Decimal("0.009")
        )
        self.order_service.handle_order(order=order)
        self.assertEqual(self.get_cached_pending_amount(), order.amount)
        order.refresh_from_db()
        self.assertEqual(order.state, Order.STATE_PENDING)

    @patch("exchange.services.OrderProcessService.exchange_service")
    def test_process_orders_multiple_orders_make_sufficient_amount(
        self, mock_exchange_service
    ):
        mock_exchange_service.buy_from_exchange.return_value = True
        order1 = Order.objects.create(
            user=self.user, currency=self.currency, amount=Decimal("0.006")
        )
        order2 = Order.objects.create(
            user=self.user, currency=self.currency, amount=Decimal("0.004")
        )
        total_amount = order1.amount + order2.amount
        # Place first order, it does not have enough amount
        self.order_service.handle_order(order=order1)
        order1.refresh_from_db()
        self.assertEqual(order1.state, Order.STATE_PENDING)
        self.assertEqual(self.get_cached_pending_amount(), order1.amount)
        # Place second order, it has enough amound when added to prev order
        self.order_service.handle_order(order=order2)
        order1.refresh_from_db()
        order2.refresh_from_db()
        self.assertEqual(order1.state, Order.STATE_DONE)
        self.assertEqual(order2.state, Order.STATE_DONE)
        self.assertEqual(self.get_cached_pending_amount(), Decimal("0.00"))

    @patch("exchange.services.OrderProcessService.exchange_service")
    def test_process_orders_multiple_orders_make_insufficient_amount(
        self, mock_exchange_service
    ):
        mock_exchange_service.buy_from_exchange.return_value = True
        order1 = Order.objects.create(
            user=self.user, currency=self.currency, amount=Decimal("0.006")
        )
        order2 = Order.objects.create(
            user=self.user, currency=self.currency, amount=Decimal("0.003")
        )
        total_amount = order1.amount + order2.amount
        self.order_service.handle_order(order=order1)
        self.assertEqual(self.get_cached_pending_amount(), order1.amount)
        order1.refresh_from_db()
        order2.refresh_from_db()
        self.order_service.handle_order(order=order2)
        self.assertEqual(order1.state, Order.STATE_PENDING)
        self.assertEqual(order2.state, Order.STATE_PENDING)
        self.assertEqual(self.get_cached_pending_amount(), total_amount)
