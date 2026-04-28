from rest_framework import serializers

from users.serializers import UserSerializer
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "id",
            "conversation",
            "sender",
            "sender_type",
            "sender_name",
            "display_name",
            "content",
            "is_read",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "conversation",
            "sender",
            "sender_type",
            "sender_name",
            "display_name",
            "is_read",
            "created_at",
            "updated_at",
        )

    def get_display_name(self, obj):
        return obj.get_display_name()


class ConversationSerializer(serializers.ModelSerializer):
    lead_id = serializers.UUIDField(source="lead.id", read_only=True)
    lead_name = serializers.CharField(source="lead.name", read_only=True)
    lead_email = serializers.CharField(source="lead.email", read_only=True)
    agent_name = serializers.CharField(source="lead.owner.full_name", read_only=True)
    customer = UserSerializer(source="lead.customer", read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = (
            "id",
            "lead_id",
            "lead_name",
            "lead_email",
            "agent_name",
            "customer",
            "last_message",
            "unread_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def get_last_message(self, obj):
        message = obj.messages.order_by("-created_at").first()
        return MessageSerializer(message).data if message else None

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0

        opposite_type = "customer" if request.user.role == "agent" else "agent"
        return obj.messages.filter(sender_type=opposite_type, is_read=False).count()


class CustomerConversationSerializer(serializers.ModelSerializer):
    lead_name = serializers.CharField(source="lead.name", read_only=True)
    lead_email = serializers.CharField(source="lead.email", read_only=True)
    agent_name = serializers.CharField(source="lead.owner.full_name", read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = (
            "id",
            "lead_name",
            "lead_email",
            "agent_name",
            "last_message",
            "unread_count",
            "created_at",
            "updated_at",
        )

    def get_last_message(self, obj):
        message = obj.messages.order_by("-created_at").first()
        return MessageSerializer(message).data if message else None

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0

        return obj.messages.filter(sender_type="agent", is_read=False).count()
