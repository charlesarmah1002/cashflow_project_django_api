from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Account
from .serializers import AccountSerializer

class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
    def get_queryset(self): return Account.objects.filter(business=self.request.user.business, is_active=True)
    def perform_create(self, serializer): serializer.save(business=self.request.user.business)
    def destroy(self, request, *args, **kwargs):
        account = self.get_object(); account.is_active = False; account.save(update_fields=["is_active"]); return Response(status=status.HTTP_204_NO_CONTENT)
