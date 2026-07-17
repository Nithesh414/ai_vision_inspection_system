import { useEffect, useState } from "react";
import { getProducts, createInspection } from "../api/client";

export default function Inspect() {
  const [products, setProducts] = useState([]);
  const [productId, setProductId] = useState("");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getProducts().then(setProducts).catch(() => setError("Could not load products."));
  }, []);

  function handleFile(e) {
    const f = e.target.files[0];
    setFile(f);
    setResult(null);
    setPreview(f ? URL.createObjectURL(f) : null);
  }

  async function runInspection() {
    if (!productId || !file) {
      setError("Select a product and capture/upload an image first.");
      return;
    }
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const data = await createInspection(productId, file);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Inspection failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <p className="page-eyebrow">Operator Console</p>
          <h1 className="page-title">New Inspection</h1>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <div className="card">
          <div className="field">
            <label>Product</label>
            <select value={productId} onChange={(e) => setProductId(e.target.value)} style={{ width: "100%", padding: 10, marginTop: 6, borderRadius: 6, border: "1px solid #d8dbd6" }}>
              <option value="">Select product…</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>{p.name} ({p.code})</option>
              ))}
            </select>
          </div>

          <div className="field">
            <label>Capture / Upload Image</label>
            <input type="file" accept="image/*" capture="environment" onChange={handleFile} style={{ marginTop: 6 }} />
          </div>

          {preview && (
            <img src={preview} alt="preview" style={{ width: "100%", borderRadius: 8, marginTop: 8, maxHeight: 260, objectFit: "cover" }} />
          )}

          {error && <div className="error-text">{error}</div>}

          <button className="btn amber" style={{ marginTop: 16 }} onClick={runInspection} disabled={loading}>
            {loading ? "Inspecting…" : "Run Inspection"}
          </button>
        </div>

        <div className="card">
          <div className="stat-label" style={{ marginBottom: 12 }}>Result</div>
          {!result && <div style={{ color: "var(--ink-soft)", fontSize: 14 }}>Run an inspection to see the decision here.</div>}
          {result && (
            <div>
              <span className={`stamp ${result.status === "PASS" ? "pass" : "fail"}`}>{result.status}</span>
              <div style={{ marginTop: 14, fontFamily: "var(--font-mono)", fontSize: 13, color: "var(--ink-soft)" }}>
                Confidence {(result.confidence * 100).toFixed(1)}% · {result.inspection_time_seconds}s
                {result.severity && (
                  <span className={`severity-badge ${result.severity}`} style={{ marginLeft: 10 }}>{result.severity}</span>
                )}
              </div>

              <div style={{ marginTop: 18 }}>
                <div className="stat-label">Reasons</div>
                <ul style={{ paddingLeft: 18, fontSize: 14 }}>
                  {result.reasons.map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              </div>

              {result.suggested_actions?.length > 0 && (
                <div style={{ marginTop: 14 }}>
                  <div className="stat-label">Suggested Actions</div>
                  <ul style={{ paddingLeft: 18, fontSize: 14 }}>
                    {result.suggested_actions.map((a, i) => <li key={i}>{a}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
