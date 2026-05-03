import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/axiosInstance";
import ChatWindow from "../components/ChatWindow";
import "./CustomerChatRoom.css";

export default function CustomerChatRoom() {
  const { id } = useParams();
  const [conversation, setConversation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/chat/conversation/${id}/`)
      .then(({ data }) => setConversation(data))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="loading-page">
        <div className="spinner" />
      </div>
    );
  }

  if (!conversation) {
    return <p className="form-error">Conversation not found.</p>;
  }

  return (
    <div className="stack animate-fade">
      <section className="card section-panel">
        <div className="brand-kicker">Conversation</div>
        <h1 className="brand-title" style={{ fontSize: "2.5rem" }}>
          {conversation.lead_name}
        </h1>
        <p className="brand-copy">Handled by {conversation.agent_name}</p>
      </section>

      <ChatWindow
        conversationId={id}
        historyUrl={`/chat/conversation/${id}/messages/`}
        postUrl={`/chat/conversation/${id}/messages/`}
        markReadUrl={`/chat/conversation/${id}/mark-read/`}
      />
    </div>
  );
}
