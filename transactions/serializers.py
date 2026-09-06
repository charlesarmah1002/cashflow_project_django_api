from rest_framework import serializers
from .models import Category, Transaction
from accounts.models import Account

class CategorySerializer(serializers.ModelSerializer):
    class Meta: model = Category; fields = ("id", "name", "type", "created_at"); read_only_fields = ("created_at",)

class TransactionSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source="account.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    class Meta: model = Transaction; fields = ("id", "account", "account_name", "category", "category_name", "type", "amount", "description", "date", "created_at"); read_only_fields = ("created_at", "account_name", "category_name")
    def validate(self, attrs):
        business = self.context["request"].user.business
        account = attrs.get("account", getattr(self.instance, "account", None)); category = attrs.get("category", getattr(self.instance, "category", None)); tx_type = attrs.get("type", getattr(self.instance, "type", None))
        if account and account.business_id != business.id: raise serializers.ValidationError({"account": "Account does not belong to your business."})
        if category and category.business_id != business.id: raise serializers.ValidationError({"category": "Category does not belong to your business."})
        if account and not account.is_active: raise serializers.ValidationError({"account": "Account is inactive."})
        if category and tx_type != category.type: raise serializers.ValidationError({"type": "Transaction type must match category type."})
        return attrs
