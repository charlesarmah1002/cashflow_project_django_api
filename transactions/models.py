from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from core.models import Business
from accounts.models import Account

class Category(models.Model):
    class CategoryType(models.TextChoices): INCOME="income", "Income"; EXPENSE="expense", "Expense"
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=CategoryType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: constraints = [models.UniqueConstraint(fields=["business", "name", "type"], name="unique_category_per_business_type")]

class Transaction(models.Model):
    class TransactionType(models.TextChoices): INCOME="income", "Income"; EXPENSE="expense", "Expense"
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="transactions")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="transactions")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="transactions")
    type = models.CharField(max_length=10, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    description = models.CharField(max_length=500, blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: indexes = [models.Index(fields=["business", "date"]), models.Index(fields=["business", "account"]), models.Index(fields=["business", "category"])]
