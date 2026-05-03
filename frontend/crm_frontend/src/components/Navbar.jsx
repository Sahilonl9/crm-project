import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Navbar.css";

const agentNavItems = [
  {
    to: "/dashboard",
    label: "Dashboard",
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <rect x="1" y="1" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
        <rect x="9" y="1" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
        <rect x="1" y="9" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
        <rect x="9" y="9" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
      </svg>
    ),
  },
  {
    to: "/leads",
    label: "Leads",
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <circle cx="6" cy="5" r="3" stroke="currentColor" strokeWidth="1.5" />
        <path d="M1 14c0-2.761 2.239-5 5-5s5 2.239 5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M11 7l1.5 1.5L15 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
];

const customerNavItems = [
  {
    to: "/my-chats",
    label: "My Chats",
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M3 4.5A2.5 2.5 0 015.5 2h5A2.5 2.5 0 0113 4.5v3A2.5 2.5 0 0110.5 10H8l-3 3v-3H5.5A2.5 2.5 0 013 7.5v-3z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
      </svg>
    ),
  },
];

export default function Navbar() {
  const { user, logout } = useAuth();

  const navItems = user?.role === "customer" ? customerNavItems : agentNavItems;

  return (
    <aside className="navbar">
      <div className="navbar-logo">
        <span className="navbar-logo-mark">♛</span>
        <span className="navbar-logo-text">CRM</span>
      </div>

      <nav className="navbar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `navbar-link${isActive ? " navbar-link--active" : ""}`
            }
          >
            <span className="navbar-link-icon">{item.icon}</span>
            <span className="navbar-link-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="navbar-footer">
        <div className="navbar-user">
          <div className="navbar-avatar">
            {user?.first_name?.[0] || user?.email?.[0]?.toUpperCase() || "?"}
          </div>
          <div className="navbar-user-info">
            <span className="navbar-user-name">{user?.full_name || user?.email}</span>
            <span className="navbar-user-email">{user?.email}</span>
          </div>
        </div>

        <button className="navbar-logout" onClick={logout} title="Sign out">
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
            <path d="M6 2H3a1 1 0 00-1 1v9a1 1 0 001 1h3M10 10l3-3-3-3M13 7.5H6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
      </div>
    </aside>
  );
}
