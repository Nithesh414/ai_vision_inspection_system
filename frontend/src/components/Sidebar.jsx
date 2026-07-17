import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

const LINKS = [
  { to: "/", label: "Dashboard" },
  { to: "/inspect", label: "New Inspection" },
  { to: "/history", label: "Inspection History" },
  { to: "/analytics", label: "Analytics" },
  { to: "/reports", label: "Reports" },
  { to: "/models", label: "Model Management" },
  { to: "/settings", label: "Settings" },
];

export default function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <div className="sidebar">
      <div className="sidebar-brand">
        Line 04 · QC Station
        <strong>Inspection Platform</strong>
      </div>
      {LINKS.map((l) => (
        <NavLink
          key={l.to}
          to={l.to}
          end={l.to === "/"}
          className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
        >
          {l.label}
        </NavLink>
      ))}
      <div style={{ marginTop: "auto", paddingTop: 20, borderTop: "1px solid var(--graphite-700)" }}>
        <div style={{ fontSize: 13, color: "#8b96a3", padding: "0 12px 8px" }}>
          {user?.username} · {user?.role}
        </div>
        <button className="nav-link" style={{ width: "100%", textAlign: "left", background: "none", border: "none" }} onClick={logout}>
          Log out
        </button>
      </div>
    </div>
  );
}
