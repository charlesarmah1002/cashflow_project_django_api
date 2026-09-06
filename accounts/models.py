from django.db import models
from core.models import Business

class Account(models.Model):
    class AccountType(models.TextChoices): CASH="cash", "Cash"; BANK="bank", "Bank"; MOBILE_MONEY="mobile_money", "Mobile money"; OTHER="other", "Other"
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="accounts")
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=AccountType.choices)
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: indexes = [models.Index(fields=["business", "is_active"])]
    def __str__(self): return self.name
