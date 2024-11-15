from django.urls import path
from exchange.views import PlaceOrderAPIView

urlpatterns = [
    path("orders/place/", PlaceOrderAPIView.as_view(), name="place_order"),
]
