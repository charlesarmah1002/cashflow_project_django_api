from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from .models import Category, Transaction
from .serializers import CategorySerializer, TransactionSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    def get_queryset(self):
        qs = Category.objects.filter(business=self.request.user.business)
        value = self.request.query_params.get("type")
        return qs.filter(type=value) if value in ("income", "expense") else qs
    def perform_create(self, serializer): serializer.save(business=self.request.user.business)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["account", "category", "type"]
    ordering_fields = ["date", "created_at", "amount"]
    ordering = ["-date", "-created_at"]
    def get_queryset(self):
        qs = Transaction.objects.filter(business=self.request.user.business).select_related("account", "category")
        if self.request.query_params.get("date_from"): qs = qs.filter(date__gte=self.request.query_params["date_from"])
        if self.request.query_params.get("date_to"): qs = qs.filter(date__lte=self.request.query_params["date_to"])
        return qs
    def perform_create(self, serializer): serializer.save(business=self.request.user.business)
