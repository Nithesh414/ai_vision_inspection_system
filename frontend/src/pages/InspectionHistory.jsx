import { useEffect, useState } from "react";
import { getInspections } from "../api/client";

export default function InspectionHistory() {
  const [inspections, setInspections] = useState([]);
  const [filter, setFilter] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getInspections(filter || undefined)
      .then(setInspections)
      .catch(() => setError("Could not load inspection history."));
  }, [filter]);

  return (
    <div>
      <div className="page-header">
        <div>
          <p className="page-eyebrow">Records</p>
          <h1 className="page-title">Inspection History</h1>
        </div>
        <select value={filter} onChange={(e) => setFilter(e.target.value)} style={{ padding: 8, borderRadius: 6, border: "1px solid #d8dbd6" }}>
          <option value="">All statuses</option>
          <option value="PASS">Pass only</option>
          <option value="FAIL">Fail only</option>
        </select>
      </div>

      {error && <div className="card" style={{ color: "var(--fail-red)" }}>{error}</div>}

      <div className="card" style={{ padding: 0 }}>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Status</th>
              <th>Severity</th>
              <th>Confidence</th>
              <th>Defects</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {inspections.map((i) => (
              <tr key={i.id}>
                <td>{new Date(i.created_at).toLocaleString()}</td>
                <td><span className={`stamp ${i.status === "PASS" ? "pass" : "fail"}`} style={{ transform: "none", fontSize: 11, padding: "3px 8px" }}>{i.status}</span></td>
                <td>{i.severity && <span className={`severity-badge ${i.severity}`}>{i.severity}</span>}</td>
                <td>{i.confidence != null ? `${(i.confidence * 100).toFixed(1)}%` : "—"}</td>
                <td>{i.defects?.length || 0}</td>
                <td>{i.inspection_time_seconds ? `${i.inspection_time_seconds}s` : "—"}</td>
              </tr>
            ))}
            {inspections.length === 0 && (
              <tr><td colSpan={6} style={{ textAlign: "center", color: "var(--ink-soft)", padding: 24 }}>No inspections yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
