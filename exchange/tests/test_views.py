from decimal import Decimal
from unittest.mock import patch
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from django_redis import get_redis_connection

from exchange.models.currency import Currency
from exchange.models.order import Order
from wallet.models import Wallet


class PlaceOrderAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alireza", password="pwd")
        self.client = APIClient()
        self.unauth_client = APIClient()
        self.client.login(username="alireza", password="pwd")

        self.wallet = Wallet.objects.get(user=self.user)
        self.initial_balance = Decimal("100.00")
        self.wallet.balance = self.initial_balance
        self.wallet.save()

        self.currency = Currency.objects.create(
            title="Aban", code="ABAN", price_usd=Decimal("1000.00")
        )
        self.url = reverse("place_order")

    def tearDown(self):
        self.redis_client = get_redis_connection("default")
        self.redis_client.flushdb()

    @patch("exchange.services.OrderProcessService.handle_order")
    def test_place_order_mocked(self, mock_handle_order):
        """
        Here we just test if handle_order is called correctly or not
         unittests tests of handle_order are in test_service
        """
        mock_handle_order.return_value = None
        data = {"currency_code": "ABAN", "amount": Decimal("0.001")}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "order placed")
        self.assertTrue(mock_handle_order.called)

    def test_place_order_success(self):
        order_value = Decimal("0.001")
        order_value_price_usd = order_value * self.currency.price_usd
        data = {"currency_code": "ABAN", "amount": order_value}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.first().amount, order_value)
        self.wallet.refresh_from_db()
        self.assertEqual(
            self.wallet.balance, self.initial_balance - order_value_price_usd
        )

    def test_place_order_insufficient_balance(self):
        data = {"currency_code": "ABAN", "amount": self.initial_balance * 2}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Insufficient balance")
        self.assertEqual(Order.objects.count(), 0)

    def test_place_order_invalid_currency(self):
        data = {"currency_code": "X", "amount": Decimal("0.001")}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Currency not found")
        self.assertEqual(Order.objects.count(), 0)

    def test_place_order_without_authentication(self):
        data = {"currency_code": "ABAN", "amount": Decimal("0.001")}
        response = self.unauth_client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
