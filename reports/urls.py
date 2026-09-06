from django.urls import path
from .views import ByAccountView, ByCategoryView, CashflowView, DashboardSummaryView
urlpatterns = [path("dashboard/summary/", DashboardSummaryView.as_view()), path("reports/cashflow/", CashflowView.as_view()), path("reports/by-category/", ByCategoryView.as_view()), path("reports/by-account/", ByAccountView.as_view())]
