import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../api/axiosInstance";
import "./Dashboard.css";



function StatCard({ label, value, sub, accent, delay = 0 }) {
  return (
    <div className="stat-card animate-fade" style={{ animationDelay: `${delay}ms` }}>
      <span className="stat-label">{label}</span>
      <span className="stat-value" style={accent ? { color: accent } : {}}>
        {value}
      </span>
      {sub && <span className="stat-sub">{sub}</span>}
    </div>
  );
}

const STATUS_META = {
  new: { label: "New", color: "#5c9be8" },
  contacted: { label: "Contacted", color: "#9b72e8" },
  interested: { label: "Interested", color: "#e8a32a" },
  closed: { label: "Closed", color: "#e85c5c" },
};

function currency(val) {
  const n = parseFloat(val) || 0;
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `$${(n / 1_000).toFixed(1)}K`;
  return `$${n.toLocaleString()}`;
}

export default function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/leads/dashboard/")
      .then(({ data }) => setData(data))
      .catch(() => setError("Failed to load dashboard data."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="loading-page">
        <div className="spinner" style={{ width: 28, height: 28 }} />
      </div>
    );
  }

  if (error) {
    return (
      <p style={{ color: "var(--red)", padding: "var(--sp-8)" }}>{error}</p>
    );
  }

  const byStatus = data?.by_status || {};
  const statusEntries = Object.entries(STATUS_META);

  return (
    <div className="dashboard animate-fade">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Dashboard</h1>
          <p className="dashboard-greeting">
            Good {getTimeOfDay()},{" "}
            <span style={{ color: "var(--accent)" }}>
              {user?.first_name || user?.email?.split("@")[0]}
            </span>
          </p>
        </div>
        <Link to="/leads" className="btn btn-primary">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 1v12M1 7h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
          New Lead
        </Link>
      </div>

      <div className="stat-grid">
        <StatCard
          label="Total Leads"
          value={data.total}
          sub="in your pipeline"
          delay={0}
        />
        <StatCard
          label="Conversion Rate"
          value={`${data.conversion_rate}%`}
          sub="leads to closed"
          accent="var(--green)"
          delay={60}
        />
        <StatCard
          label="Pipeline Value"
          value={currency(data.total_value)}
          sub="total deal value"
          accent="var(--accent)"
          delay={120}
        />
        <StatCard
          label="Average Lead Value"
          value={currency(data.average_value)}
          sub="average opportunity"
          accent="var(--blue)"
          delay={180}
        />
        <StatCard
          label="Follow-ups"
          value={data.follow_ups}
          sub={data.follow_ups === 1 ? "lead scheduled" : "leads scheduled"}
          accent={data.follow_ups > 0 ? "var(--accent)" : undefined}
          delay={240}
        />
      </div>

      <div className="dashboard-grid">
        <div className="card dashboard-status">
          <h2 className="section-title">Pipeline by Status</h2>
          <div className="status-bars">
            {statusEntries.map(([key, meta]) => {
              const count = byStatus[key] || 0;
              const pct = data.total > 0 ? (count / data.total) * 100 : 0;

              return (
                <div key={key} className="status-bar-row">
                  <div className="status-bar-label">
                    <span className="status-dot" style={{ background: meta.color }} />
                    <span>{meta.label}</span>
                  </div>
                  <div className="status-bar-track">
                    <div
                      className="status-bar-fill"
                      style={{ width: `${pct}%`, background: meta.color }}
                    />
                  </div>
                  <span className="status-bar-count">{count}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="card dashboard-recent">
          <div className="section-header">
            <h2 className="section-title">Pipeline Snapshot</h2>
            <Link to="/leads" className="btn btn-ghost btn-sm">View all</Link>
          </div>

          <div className="recent-leads">
            {statusEntries.map(([key, meta], i) => (
              <div
                key={key}
                className="recent-lead-row animate-fade"
                style={{ animationDelay: `${i * 40}ms` }}
              >
                <div className="recent-lead-avatar" style={{ background: `${meta.color}20`, color: meta.color }}>
                  {meta.label[0]}
                </div>
                <div className="recent-lead-info">
                  <span className="recent-lead-name">{meta.label}</span>
                  <span className="recent-lead-company">
                    {byStatus[key] || 0} lead{(byStatus[key] || 0) === 1 ? "" : "s"}
                  </span>
                </div>
                <div className="recent-lead-right">
                  <span
                    className="recent-lead-status"
                    style={{ color: meta.color }}
                  >
                    {data.total > 0 ? `${Math.round(((byStatus[key] || 0) / data.total) * 100)}%` : "0%"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function getTimeOfDay() {
  const h = new Date().getHours();
  if (h < 12) return "morning";
  if (h < 17) return "afternoon";
  return "evening";
}
