import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/axiosInstance";
import "./CustomerDashboard.css";


export default function CustomerDashboard() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/chat/my-conversations/")
      .then(({ data }) => setConversations(data.results || data))
      .catch(() => setError("Failed to load conversations."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="loading-page">
        <div className="spinner" />
      </div>
    );
  }

  if (error) {
    return <p className="form-error">{error}</p>;
  }

  return (
    <div className="customer-dashboard animate-fade">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">My Chats</h1>
          <p className="dashboard-greeting">Your assigned lead conversations</p>
        </div>
      </div>

      {conversations.length === 0 ? (
        <div className="card" style={{ padding: 24 }}>
          <p className="brand-copy" style={{ margin: 0 }}>
            No conversations yet.
          </p>
        </div>
      ) : (
        <div className="conversation-list">
          {conversations.map((conversation) => (
            <Link
              key={conversation.id}
              to={`/my-chats/${conversation.id}`}
              className="card conversation-card"
            >
              <div className="list-row">
                <div>
                  <h3 style={{ margin: "0 0 6px" }}>{conversation.lead_name}</h3>
                  <div className="brand-copy" style={{ margin: 0 }}>
                    Handled by: {conversation.agent_name}
                  </div>
                </div>
                {conversation.unread_count > 0 && (
                  <span className="unread-pill">{conversation.unread_count}</span>
                )}
              </div>

              <p className="brand-copy" style={{ marginTop: 12 }}>
                {conversation.last_message?.content?.slice(0, 60) || "No messages yet."}
              </p>

              <div className="mono">
                {conversation.last_message?.created_at
                  ? new Date(conversation.last_message.created_at).toLocaleString()
                  : "No activity yet"}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
