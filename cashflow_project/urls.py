from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

def health_check(request):
	return JsonResponse({"status": "ok"})

urlpatterns = [path("health/", health_check), path("admin/", admin.site.urls), path("api/", include("core.urls")), path("api/", include("accounts.urls")), path("api/", include("transactions.urls")), path("api/", include("reports.urls"))]
