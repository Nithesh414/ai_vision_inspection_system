import { useAuth } from "../context/AuthContext.jsx";

export default function Settings() {
  const { user } = useAuth();

  return (
    <div>
      <div className="page-header">
        <div>
          <p className="page-eyebrow">Account</p>
          <h1 className="page-title">Settings</h1>
        </div>
      </div>

      <div className="card" style={{ maxWidth: 480 }}>
        <div className="field">
          <label>Username</label>
          <input value={user?.username || ""} disabled />
        </div>
        <div className="field">
          <label>Role</label>
          <input value={user?.role || ""} disabled />
        </div>
        <p style={{ fontSize: 13, color: "var(--ink-soft)" }}>
          Product specifications, component tolerances, and user accounts are managed by
          administrators via the API (<code>/api/products</code>, <code>/api/auth/register</code>).
        </p>
      </div>
    </div>
  );
}
