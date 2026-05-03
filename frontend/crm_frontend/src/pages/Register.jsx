import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Auth.css";

export default function Register() {
  const { register } = useAuth();
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    password2: "",
    role: "agent",
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const validate = () => {
    const e = {};
    if (!form.first_name.trim()) e.first_name = "Required";
    if (!form.email.trim()) e.email = "Required";
    if (!form.password) e.password = "Required";
    if (form.password.length < 8) e.password = "Minimum 8 characters";
    if (form.password !== form.password2) e.password2 = "Passwords do not match";
    return e;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) {
      setErrors(errs);
      return;
    }

    setErrors({});
    setLoading(true);
    try {
      await register(form);
    } catch (err) {
      const data = err.response?.data || {};
      if (typeof data === "object") setErrors(data);
      else setErrors({ general: "Registration failed. Please try again." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-bg">
        <div className="auth-bg-grid" />
        <div className="auth-bg-glow" style={{ right: "10%", left: "auto" }} />
      </div>

      <div className="auth-card auth-card--wide animate-fade">
        <div className="auth-logo">
          <span className="auth-logo-mark">♛</span>
          <span className="auth-logo-text">CRM</span>
        </div>

        <div className="auth-heading">
          <h1 className="auth-title">Create account</h1>
          <p className="auth-subtitle">Join as an agent or customer</p>
        </div>

        <div className="auth-form-row" style={{ marginBottom: 16 }}>
          <button
            type="button"
            className={`btn ${form.role === "agent" ? "btn-primary" : "btn-secondary"}`}
            onClick={() => setForm((f) => ({ ...f, role: "agent" }))}
          >
            I am a Salesperson
          </button>
          <button
            type="button"
            className={`btn ${form.role === "customer" ? "btn-primary" : "btn-secondary"}`}
            onClick={() => setForm((f) => ({ ...f, role: "customer" }))}
          >
            I am a Customer
          </button>
        </div>

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="auth-form-row">
            <div className="form-group">
              <label className="form-label">First Name *</label>
              <input className="form-input" value={form.first_name} onChange={set("first_name")} placeholder="Sahil" autoFocus />
              {errors.first_name && <span className="form-error">{errors.first_name}</span>}
            </div>
            <div className="form-group">
              <label className="form-label">Last Name</label>
              <input className="form-input" value={form.last_name} onChange={set("last_name")} placeholder="Ray" />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Email *</label>
            <input className="form-input" type="email" value={form.email} onChange={set("email")} placeholder="you@company.com" autoComplete="email" />
            {errors.email && <span className="form-error">{errors.email}</span>}
          </div>

          <div className="auth-form-row">
            <div className="form-group">
              <label className="form-label">Password *</label>
              <input className="form-input" type="password" value={form.password} onChange={set("password")} placeholder="Min 8 characters" autoComplete="new-password" />
              {errors.password && <span className="form-error">{errors.password}</span>}
            </div>
            <div className="form-group">
              <label className="form-label">Confirm Password *</label>
              <input className="form-input" type="password" value={form.password2} onChange={set("password2")} placeholder="Repeat password" autoComplete="new-password" />
              {errors.password2 && <span className="form-error">{errors.password2}</span>}
            </div>
          </div>

          {errors.general && <p className="auth-error">{errors.general}</p>}

          <button type="submit" className="btn btn-primary btn-lg auth-submit" disabled={loading}>
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account? <Link to="/login" className="auth-link">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
