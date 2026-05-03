import { useEffect, useRef, useState } from "react";
import api from "../api/axiosInstance";
import { useAuth } from "../context/AuthContext";
import "./ChatWindow.css";

const WS_BASE =
  import.meta.env.VITE_WS_BASE_URL ||
  (window.location.protocol === "https:" ? "wss://localhost:8000" : "ws://localhost:8000");

function sortMessages(list) {
  return [...list].sort(
    (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
  );
}

function mergeMessages(current, incoming) {
  const map = new Map();
  [...current, ...incoming].forEach((msg) => {
    map.set(msg.id, msg);
  });
  return sortMessages([...map.values()]);
}

export default function ChatWindow({ conversationId, historyUrl, postUrl, markReadUrl }) {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [content, setContent] = useState("");
  const [typing, setTyping] = useState(false);
  const [loading, setLoading] = useState(true);

  const socketRef = useRef(null);
  const scrollRef = useRef(null);

  const loadMessages = async (silent = false) => {
    try {
      const { data } = await api.get(historyUrl);
      const history = data.results || data || [];
      setMessages((current) => mergeMessages(current, history));
    } catch (error) {
      if (!silent) {
        console.error("Failed to load messages:", error);
      }
    } finally {
      if (!silent) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    if (!historyUrl) return;
    loadMessages();
  }, [historyUrl]);

  useEffect(() => {
    if (!conversationId) return;

    const token = localStorage.getItem("access_token");
    const socket = new WebSocket(`${WS_BASE}/ws/chat/${conversationId}/?token=${token}`);
    socketRef.current = socket;

    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data);

      if (payload.type === "message" && payload.message) {
        setMessages((current) => mergeMessages(current, [payload.message]));
      }

      if (payload.type === "typing") {
        setTyping(true);
        window.clearTimeout(window.__smartcrmTypingTimer);
        window.__smartcrmTypingTimer = window.setTimeout(() => setTyping(false), 1200);
      }

      if (payload.type === "mark_read") {
        setMessages((current) =>
          current.map((message) =>
            message.sender?.id === user?.id ? { ...message, is_read: true } : message
          )
        );
      }
    };

    return () => socket.close();
  }, [conversationId, user?.id]);

  // Fallback auto-refresh every 2 seconds
  useEffect(() => {
    if (!historyUrl) return;

    const interval = window.setInterval(() => {
      loadMessages(true);
    }, 2000);

    return () => window.clearInterval(interval);
  }, [historyUrl]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  useEffect(() => {
    if (markReadUrl && messages.length > 0) {
      api.post(markReadUrl).catch(() => {});
    }
  }, [markReadUrl, messages.length]);

  const handleTyping = (value) => {
    setContent(value);
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: "typing" }));
    }
  };

  const handleSend = async () => {
    if (!content.trim()) return;

    const draft = content.trim();
    setContent("");

    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: "message", content: draft }));
      return;
    }

    try {
      const { data } = await api.post(postUrl, { content: draft });
      setMessages((current) => mergeMessages(current, [data]));
    } catch (error) {
      console.error("Failed to send message:", error);
    }
  };

  return (
    <section className="card chat-panel">
      <div className="chat-messages">
        {loading ? (
          <div className="chat-loading"><div className="spinner" /></div>
        ) : messages.length === 0 ? (
          <div className="chat-empty">No messages yet.</div>
        ) : (
          messages.map((message) => {
            const own = message.sender?.id === user?.id;
            return (
              <div key={message.id} className={`message-bubble ${own ? "own" : ""}`}>
                <div className="message-meta">
                  <span>{message.sender_name}</span>
                  <span>{new Date(message.created_at).toLocaleString()}</span>
                </div>
                <div>{message.content}</div>
              </div>
            );
          })
        )}

        {typing && <div className="brand-copy">Someone is typing...</div>}
        <div ref={scrollRef} />
      </div>

      <div className="chat-compose">
        <textarea
          className="form-textarea"
          value={content}
          onChange={(e) => handleTyping(e.target.value)}
          placeholder="Type your message..."
        />
        <div className="toolbar">
          <button className="btn btn-primary" onClick={handleSend}>
            Send Message
          </button>
        </div>
      </div>
    </section>
  );
}
