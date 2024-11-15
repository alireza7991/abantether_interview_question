from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _


class Currency(models.Model):
    title = models.CharField(max_length=128, verbose_name=_("Title"))
    code = models.CharField(
        max_length=16, unique=True, db_index=True, verbose_name=_("Code")
    )
    price_usd = models.DecimalField(
        max_digits=20, decimal_places=2, verbose_name=_("Price")
    )
    is_active = models.BooleanField(default=True)

    def price_of_amount(self, amount: Decimal):
        return amount * self.price_usd

    def __str__(self) -> str:
        return f"{self.code} - ${self.price_usdt}"
