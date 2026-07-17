import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { getTrends } from "../api/client";

export default function Analytics() {
  const [trends, setTrends] = useState([]);
  const [days, setDays] = useState(30);
  const [error, setError] = useState("");

  useEffect(() => {
    getTrends(days).then(setTrends).catch(() => setError("Could not load analytics."));
  }, [days]);

  // Reshape into { day, pass, fail }
  const byDay = {};
  trends.forEach((t) => {
    byDay[t.day] = byDay[t.day] || { day: t.day, PASS: 0, FAIL: 0 };
    byDay[t.day][t.status] = t.count;
  });
  const chartData = Object.values(byDay);

  return (
    <div>
      <div className="page-header">
        <div>
          <p className="page-eyebrow">Quality Trends</p>
          <h1 className="page-title">Analytics</h1>
        </div>
        <select value={days} onChange={(e) => setDays(Number(e.target.value))} style={{ padding: 8, borderRadius: 6, border: "1px solid #d8dbd6" }}>
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {error && <div className="card" style={{ color: "var(--fail-red)" }}>{error}</div>}

      <div className="card">
        <div className="stat-label" style={{ marginBottom: 12 }}>Pass vs Fail Over Time</div>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#eceeec" />
            <XAxis dataKey="day" fontSize={11} />
            <YAxis fontSize={12} allowDecimals={false} />
            <Tooltip />
            <Line type="monotone" dataKey="PASS" stroke="#1f9d55" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="FAIL" stroke="#d13b3b" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
