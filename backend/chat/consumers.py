import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        self.lead_id = self.scope['url_route']['kwargs']['lead_id']
        self.group_name = f'chat_{self.lead_id}'

        # Reject unauthenticated connections
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        # Verify the user owns this lead
        if not await self._user_owns_lead():
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'error': 'Invalid JSON'}))
            return

        msg_type = data.get('type', 'message')

        if msg_type == 'message':
            content = data.get('content', '').strip()
            if not content:
                return

            message = await self._save_message(content)
            if message is None:
                await self.send(text_data=json.dumps({'error': 'Could not save message'}))
                return

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                }
            )

        elif msg_type == 'typing':
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'typing_indicator',
                    'user_id': str(self.user.id),
                    'user_name': self.user.full_name,
                    'is_typing': data.get('is_typing', False),
                }
            )

    # ── Group message handlers ────────────────────────────────────────────────

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
        }))

    async def typing_indicator(self, event):
        # Don't echo typing indicator back to sender
        if str(self.user.id) != event.get('user_id'):
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'user_name': event['user_name'],
                'is_typing': event['is_typing'],
            }))

    # ── DB helpers ────────────────────────────────────────────────────────────

    @database_sync_to_async
    def _user_owns_lead(self):
        from leads.models import Lead
        return Lead.objects.filter(pk=self.lead_id, owner=self.user).exists()

    @database_sync_to_async
    def _save_message(self, content):
        from leads.models import Lead
        from chat.models import Conversation, Message

        try:
            lead = Lead.objects.get(pk=self.lead_id, owner=self.user)
            conversation, _ = Conversation.objects.get_or_create(lead=lead)
            message = Message.objects.create(
                conversation=conversation,
                sender=self.user,
                content=content,
            )
            # Update conversation timestamp
            Conversation.objects.filter(pk=conversation.pk).update(updated_at=timezone.now())

            return {
                'id': str(message.id),
                'conversation': str(conversation.id),
                'sender': str(self.user.id),
                'sender_id': str(self.user.id),
                'sender_name': self.user.full_name,
                'content': message.content,
                'is_read': message.is_read,
                'created_at': message.created_at.isoformat(),
            }
        except Exception:
            return None