from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from .models import Lead, Note
from .permissions import IsOwner
from .serializers import (
    DashboardSerializer,
    LeadListSerializer,
    LeadSerializer,
    NoteSerializer,
)


class IsAgent(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.AGENT
        )


class LeadViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, IsAgent, IsOwner)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", "email", "phone", "company")
    ordering_fields = ("created_at", "updated_at", "name", "value", "follow_up_date")
    ordering = ("-created_at",)

    def get_queryset(self):
        queryset = (
            Lead.objects.filter(owner=self.request.user)
            .select_related("owner", "customer")
            .prefetch_related("notes__author")
        )

        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        source_param = self.request.query_params.get("source")
        if source_param:
            queryset = queryset.filter(source=source_param)

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
                | Q(company__icontains=search)
            )

        follow_up_from = self.request.query_params.get("follow_up_from")
        follow_up_to = self.request.query_params.get("follow_up_to")

        if follow_up_from:
            queryset = queryset.filter(follow_up_date__gte=follow_up_from)

        if follow_up_to:
            queryset = queryset.filter(follow_up_date__lte=follow_up_to)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return LeadListSerializer
        return LeadSerializer

    def get_permissions(self):
        if self.action in ["list", "create"]:
            return [permissions.IsAuthenticated(), IsAgent()]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = (permissions.IsAuthenticated, IsAgent, IsOwner)

    def get_queryset(self):
        return (
            Note.objects.filter(
                lead_id=self.kwargs["lead_pk"],
                lead__owner=self.request.user,
            )
            .select_related("author", "lead")
        )

    def perform_create(self, serializer):
        lead = get_object_or_404(
            Lead,
            pk=self.kwargs["lead_pk"],
            owner=self.request.user,
        )
        serializer.save(author=self.request.user, lead=lead)


class DashboardView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAgent)

    def get(self, request):
        queryset = Lead.objects.filter(owner=request.user)
        serializer = DashboardSerializer(DashboardSerializer.build(queryset))
        return Response(serializer.data)
