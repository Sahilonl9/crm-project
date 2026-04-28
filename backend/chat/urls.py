from django.urls import path

from .views import (
    AgentConversationView,
    AgentMarkReadView,
    AgentMessageListCreateView,
    CustomerConversationDetailView,
    CustomerConversationListView,
    CustomerMarkReadView,
    CustomerMessageListCreateView,
)

urlpatterns = [
    path("my-conversations/", CustomerConversationListView.as_view(), name="my-conversations"),
    path("conversation/<uuid:pk>/", CustomerConversationDetailView.as_view(), name="conversation-detail"),
    path("conversation/<uuid:conversation_id>/messages/", CustomerMessageListCreateView.as_view(), name="conversation-messages"),
    path("conversation/<uuid:conversation_id>/mark-read/", CustomerMarkReadView.as_view(), name="conversation-mark-read"),
    path("<uuid:lead_id>/", AgentConversationView.as_view(), name="agent-conversation"),
    path("<uuid:lead_id>/messages/", AgentMessageListCreateView.as_view(), name="agent-messages"),
    path("<uuid:lead_id>/mark-read/", AgentMarkReadView.as_view(), name="agent-mark-read"),
]
