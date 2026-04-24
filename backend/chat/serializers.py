from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_id = serializers.UUIDField(source='sender.id', read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'conversation', 'sender', 'sender_id', 'sender_name',
                  'content', 'is_read', 'created_at')
        read_only_fields = ('id', 'sender', 'sender_id', 'sender_name', 'is_read', 'created_at')

    def get_sender_name(self, obj):
        return obj.sender.full_name if obj.sender else 'Unknown'


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    unread_count = serializers.IntegerField(read_only=True)
    lead_name = serializers.CharField(source='lead.name', read_only=True)

    class Meta:
        model = Conversation
        fields = ('id', 'lead', 'lead_name', 'unread_count', 'messages', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')