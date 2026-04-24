from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from leads.models import Lead
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationView(APIView):
    """
    GET  /api/chat/<lead_id>/   → get or create conversation for lead
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, lead_id):
        lead = generics.get_object_or_404(Lead, pk=lead_id, owner=request.user)
        conversation, _ = Conversation.objects.get_or_create(lead=lead)
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)


class MessageListView(generics.ListCreateAPIView):
    """
    GET  /api/chat/<lead_id>/messages/   → list messages
    POST /api/chat/<lead_id>/messages/   → send message
    """
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def _get_conversation(self):
        lead = generics.get_object_or_404(
            Lead, pk=self.kwargs['lead_id'], owner=self.request.user
        )
        conversation, _ = Conversation.objects.get_or_create(lead=lead)
        return conversation

    def get_queryset(self):
        return self._get_conversation().messages.select_related('sender').all()

    def perform_create(self, serializer):
        conversation = self._get_conversation()
        msg = serializer.save(sender=self.request.user, conversation=conversation)
        # Update conversation timestamp
        conversation.save(update_fields=['updated_at'])
        # Broadcast via channel layer (best-effort)
        self._broadcast(conversation, msg)

    def _broadcast(self, conversation, message):
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            import json

            channel_layer = get_channel_layer()
            group_name = f'chat_{conversation.lead_id}'
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'chat_message',
                    'message': MessageSerializer(message).data,
                }
            )
        except Exception:
            pass  # Don't fail HTTP request if WS broadcast fails


class MarkReadView(APIView):
    """
    POST /api/chat/<lead_id>/mark-read/  → mark all unread messages as read
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, lead_id):
        lead = generics.get_object_or_404(Lead, pk=lead_id, owner=request.user)
        try:
            conversation = Conversation.objects.get(lead=lead)
        except Conversation.DoesNotExist:
            return Response({'detail': 'No conversation found.'}, status=status.HTTP_404_NOT_FOUND)

        updated = conversation.messages.filter(is_read=False).exclude(
            sender=request.user
        ).update(is_read=True)

        return Response({'marked_read': updated})