import uuid

from django.conf import settings
from django.db import models

from leads.models import Lead


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.OneToOneField(
        Lead,
        on_delete=models.CASCADE,
        related_name="conversation",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "chat_conversations"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation: {self.lead.name}"

    @property
    def unread_count(self):
        return self.messages.filter(is_read=False).count()


class Message(models.Model):
    SENDER_CHOICES = [
        ("agent", "Agent"),
        ("customer", "Customer"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    sender_type = models.CharField(max_length=10, choices=SENDER_CHOICES)
    sender_name = models.CharField(max_length=255)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "chat_messages"
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.sender_type}] {self.conversation}"

    def get_display_name(self):
        return self.sender_name
