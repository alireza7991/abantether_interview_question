from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db import models, transaction
from django.contrib.auth.models import User
from decimal import Decimal

from wallet.exceptions import (
    InsufficientBalanceException,
    InvalidWithdrawalAmountException,
)


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="wallet")
    balance = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal("0.00")
    )

    def __str__(self):
        return f"{self.user.username} - {self.balance}$"

    def withdraw(self, amount: Decimal) -> None:
        if amount <= 0:
            raise InvalidWithdrawalAmountException(
                "The withdrawal amount must be positive."
            )
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=self.pk)
            if wallet.balance < amount:
                raise InsufficientBalanceException
            wallet.balance -= amount
            wallet.save()


"""
    Create a wallet for every User upon signup
"""


@receiver(post_save, sender=User)
def create_user_wallet_hook(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.get_or_create(
            user=instance, defaults={"balance": Decimal("0.00")}
        )
