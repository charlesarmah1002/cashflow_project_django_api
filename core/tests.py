from datetime import date
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import Account
from transactions.models import Category, Transaction
from .models import Business, User

class CashflowAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="owner@example.com", password="strong-password", name="Owner", business=Business.objects.create(name="Owner Business"))
        self.other = User.objects.create_user(email="other@example.com", password="strong-password", name="Other", business=Business.objects.create(name="Other Business"))
        self.account = Account.objects.create(business=self.user.business, name="Cash", type="cash", opening_balance=Decimal("100.00"))
        self.income_category = Category.objects.create(business=self.user.business, name="Sales", type="income")
        self.expense_category = Category.objects.create(business=self.user.business, name="Rent", type="expense")
        self.client.force_authenticate(self.user)

    def test_register_returns_tokens_and_creates_business(self):
        response = self.client.post("/api/auth/register/", {"business_name": "New Co", "name": "New Owner", "email": "new@example.com", "password": "strong-password"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["user"]["business"]["name"], "New Co")

    def test_login_uses_email(self):
        self.client.force_authenticate(user=None)
        response = self.client.post("/api/auth/login/", {"email": "owner@example.com", "password": "strong-password"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_password_change_updates_password(self):
        response = self.client.post("/api/auth/password/change/", {"current_password": "strong-password", "new_password": "new-strong-password"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new-strong-password"))

    def test_password_change_rejects_incorrect_current_password(self):
        response = self.client.post("/api/auth/password/change/", {"current_password": "wrong-password", "new_password": "new-strong-password"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("strong-password"))

    def test_transaction_creation_and_balance(self):
        response = self.client.post("/api/transactions/", {"account": self.account.id, "category": self.income_category.id, "type": "income", "amount": "50.00", "date": str(date.today())}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(f"/api/accounts/{self.account.id}/")
        self.assertEqual(response.data["current_balance"], Decimal("150.00"))

    def test_mismatched_category_type_is_rejected(self):
        response = self.client.post("/api/transactions/", {"account": self.account.id, "category": self.expense_category.id, "type": "income", "amount": "10.00", "date": str(date.today())}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_business_isolation(self):
        other_account = Account.objects.create(business=self.other.business, name="Other Cash", type="cash")
        response = self.client.get(f"/api/accounts/{other_account.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.post("/api/transactions/", {"account": other_account.id, "category": self.income_category.id, "type": "income", "amount": "10.00", "date": str(date.today())}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_account_delete_is_soft_delete(self):
        response = self.client.delete(f"/api/accounts/{self.account.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.account.refresh_from_db()
        self.assertFalse(self.account.is_active)
        self.assertEqual(self.client.get("/api/accounts/").data["count"], 0)

    def test_dashboard_summary(self):
        Transaction.objects.create(business=self.user.business, account=self.account, category=self.income_category, type="income", amount=Decimal("50.00"), date=date.today())
        Transaction.objects.create(business=self.user.business, account=self.account, category=self.expense_category, type="expense", amount=Decimal("20.00"), date=date.today())
        response = self.client.get("/api/dashboard/summary/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_balance"], Decimal("130.00"))
        self.assertEqual(response.data["net_cashflow"], Decimal("30.00"))
