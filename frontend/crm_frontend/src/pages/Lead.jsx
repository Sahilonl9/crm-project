import { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axiosInstance";
import LeadCard from "../components/LeadCard";
import LeadForm from "../components/LeadForm";
import "./Lead.css";


const STATUS_OPTIONS = [
  { value: '',           label: 'All Statuses' },
  { value: 'new',        label: 'New' },
  { value: 'contacted',  label: 'Contacted' },
  { value: 'interested', label: 'Interested' },
  { value: 'closed',     label: 'Closed' },
]

const SOURCE_OPTIONS = [
  { value: '',             label: 'All Sources' },
  { value: 'website',      label: 'Website' },
  { value: 'referral',     label: 'Referral' },
  { value: 'social_media', label: 'Social Media' },
  { value: 'cold_call',    label: 'Cold Call' },
  { value: 'email',        label: 'Email Campaign' },
  { value: 'event',        label: 'Event' },
  { value: 'other',        label: 'Other' },
]

export default function Leads() {
  const navigate = useNavigate()
  const [leads, setLeads]           = useState([])
  const [loading, setLoading]       = useState(true)
  const [search, setSearch]         = useState('')
  const [status, setStatus]         = useState('')
  const [source, setSource]         = useState('')
  const [showForm, setShowForm]     = useState(false)
  const [page, setPage]             = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const [pageSize]                  = useState(20)
  const searchTimer                 = useRef(null)

  const fetchLeads = useCallback(async (params = {}) => {
    setLoading(true)
    try {
      const { data } = await api.get('/leads/', {
        params: {
          search: params.search  ?? search,
          status: params.status  ?? status,
          source: params.source  ?? source,
          page:   params.page    ?? page,
        },
      })
      setLeads(data.results ?? data)
      setTotalCount(data.count ?? (data.results ?? data).length)
    } catch (_) {}
    finally { setLoading(false) }
  }, [search, status, source, page])

  useEffect(() => { fetchLeads() }, [status, source, page])

  const handleSearch = (val) => {
    setSearch(val)
    clearTimeout(searchTimer.current)
    searchTimer.current = setTimeout(() => {
      setPage(1)
      fetchLeads({ search: val, page: 1 })
    }, 350)
  }

  const handleStatusChange = (val) => { setStatus(val); setPage(1) }
  const handleSourceChange = (val) => { setSource(val); setPage(1) }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this lead? This action cannot be undone.')) return
    try {
      await api.delete(`/leads/${id}/`)
      setLeads((prev) => prev.filter((l) => l.id !== id))
      setTotalCount((c) => c - 1)
    } catch (_) {}
  }

  const handleCreated = (lead) => {
    setShowForm(false)
    navigate(`/leads/${lead.id}`)
  }

  const totalPages = Math.ceil(totalCount / pageSize)

  return (
    <div className="leads-page">
      {/* Page header */}
      <div className="leads-header">
        <div>
          <h1 className="leads-title">Leads</h1>
          <p className="leads-count">
            {totalCount} {totalCount === 1 ? 'lead' : 'leads'} in your pipeline
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 1v12M1 7h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          New Lead
        </button>
      </div>

      {/* Inline create form */}
      {showForm && (
        <div className="card leads-form-panel animate-fade">
          <LeadForm
            onSuccess={handleCreated}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      {/* Filters */}
      <div className="leads-filters">
        {/* Search */}
        <div className="leads-search">
          <svg className="leads-search-icon" width="15" height="15" viewBox="0 0 15 15" fill="none">
            <circle cx="6.5" cy="6.5" r="5" stroke="currentColor" strokeWidth="1.4"/>
            <path d="M10.5 10.5l3 3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
          </svg>
          <input
            className="leads-search-input"
            placeholder="Search by name, email, company…"
            value={search}
            onChange={(e) => handleSearch(e.target.value)}
          />
          {search && (
            <button className="leads-search-clear" onClick={() => handleSearch('')}>✕</button>
          )}
        </div>

        {/* Status filter */}
        <div className="form-select-wrap leads-filter-select">
          <select
            className="form-select"
            value={status}
            onChange={(e) => handleStatusChange(e.target.value)}
          >
            {STATUS_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
          <span className="form-select-arrow">▾</span>
        </div>

        {/* Source filter */}
        <div className="form-select-wrap leads-filter-select">
          <select
            className="form-select"
            value={source}
            onChange={(e) => handleSourceChange(e.target.value)}
          >
            {SOURCE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
          <span className="form-select-arrow">▾</span>
        </div>

        {/* Reset */}
        {(search || status || source) && (
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => { setSearch(''); setStatus(''); setSource(''); setPage(1) }}
          >
            Reset filters
          </button>
        )}
      </div>

      {/* Lead grid */}
      {loading ? (
        <div className="leads-loading">
          <div className="spinner" style={{ width: 28, height: 28 }} />
        </div>
      ) : leads.length === 0 ? (
        <div className="leads-empty">
          <svg width="40" height="40" viewBox="0 0 40 40" fill="none" opacity="0.3">
            <circle cx="20" cy="20" r="18" stroke="currentColor" strokeWidth="2"/>
            <path d="M13 20h14M20 13v14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <p>No leads found.</p>
          <button className="btn btn-primary btn-sm" onClick={() => setShowForm(true)}>
            Create your first lead
          </button>
        </div>
      ) : (
        <div className="leads-grid">
          {leads.map((lead, i) => (
            <div key={lead.id} style={{ animationDelay: `${i * 30}ms` }}>
              <LeadCard lead={lead} onDelete={handleDelete} />
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="leads-pagination">
          <button
            className="btn btn-secondary btn-sm"
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
          >
            ← Prev
          </button>
          <span className="leads-page-info">
            Page {page} of {totalPages}
          </span>
          <button
            className="btn btn-secondary btn-sm"
            disabled={page === totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}