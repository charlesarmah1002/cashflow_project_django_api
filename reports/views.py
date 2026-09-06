from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Q, Sum
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from rest_framework.response import Response
from rest_framework.views import APIView
from transactions.models import Transaction
from accounts.models import Account

def parse_date(value, fallback):
    try: return date.fromisoformat(value) if value else fallback
    except ValueError: return fallback

def txs(user, start=None, end=None):
    qs = Transaction.objects.filter(business=user.business)
    return qs.filter(date__gte=start) if start and not end else qs.filter(date__range=(start, end)) if start and end else qs

def dec(v): return v or Decimal("0")

class DashboardSummaryView(APIView):
    def get(self, request):
        today = date.today(); start = today.replace(day=1); end = today
        all_tx = txs(request.user); month = txs(request.user, start, end)
        def total(qs, kind): return dec(qs.filter(type=kind).aggregate(total=Sum("amount"))["total"])
        balance = sum((a.opening_balance for a in Account.objects.filter(business=request.user.business)), Decimal("0")) + total(all_tx, "income") - total(all_tx, "expense")
        income, expense = total(month, "income"), total(month, "expense")
        return Response({"total_balance": balance, "income_this_month": income, "expense_this_month": expense, "net_cashflow": income-expense})

class CashflowView(APIView):
    def get(self, request):
        today = date.today(); start = parse_date(request.query_params.get("from"), today.replace(day=1)); end = parse_date(request.query_params.get("to"), today); group = request.query_params.get("group_by", "day")
        trunc = {"day": TruncDay, "week": TruncWeek, "month": TruncMonth}.get(group)
        if not trunc: return Response({"detail": "group_by must be day, week, or month."}, status=400)
        rows = txs(request.user, start, end).annotate(period=trunc("date")).values("period", "type").annotate(total=Sum("amount")).order_by("period")
        result = {}
        for row in rows:
            key = row["period"].date().isoformat() if hasattr(row["period"], "date") else row["period"].isoformat(); result.setdefault(key, {"period": key, "income": Decimal("0"), "expense": Decimal("0"), "net": Decimal("0")}); result[key][row["type"]] = row["total"]
        for row in result.values(): row["net"] = row["income"] - row["expense"]
        return Response({"from": start, "to": end, "group_by": group, "results": list(result.values())})

class ByCategoryView(APIView):
    def get(self, request):
        kind = request.query_params.get("type"); today = date.today(); start = parse_date(request.query_params.get("from"), today.replace(day=1)); end = parse_date(request.query_params.get("to"), today); qs = txs(request.user, start, end)
        if kind in ("income", "expense"): qs = qs.filter(type=kind)
        rows = qs.values("category_id", "category__name").annotate(total=Sum("amount")).order_by("-total")
        return Response({"type": kind, "from": start, "to": end, "results": [{"category_id": r["category_id"], "category_name": r["category__name"], "total": r["total"]} for r in rows]})

class ByAccountView(APIView):
    def get(self, request):
        result = []
        for a in Account.objects.filter(business=request.user.business, is_active=True):
            income = dec(a.transactions.filter(type="income").aggregate(x=Sum("amount"))["x"]); expense = dec(a.transactions.filter(type="expense").aggregate(x=Sum("amount"))["x"]); result.append({"account_id": a.id, "account_name": a.name, "account_type": a.type, "current_balance": a.opening_balance + income - expense})
        return Response({"results": result})
