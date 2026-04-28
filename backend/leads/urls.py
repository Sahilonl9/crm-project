from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import DashboardView, LeadViewSet, NoteViewSet

router = DefaultRouter()
router.register(r"", LeadViewSet, basename="lead")

leads_router = NestedDefaultRouter(router, r"", lookup="lead")
leads_router.register(r"notes", NoteViewSet, basename="lead-notes")

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="leads-dashboard"),
    path("", include(router.urls)),
    path("", include(leads_router.urls)),
]
