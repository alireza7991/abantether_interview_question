from decimal import Decimal

from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from exchange.models.currency import Currency
from wallet.models import Wallet


class Order(models.Model):
    user: User = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="orders", verbose_name=_("User")
    )
    currency: Currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name=_("Currency"),
    )
    amount = models.DecimalField(
        max_digits=20, decimal_places=12, verbose_name=_("Amount")
    )

    STATE_PENDING = "P"
    STATE_DONE = "D"
    STATE_CANCELED = "C"
    STATE_FAILED = "F"
    STATE_CHOICES = [
        (
            STATE_PENDING,  # اردر ثبت شده اما هنوز با صرافی خارجی تسویه نشده
            _("Pending"),
        ),
        (
            STATE_DONE,  # اردر ثبت شده و مبلغ با صرافی خارجی تسویه شده
            _("Done"),
        ),
        (
            STATE_CANCELED,  # اردر ثبت شده اما قبل از تسویه از صرافی خارجی توسط کاربر کنسل شده
            _("Canceled"),
        ),
        (
            STATE_FAILED,  # اردر ثبت شده اما در فرایند تسویه یا ... به مشکل خورده است
            _("Failed"),
        ),
    ]
    state = models.CharField(
        default=STATE_PENDING,
        max_length=1,
        choices=STATE_CHOICES,
        verbose_name=_("State"),
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def usd_price(self):
        return self.amount * self.currency.price_usd

    @classmethod
    def create_order(cls, user, currency_code, amount):
        with transaction.atomic():
            currency = Currency.objects.get(code=currency_code)
            wallet = Wallet.objects.get(user=user)
            wallet.withdraw(amount=currency.price_of_amount(amount))
            from exchange.services import OrderProcessService

            order_service = OrderProcessService()
            new_order = cls.objects.create(user=user, currency=currency, amount=amount)
            order_service.handle_order(
                order=new_order
            )  # Process order with external exchange

    def __str__(self) -> str:
        return f"Order({self.user} - {self.currency} - {self.amount})"
