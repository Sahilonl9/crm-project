import json
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError

from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.group_name = f"chat_{self.conversation_id}"

        token = parse_qs(self.scope["query_string"].decode()).get("token", [None])[0]
        self.user = await self.get_user(token)

        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        has_access = await self.user_can_access()
        if not has_access:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        payload = json.loads(text_data or "{}")
        event_type = payload.get("type")

        if event_type == "message":
            message = await self.save_message(payload.get("content", ""))
            if not message:
                return

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat.message",
                    "message": message,
                },
            )

        elif event_type == "typing":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat.typing",
                    "user_id": str(self.user.id),
                    "sender_type": self.user.role,
                },
            )

        elif event_type == "mark_read":
            updated = await self.mark_read()
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat.read",
                    "updated": updated,
                    "sender_type": self.user.role,
                },
            )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "message",
                    "message": event["message"],
                }
            )
        )

    async def chat_typing(self, event):
        if event["user_id"] != str(self.user.id):
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "typing",
                        "sender_type": event["sender_type"],
                    }
                )
            )

    async def chat_read(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "mark_read",
                    "updated": event["updated"],
                    "sender_type": event["sender_type"],
                }
            )
        )

    @database_sync_to_async
    def get_user(self, token):
        if not token:
            return None

        try:
            validated = JWTAuthentication().get_validated_token(token)
            return JWTAuthentication().get_user(validated)
        except TokenError:
            return None

    @database_sync_to_async
    def user_can_access(self):
        try:
            conversation = Conversation.objects.select_related(
                "lead__owner",
                "lead__customer",
            ).get(id=self.conversation_id)
        except Conversation.DoesNotExist:
            return False

        if self.user.role == "agent":
            return conversation.lead.owner_id == self.user.id

        return conversation.lead.customer_id == self.user.id

    @database_sync_to_async
    def save_message(self, content):
        content = (content or "").strip()
        if not content:
            return None

        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            sender_type=self.user.role,
            sender_name=self.user.full_name or self.user.email,
            content=content,
        )
        conversation.save(update_fields=["updated_at"])

        return {
            "id": str(message.id),
            "conversation": str(conversation.id),
            "sender": {
                "id": str(self.user.id),
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "full_name": self.user.full_name,
                "role": self.user.role,
            },
            "sender_type": message.sender_type,
            "sender_name": message.sender_name,
            "content": message.content,
            "is_read": message.is_read,
            "created_at": message.created_at.isoformat(),
            "updated_at": message.updated_at.isoformat(),
        }

    @database_sync_to_async
    def mark_read(self):
        opposite = Message.SenderType.CUSTOMER if self.user.role == "agent" else Message.SenderType.AGENT
        return Message.objects.filter(
            conversation_id=self.conversation_id,
            sender_type=opposite,
            is_read=False,
        ).update(is_read=True)
