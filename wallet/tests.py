from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from wallet.exceptions import (
    InsufficientBalanceException,
    InvalidWithdrawalAmountException,
)
from wallet.models import Wallet


class WalletTestCase(TestCase):
    def setUp(self) -> None:
        self.initial_balance = Decimal("100.00")
        self.user: User = User.objects.create_user(
            username="testuser", password="testpass"
        )
        self.wallet = Wallet.objects.get(user=self.user)
        self.wallet.balance = self.initial_balance
        self.wallet.save()

    def test_successful_withdrawal(self) -> None:
        """
        Test that a valid withdrawal decreases the balance correctly.
        """
        withdraw_amount = Decimal("1.53")
        self.wallet.withdraw(withdraw_amount)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, self.initial_balance - withdraw_amount)

    def test_insufficient_balance(self) -> None:
        """
        Test that withdrawing more than the available balance raises a valid exception.
        Verifies that the balance remains unchanged.
        """
        with self.assertRaises(InsufficientBalanceException):
            self.wallet.withdraw(self.initial_balance + Decimal("120.00"))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, self.initial_balance)

    def test_negative_withdrawal(self) -> None:
        """
        Test that withdrawing a negative amount raises an exception.
        Verifies that the balance remains unchanged.
        """
        with self.assertRaises(InvalidWithdrawalAmountException):
            self.wallet.withdraw(Decimal("-10.00"))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, self.initial_balance)

    def test_zero_withdrawal(self) -> None:
        """
        Test that withdrawing zero raises an exception.
        Verifies that the balance remains unchanged.
        """
        with self.assertRaises(InvalidWithdrawalAmountException):
            self.wallet.withdraw(Decimal("0.00"))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, self.initial_balance)
