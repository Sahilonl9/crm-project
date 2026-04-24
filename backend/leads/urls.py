from django.urls import path, include
from rest_framework_nested import routers
from .views import LeadViewSet, NoteViewSet, DashboardView

# Primary router
router = routers.DefaultRouter()
router.register(r'', LeadViewSet, basename='lead')

# Nested router: /api/leads/<lead_pk>/notes/
leads_router = routers.NestedDefaultRouter(router, r'', lookup='lead')
leads_router.register(r'notes', NoteViewSet, basename='lead-notes')

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='leads-dashboard'),
    path('', include(router.urls)),
    path('', include(leads_router.urls)),
]