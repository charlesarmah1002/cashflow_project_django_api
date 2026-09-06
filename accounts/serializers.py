from decimal import Decimal
from django.db.models import Q, Sum
from rest_framework import serializers
from .models import Account

class AccountSerializer(serializers.ModelSerializer):
    current_balance = serializers.SerializerMethodField()
    class Meta: model = Account; fields = ("id", "name", "type", "opening_balance", "is_active", "created_at", "current_balance"); read_only_fields = ("is_active", "created_at", "current_balance")
    def get_current_balance(self, obj):
        totals = obj.transactions.values("type").annotate(total=Sum("amount"))
        income = next((x["total"] for x in totals if x["type"] == "income"), Decimal("0"))
        expense = next((x["total"] for x in totals if x["type"] == "expense"), Decimal("0"))
        return obj.opening_balance + income - expense
