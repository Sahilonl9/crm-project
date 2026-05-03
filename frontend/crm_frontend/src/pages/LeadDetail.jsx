import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import api from "../api/axiosInstance";
import LeadForm from "../components/LeadForm";
import NoteList from "../components/NoteList";
import ChatWindow from "../components/ChatWindow";
import "./LeadDetail.css";


const STATUS_COLORS = {
  new: "#5c9be8",
  contacted: "#9b72e8",
  interested: "#e8a32a",
  closed: "#e85c5c",
};

function currency(val) {
  const n = parseFloat(val) || 0;
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `$${(n / 1_000).toFixed(1)}K`;
  return `$${n.toLocaleString()}`;
}

function InfoRow({ label, value, mono }) {
  if (!value) return null;
  return (
    <div className="info-row">
      <span className="info-label">{label}</span>
      <span className={`info-value${mono ? " info-value--mono" : ""}`}>{value}</span>
    </div>
  );
}

const TABS = ["overview", "edit", "notes", "chat"];

export default function LeadDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [lead, setLead] = useState(null);
  const [conversation, setConversation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("overview");
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get(`/leads/${id}/`),
      api.get(`/chat/${id}/`),
    ])
      .then(([leadRes, conversationRes]) => {
        setLead(leadRes.data);
        setConversation(conversationRes.data);
      })
      .catch(() => navigate("/leads"))
      .finally(() => setLoading(false));
  }, [id, navigate]);

  const handleUpdated = (updated) => {
    setLead(updated);
    setTab("overview");
  };

  const handleDelete = async () => {
    if (!window.confirm(`Delete "${lead.name}"? This cannot be undone.`)) return;
    setDeleting(true);
    try {
      await api.delete(`/leads/${id}/`);
      navigate("/leads");
    } catch (_) {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-page">
        <div className="spinner" />
      </div>
    );
  }

  if (!lead) return null;

  const statusColor = STATUS_COLORS[lead.status] || "var(--text-muted)";

  return (
    <div className="lead-detail animate-fade">
      <div className="detail-breadcrumb">
        <Link to="/leads" className="detail-breadcrumb-link">Leads</Link>
        <span className="detail-breadcrumb-sep">›</span>
        <span className="detail-breadcrumb-current">{lead.name}</span>
      </div>

      <div className="detail-hero">
        <div className="detail-hero-left">
          <div className="detail-avatar">{lead.name[0]?.toUpperCase()}</div>
          <div className="detail-hero-info">
            <h1 className="detail-name">{lead.name}</h1>
            {lead.company && <p className="detail-company">{lead.company}</p>}
            <div className="detail-badges">
              <span
                className="detail-status-badge"
                style={{
                  color: statusColor,
                  borderColor: statusColor,
                  background: `${statusColor}14`,
                }}
              >
                <span
                  style={{
                    width: 6,
                    height: 6,
                    borderRadius: "50%",
                    background: statusColor,
                    display: "inline-block",
                  }}
                />
                {lead.status_display}
              </span>
              <span className="detail-source-badge">{lead.source_display}</span>
            </div>
          </div>
        </div>

        <div className="detail-hero-right">
          <div className="detail-value-display">
            <span className="detail-value-label">Deal Value</span>
            <span className="detail-value-amount">{currency(lead.value)}</span>
          </div>
          <button
            className="btn btn-danger btn-sm"
            onClick={handleDelete}
            disabled={deleting}
          >
            {deleting ? "Deleting..." : "Delete Lead"}
          </button>
        </div>
      </div>

      <div className="detail-tabs">
        {TABS.map((t) => (
          <button
            key={t}
            className={`detail-tab${tab === t ? " detail-tab--active" : ""}`}
            onClick={() => setTab(t)}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      <div className="detail-content">
        {tab === "overview" && (
          <div className="detail-overview animate-fade">
            <div className="card detail-info-card">
              <h2 className="detail-section-title">Contact Information</h2>
              <div className="info-rows">
                <InfoRow label="Name" value={lead.name} />
                <InfoRow label="Email" value={lead.email} mono />
                <InfoRow label="Phone" value={lead.phone} mono />
                <InfoRow label="Company" value={lead.company} />
                <InfoRow label="Source" value={lead.source_display} />
                <InfoRow label="Follow-up" value={lead.follow_up_date} mono />
                <InfoRow
                  label="Customer"
                  value={lead.customer ? (lead.customer.full_name || lead.customer.email) : "Unassigned"}
                />
                <InfoRow
                  label="Created"
                  value={new Date(lead.created_at).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                />
              </div>

              {lead.description && (
                <div className="detail-description">
                  <span className="info-label">Description</span>
                  <p className="detail-desc-text">{lead.description}</p>
                </div>
              )}

              <button
                className="btn btn-secondary btn-sm detail-edit-btn"
                onClick={() => setTab("edit")}
              >
                Edit Lead
              </button>
            </div>

            <div className="detail-quick-stats">
              <div className="card quick-stat">
                <span className="quick-stat-label">Total Notes</span>
                <span className="quick-stat-value">{lead.notes?.length ?? 0}</span>
              </div>
              <div className="card quick-stat">
                <span className="quick-stat-label">Pipeline Stage</span>
                <span className="quick-stat-value" style={{ color: statusColor, fontSize: 15 }}>
                  {lead.status_display}
                </span>
              </div>
              <div
                className="card quick-stat"
                style={{ cursor: "pointer" }}
                onClick={() => setTab("notes")}
              >
                <span className="quick-stat-label">Latest Note</span>
                <span
                  className="quick-stat-value"
                  style={{
                    fontSize: 13,
                    fontFamily: "var(--font-body)",
                    fontWeight: 400,
                    color: "var(--text-muted)",
                  }}
                >
                  {lead.notes?.[0]?.content?.slice(0, 60) || "No notes yet"}
                  {lead.notes?.[0]?.content?.length > 60 ? "..." : ""}
                </span>
              </div>
            </div>
          </div>
        )}

        {tab === "edit" && (
          <div className="card animate-fade">
            <LeadForm
              lead={lead}
              onSuccess={handleUpdated}
              onCancel={() => setTab("overview")}
            />
          </div>
        )}

        {tab === "notes" && (
          <div className="card animate-fade">
            <NoteList leadId={id} />
          </div>
        )}

        {tab === "chat" && conversation && (
          <div className="animate-fade">
            <ChatWindow
              conversationId={conversation.id}
              historyUrl={`/chat/${id}/messages/`}
              postUrl={`/chat/${id}/messages/`}
              markReadUrl={`/chat/${id}/mark-read/`}
            />
          </div>
        )}
      </div>
    </div>
  );
}
