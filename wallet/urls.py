from django.urls import path
from wallet.views import WalletDetailAPIView

urlpatterns = [
    path("wallets/", WalletDetailAPIView.as_view(), name="wallet-detail"),
]
