from django.shortcuts import get_object_or_404
from rest_framework import exceptions, generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from leads.models import Lead
from leads.permissions import IsOwner
from users.models import User
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    CustomerConversationSerializer,
    MessageSerializer,
)


class IsAgent(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.AGENT
        )


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.CUSTOMER
        )


class MessagePagination(PageNumberPagination):
    page_size = 30


def create_message(conversation, sender, content):
    content = (content or "").strip()
    if not content:
        raise exceptions.ValidationError({"content": "Message content is required."})

    return Message.objects.create(
        conversation=conversation,
        sender=sender,
        sender_type=sender.role,
        sender_name=sender.full_name or sender.email,
        content=content,
    )


class AgentConversationView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAgent)

    def get(self, request, lead_id):
        lead = get_object_or_404(Lead, pk=lead_id, owner=request.user)
        conversation, _ = Conversation.objects.get_or_create(lead=lead)
        serializer = ConversationSerializer(conversation, context={"request": request})
        return Response(serializer.data)


class AgentMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated, IsAgent)
    pagination_class = MessagePagination

    def get_conversation(self):
        lead = get_object_or_404(Lead, pk=self.kwargs["lead_id"], owner=self.request.user)
        conversation, _ = Conversation.objects.get_or_create(lead=lead)
        return conversation

    def get_queryset(self):
        return self.get_conversation().messages.select_related("sender").all()

    def create(self, request, *args, **kwargs):
        conversation = self.get_conversation()
        message = create_message(conversation, request.user, request.data.get("content", ""))
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AgentMarkReadView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAgent)

    def post(self, request, lead_id):
        lead = get_object_or_404(Lead, pk=lead_id, owner=request.user)
        conversation, _ = Conversation.objects.get_or_create(lead=lead)

        updated = conversation.messages.filter(
            is_read=False,
            sender_type=Message.SenderType.CUSTOMER,
        ).update(is_read=True)

        return Response({"updated": updated})


class CustomerConversationListView(generics.ListAPIView):
    serializer_class = CustomerConversationSerializer
    permission_classes = (permissions.IsAuthenticated, IsCustomer)

    def get_queryset(self):
        return (
            Conversation.objects.filter(lead__customer=self.request.user)
            .select_related("lead__owner", "lead__customer")
            .prefetch_related("messages")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class CustomerConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user

        if user.role == User.Role.AGENT:
            return Conversation.objects.filter(lead__owner=user).select_related(
                "lead__owner", "lead__customer", "lead"
            ).prefetch_related("messages")

        return Conversation.objects.filter(lead__customer=user).select_related(
            "lead__owner", "lead__customer", "lead"
        ).prefetch_related("messages")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class CustomerMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = MessagePagination

    def get_conversation(self):
        conversation = get_object_or_404(Conversation, pk=self.kwargs["conversation_id"])
        user = self.request.user

        if user.role == User.Role.CUSTOMER and conversation.lead.customer_id != user.id:
            raise exceptions.PermissionDenied("You do not have access to this conversation.")

        if user.role == User.Role.AGENT and conversation.lead.owner_id != user.id:
            raise exceptions.PermissionDenied("You do not have access to this conversation.")

        return conversation

    def get_queryset(self):
        return self.get_conversation().messages.select_related("sender").all()

    def create(self, request, *args, **kwargs):
        conversation = self.get_conversation()
        message = create_message(conversation, request.user, request.data.get("content", ""))
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CustomerMarkReadView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, pk=conversation_id)
        user = request.user

        if user.role == User.Role.CUSTOMER and conversation.lead.customer_id != user.id:
            raise exceptions.PermissionDenied("You do not have access to this conversation.")

        if user.role == User.Role.AGENT and conversation.lead.owner_id != user.id:
            raise exceptions.PermissionDenied("You do not have access to this conversation.")

        opposite_type = (
            Message.SenderType.AGENT
            if user.role == User.Role.CUSTOMER
            else Message.SenderType.CUSTOMER
        )

        updated = conversation.messages.filter(
            is_read=False,
            sender_type=opposite_type,
        ).update(is_read=True)

        return Response({"updated": updated})
