from rest_framework import generics, permissions
from wallet.models import Wallet
from wallet.serializers import WalletSerializer


class WalletDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Wallet.objects.get(user=self.request.user)
