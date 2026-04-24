from django.shortcuts import render

# Create your views here.
from datetime import date
from django.db.models import Count, Sum, Q
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lead, Note
from .serializers import LeadSerializer, LeadListSerializer, NoteSerializer, DashboardSerializer
from .permissions import IsOwner


class LeadViewSet(viewsets.ModelViewSet):
    """
    GET    /api/leads/           → list (owner's leads)
    POST   /api/leads/           → create
    GET    /api/leads/<id>/      → retrieve
    PUT    /api/leads/<id>/      → update
    PATCH  /api/leads/<id>/      → partial update
    DELETE /api/leads/<id>/      → destroy
    """
    permission_classes = (IsAuthenticated, IsOwner)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name', 'email', 'phone', 'company')
    ordering_fields = ('created_at', 'updated_at', 'name', 'value', 'follow_up_date')
    ordering = ('-created_at',)

    def get_queryset(self):
        qs = Lead.objects.filter(owner=self.request.user).prefetch_related('notes__author')

        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        # Filter by source
        source_param = self.request.query_params.get('source')
        if source_param:
            qs = qs.filter(source=source_param)

        # Filter by follow_up_date range
        follow_up_from = self.request.query_params.get('follow_up_from')
        follow_up_to = self.request.query_params.get('follow_up_to')
        if follow_up_from:
            qs = qs.filter(follow_up_date__gte=follow_up_from)
        if follow_up_to:
            qs = qs.filter(follow_up_date__lte=follow_up_to)

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return LeadListSerializer
        return LeadSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class NoteViewSet(viewsets.ModelViewSet):
    """
    GET    /api/leads/<lead_id>/notes/       → list notes for lead
    POST   /api/leads/<lead_id>/notes/       → create note
    GET    /api/leads/<lead_id>/notes/<id>/  → retrieve
    PUT    /api/leads/<lead_id>/notes/<id>/  → update
    PATCH  /api/leads/<lead_id>/notes/<id>/  → partial update
    DELETE /api/leads/<lead_id>/notes/<id>/  → destroy
    """
    serializer_class = NoteSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    def get_queryset(self):
        return Note.objects.filter(
            lead_id=self.kwargs['lead_pk'],
            lead__owner=self.request.user
        ).select_related('author')

    def perform_create(self, serializer):
        lead = Lead.objects.get(pk=self.kwargs['lead_pk'], owner=self.request.user)
        serializer.save(author=self.request.user, lead=lead)


class DashboardView(APIView):
    """GET /api/leads/dashboard/"""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        leads = Lead.objects.filter(owner=request.user)
        total = leads.count()

        # Count per status
        status_counts = {item['status']: item['count']
                         for item in leads.values('status').annotate(count=Count('id'))}

        won_count = status_counts.get('won', 0)
        conversion_rate = round((won_count / total * 100), 2) if total else 0.0

        total_value = leads.aggregate(t=Sum('value'))['t'] or 0
        won_value = leads.filter(status='won').aggregate(t=Sum('value'))['t'] or 0

        follow_ups_today = leads.filter(follow_up_date=date.today()).count()

        recent_leads = leads.order_by('-created_at')[:5]

        data = {
            'total_leads': total,
            'by_status': status_counts,
            'conversion_rate': conversion_rate,
            'total_value': total_value,
            'won_value': won_value,
            'follow_ups_today': follow_ups_today,
            'recent_leads': recent_leads,
        }
        serializer = DashboardSerializer(data)
        return Response(serializer.data)