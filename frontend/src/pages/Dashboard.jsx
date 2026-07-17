import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import { getDashboardSummary, getTrends } from "../api/client";

const PIE_COLORS = ["#1f9d55", "#d13b3b"];

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getDashboardSummary(), getTrends(14)])
      .then(([s, t]) => {
        setSummary(s);
        setTrends(t);
      })
      .catch(() => setError("Could not load dashboard data. Is the backend running?"));
  }, []);

  const pieData = summary
    ? [
        { name: "Pass", value: summary.pass_count },
        { name: "Fail", value: summary.fail_count },
      ]
    : [];

  return (
    <div>
      <div className="page-header">
        <div>
          <p className="page-eyebrow">Today · Line 04</p>
          <h1 className="page-title">Dashboard</h1>
        </div>
      </div>

      {error && <div className="card" style={{ color: "var(--fail-red)" }}>{error}</div>}

      {summary && (
        <>
          <div className="stat-grid">
            <div className="stat-card">
              <div className="stat-label">Today's Inspections</div>
              <div className="stat-value">{summary.todays_inspections}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Pass Count</div>
              <div className="stat-value" style={{ color: "var(--pass-green)" }}>{summary.pass_count}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Fail Count</div>
              <div className="stat-value" style={{ color: "var(--fail-red)" }}>{summary.fail_count}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Accuracy Estimate</div>
              <div className="stat-value">
                {summary.accuracy_estimate != null ? `${(summary.accuracy_estimate * 100).toFixed(1)}%` : "—"}
              </div>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1.4fr", gap: 16 }}>
            <div className="card">
              <div className="stat-label" style={{ marginBottom: 12 }}>Pass / Fail Split</div>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80}>
                    {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="card">
              <div className="stat-label" style={{ marginBottom: 12 }}>Most Common Defects</div>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={summary.most_common_defects}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#eceeec" />
                  <XAxis dataKey="defect_type" fontSize={12} />
                  <YAxis fontSize={12} allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#f0a202" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card" style={{ marginTop: 16 }}>
            <div className="stat-label" style={{ marginBottom: 12 }}>Inspection Trend (14 days)</div>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#eceeec" />
                <XAxis dataKey="day" fontSize={11} />
                <YAxis fontSize={12} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#3a4552" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}
