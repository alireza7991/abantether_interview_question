from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from exchange.models import Order, Currency
from exchange.serializers import OrderSerializer
from exchange.services import OrderProcessService
from wallet.exceptions import (
    InsufficientBalanceException,
    InvalidWithdrawalAmountException,
)


class PlaceOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        currency_code = serializer.validated_data["currency_code"]
        amount = serializer.validated_data["amount"]
        user = request.user
        try:
            Order.create_order(user=user, currency_code=currency_code, amount=amount)
            return Response({"status": "order placed"}, status=status.HTTP_201_CREATED)
        except Currency.DoesNotExist:
            return Response(
                {"error": "Currency not found"}, status=status.HTTP_400_BAD_REQUEST
            )
        except InsufficientBalanceException:
            return Response(
                {"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST
            )
        except InvalidWithdrawalAmountException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
