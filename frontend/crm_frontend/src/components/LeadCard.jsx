import { Link } from "react-router-dom";
import "./LeadCard.css";

const STATUS_COLORS = {
  new: { bg: "rgba(92,155,232,0.12)", color: "#5c9be8", dot: "#5c9be8" },
  contacted: { bg: "rgba(155,114,232,0.12)", color: "#9b72e8", dot: "#9b72e8" },
  interested: { bg: "rgba(232,163,42,0.12)", color: "#e8a32a", dot: "#e8a32a" },
  closed: { bg: "rgba(232,92,92,0.12)", color: "#e85c5c", dot: "#e85c5c" },
};

function StatusBadge({ status, label }) {
  const s = STATUS_COLORS[status] || STATUS_COLORS.new;
  return (
    <span className="lead-card-status" style={{ background: s.bg, color: s.color }}>
      <span
        style={{
          width: 6,
          height: 6,
          borderRadius: "50%",
          background: s.dot,
          display: "inline-block",
          flexShrink: 0,
        }}
      />
      {label}
    </span>
  );
}

function formatCurrency(val) {
  const n = parseFloat(val) || 0;
  if (n >= 1000000) return `$${(n / 1000000).toFixed(1)}M`;
  if (n >= 1000) return `$${(n / 1000).toFixed(1)}K`;
  return `$${n.toLocaleString()}`;
}

export default function LeadCard({ lead, onDelete }) {
  const followUp = lead.follow_up_date ? new Date(lead.follow_up_date) : null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const isPastDue = followUp && followUp < today;

  return (
    <div className="lead-card animate-fade">
      <div className="lead-card-header">
        <div className="lead-card-identity">
          <div className="lead-card-avatar">
            {lead.name[0]?.toUpperCase()}
          </div>
          <div>
            <Link to={`/leads/${lead.id}`} className="lead-card-name">
              {lead.name}
            </Link>
            {lead.company && <p className="lead-card-company">{lead.company}</p>}
          </div>
        </div>
        <StatusBadge status={lead.status} label={lead.status_display} />
      </div>

      <div className="lead-card-meta">
        {lead.email && (
          <span className="lead-card-meta-item">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <rect x="1" y="2.5" width="10" height="7" rx="1" stroke="currentColor" strokeWidth="1.2" />
              <path d="M1 4l5 3 5-3" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
            </svg>
            {lead.email}
          </span>
        )}
        {lead.phone && (
          <span className="lead-card-meta-item">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path
                d="M2 2h2.5l1 2.5-1.5 1a7 7 0 003.5 3.5l1-1.5L11 8.5V11A9 9 0 012 2z"
                stroke="currentColor"
                strokeWidth="1.2"
                strokeLinejoin="round"
              />
            </svg>
            {lead.phone}
          </span>
        )}
        {lead.customer && (
          <span className="lead-card-meta-item">
            Customer: {lead.customer.full_name || lead.customer.email}
          </span>
        )}
      </div>

      <div className="lead-card-footer">
        <span className="lead-card-value">{formatCurrency(lead.value)}</span>

        {followUp && (
          <span className={`lead-card-followup${isPastDue ? " lead-card-followup--overdue" : ""}`}>
            <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
              <circle cx="5.5" cy="5.5" r="4.5" stroke="currentColor" strokeWidth="1.2" />
              <path d="M5.5 3v2.5l1.5 1" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
            </svg>
            {isPastDue ? "Overdue · " : ""}
            {followUp.toLocaleDateString("en-US", { month: "short", day: "numeric" })}
          </span>
        )}

        <div className="lead-card-actions">
          <Link to={`/leads/${lead.id}`} className="btn btn-ghost btn-sm">View</Link>
          {onDelete && (
            <button
              className="btn btn-ghost btn-sm"
              style={{ color: "var(--red)" }}
              onClick={() => onDelete(lead.id)}
            >
              Del
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
