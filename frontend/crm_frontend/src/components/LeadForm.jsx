import { useState, useEffect } from "react";
import api from "../api/axiosInstance";
import "./LeadForm.css";

const STATUS_OPTIONS = [
  { value: "new", label: "New" },
  { value: "contacted", label: "Contacted" },
  { value: "interested", label: "Interested" },
  { value: "closed", label: "Closed" },
];

const SOURCE_OPTIONS = [
  { value: "website", label: "Website" },
  { value: "referral", label: "Referral" },
  { value: "social_media", label: "Social Media" },
  { value: "cold_call", label: "Cold Call" },
  { value: "email", label: "Email Campaign" },
  { value: "event", label: "Event" },
  { value: "other", label: "Other" },
];

const EMPTY = {
  name: "",
  email: "",
  phone: "",
  company: "",
  status: "new",
  source: "other",
  value: "",
  follow_up_date: "",
  description: "",
  customer_id: "",
};

export default function LeadForm({ lead = null, onSuccess, onCancel }) {
  const isEdit = Boolean(lead);
  const [form, setForm] = useState(EMPTY);
  const [customers, setCustomers] = useState([]);
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get("/auth/customers/")
      .then(({ data }) => setCustomers(data.results || data))
      .catch(() => setCustomers([]));
  }, []);

  useEffect(() => {
    if (lead) {
      setForm({
        name: lead.name || "",
        email: lead.email || "",
        phone: lead.phone || "",
        company: lead.company || "",
        status: lead.status || "new",
        source: lead.source || "other",
        value: lead.value || "",
        follow_up_date: lead.follow_up_date || "",
        description: lead.description || "",
        customer_id: lead.customer?.id || "",
      });
    } else {
      setForm(EMPTY);
    }
  }, [lead]);

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const validate = () => {
    const e = {};
    if (!form.name.trim()) e.name = "Name is required";
    if (form.email && !/\S+@\S+\.\S+/.test(form.email)) e.email = "Invalid email";
    if (form.value && isNaN(parseFloat(form.value))) e.value = "Must be a number";
    return e;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const e_ = validate();
    if (Object.keys(e_).length) {
      setErrors(e_);
      return;
    }

    setErrors({});
    setSaving(true);

    const payload = {
      ...form,
      value: parseFloat(form.value) || 0,
      customer_id: form.customer_id || null,
    };

    try {
      if (isEdit) {
        const { data } = await api.patch(`/leads/${lead.id}/`, payload);
        onSuccess?.(data);
      } else {
        const { data } = await api.post("/leads/", payload);
        onSuccess?.(data);
      }
    } catch (err) {
      const data = err.response?.data || {};
      setErrors(typeof data === "object" ? data : { general: "Something went wrong." });
    } finally {
      setSaving(false);
    }
  };

  return (
    <form className="lead-form" onSubmit={handleSubmit} noValidate>
      <div className="lead-form-title">
        {isEdit ? "Edit Lead" : "New Lead"}
      </div>

      <div className="lead-form-grid">
        <div className="form-group lead-form-full">
          <label className="form-label">Name *</label>
          <input className="form-input" value={form.name} onChange={set("name")} placeholder="Full name" />
          {errors.name && <span className="form-error">{errors.name}</span>}
        </div>

        <div className="form-group">
          <label className="form-label">Email</label>
          <input className="form-input" type="email" value={form.email} onChange={set("email")} placeholder="email@example.com" />
          {errors.email && <span className="form-error">{errors.email}</span>}
        </div>

        <div className="form-group">
          <label className="form-label">Phone</label>
          <input className="form-input" value={form.phone} onChange={set("phone")} placeholder="+1 234 567 8900" />
        </div>

        <div className="form-group">
          <label className="form-label">Company</label>
          <input className="form-input" value={form.company} onChange={set("company")} placeholder="Company name" />
        </div>

        <div className="form-group">
          <label className="form-label">Deal Value ($)</label>
          <input className="form-input" value={form.value} onChange={set("value")} placeholder="0" />
          {errors.value && <span className="form-error">{errors.value}</span>}
        </div>

        <div className="form-group">
          <label className="form-label">Status</label>
          <div className="form-select-wrap">
            <select className="form-select" value={form.status} onChange={set("status")}>
              {STATUS_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
            <span className="form-select-arrow">▾</span>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Source</label>
          <div className="form-select-wrap">
            <select className="form-select" value={form.source} onChange={set("source")}>
              {SOURCE_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
            <span className="form-select-arrow">▾</span>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Follow-up Date</label>
          <input className="form-input" type="date" value={form.follow_up_date} onChange={set("follow_up_date")} />
        </div>

        <div className="form-group lead-form-full">
          <label className="form-label">Assign Customer</label>
          <div className="form-select-wrap">
            <select className="form-select" value={form.customer_id} onChange={set("customer_id")}>
              <option value="">Unassigned</option>
              {customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.full_name} ({customer.email})
                </option>
              ))}
            </select>
            <span className="form-select-arrow">▾</span>
          </div>
        </div>

        <div className="form-group lead-form-full">
          <label className="form-label">Notes / Description</label>
          <textarea
            className="form-textarea"
            value={form.description}
            onChange={set("description")}
            placeholder="Add context about this lead..."
            rows={3}
          />
        </div>
      </div>

      {errors.general && (
        <p className="form-error" style={{ textAlign: "center" }}>{errors.general}</p>
      )}

      <div className="lead-form-actions">
        {onCancel && (
          <button type="button" className="btn btn-secondary" onClick={onCancel}>
            Cancel
          </button>
        )}
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? "Saving..." : isEdit ? "Save Changes" : "Create Lead"}
        </button>
      </div>
    </form>
  );
}
