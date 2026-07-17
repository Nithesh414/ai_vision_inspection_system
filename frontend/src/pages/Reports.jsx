import { useEffect, useState } from "react";
import { getInspections } from "../api/client";
import { api } from "../api/client";

export default function Reports() {
  const [inspections, setInspections] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getInspections().then(setInspections).catch(() => setError("Could not load reports."));
  }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <p className="page-eyebrow">PDF Exports</p>
          <h1 className="page-title">Reports</h1>
        </div>
      </div>

      {error && <div className="card" style={{ color: "var(--fail-red)" }}>{error}</div>}

      <div className="card" style={{ padding: 0 }}>
        <table>
          <thead>
            <tr>
              <th>Inspection</th>
              <th>Date</th>
              <th>Status</th>
              <th>Report</th>
            </tr>
          </thead>
          <tbody>
            {inspections.map((i) => (
              <tr key={i.id}>
                <td style={{ fontFamily: "var(--font-mono)", fontSize: 12 }}>{i.id.slice(0, 8)}</td>
                <td>{new Date(i.created_at).toLocaleString()}</td>
                <td><span className={`stamp ${i.status === "PASS" ? "pass" : "fail"}`} style={{ transform: "none", fontSize: 11, padding: "3px 8px" }}>{i.status}</span></td>
                <td>
                  <a href={`${api.defaults.baseURL}/uploads/reports/${i.id}.pdf`} target="_blank" rel="noreferrer" style={{ color: "var(--amber)", fontWeight: 600 }}>
                    View PDF
                  </a>
                </td>
              </tr>
            ))}
            {inspections.length === 0 && (
              <tr><td colSpan={4} style={{ textAlign: "center", color: "var(--ink-soft)", padding: 24 }}>No reports yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
