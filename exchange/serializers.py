from rest_framework import serializers


class OrderSerializer(serializers.Serializer):
    currency_code = serializers.CharField(max_length=16)
    amount = serializers.DecimalField(max_digits=20, decimal_places=12)
