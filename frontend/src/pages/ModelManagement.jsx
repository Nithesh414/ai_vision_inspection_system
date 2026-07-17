import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function ModelManagement() {
  const [versions, setVersions] = useState([]);
  const [queue, setQueue] = useState([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  function refresh() {
    api.get("/api/models/versions").then((r) => setVersions(r.data)).catch(() => setError("Could not load model versions."));
    api.get("/api/models/retrain/queue").then((r) => setQueue(r.data)).catch(() => {});
  }

  useEffect(refresh, []);

  async function triggerRetrain() {
    setMessage("");
    setError("");
    try {
      await api.post("/api/models/retrain");
      setMessage("Retraining job queued.");
      refresh();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not trigger retraining.");
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <p className="page-eyebrow">Continuous Learning</p>
          <h1 className="page-title">Model Management</h1>
        </div>
        <button className="btn amber" onClick={triggerRetrain}>Trigger Retraining</button>
      </div>

      {error && <div className="card" style={{ color: "var(--fail-red)", marginBottom: 16 }}>{error}</div>}
      {message && <div className="card" style={{ color: "var(--pass-green)", marginBottom: 16 }}>{message}</div>}

      <div className="card" style={{ padding: 0, marginBottom: 20 }}>
        <table>
          <thead>
            <tr><th>Module</th><th>Version</th><th>Active</th><th>Trained</th></tr>
          </thead>
          <tbody>
            {versions.map((v) => (
              <tr key={v.id}>
                <td>{v.module}</td>
                <td style={{ fontFamily: "var(--font-mono)" }}>{v.version_tag}</td>
                <td>{v.is_active ? "✓ Active" : "—"}</td>
                <td>{new Date(v.trained_at).toLocaleDateString()}</td>
              </tr>
            ))}
            {versions.length === 0 && (
              <tr><td colSpan={4} style={{ textAlign: "center", color: "var(--ink-soft)", padding: 24 }}>No trained model versions yet — inference runs in stub mode until weights are added.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="stat-label" style={{ marginBottom: 10 }}>Retraining Queue</div>
      <div className="card" style={{ padding: 0 }}>
        <table>
          <thead>
            <tr><th>Status</th><th>Dataset Size</th><th>Queued</th></tr>
          </thead>
          <tbody>
            {queue.map((q) => (
              <tr key={q.id}>
                <td>{q.status}</td>
                <td>{q.dataset_snapshot_count}</td>
                <td>{new Date(q.created_at).toLocaleString()}</td>
              </tr>
            ))}
            {queue.length === 0 && (
              <tr><td colSpan={3} style={{ textAlign: "center", color: "var(--ink-soft)", padding: 24 }}>No retraining jobs yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
