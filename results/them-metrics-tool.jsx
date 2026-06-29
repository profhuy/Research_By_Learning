import { useState, useCallback } from "react";

const LABELS = ["Sufficient", "Ambiguous", "Missing", "Incorrect"];
const COMPONENTS = ["OB", "EB", "S2R"];

const LABEL_COLORS = {
  Sufficient: { bg: "#eaf3de", text: "#3b6d11", border: "#639922" },
  Ambiguous: { bg: "#faeeda", text: "#854f0b", border: "#ba7517" },
  Missing: { bg: "#fcebeb", text: "#a32d2d", border: "#e24b4a" },
  Incorrect: { bg: "#EEEDFE", text: "#3C3489", border: "#7F77DD" },
};

function computeKappa(annotations) {
  if (annotations.length < 2) return null;
  const n = annotations.length;
  let agree = 0;
  let total = 0;
  const labelCountsA = {};
  const labelCountsB = {};
  LABELS.forEach(l => { labelCountsA[l] = 0; labelCountsB[l] = 0; });

  for (const row of annotations) {
    if (!row.ann1 || !row.ann2) continue;
    total++;
    if (row.ann1 === row.ann2) agree++;
    labelCountsA[row.ann1]++;
    labelCountsB[row.ann2]++;
  }

  if (total === 0) return null;

  const po = agree / total;
  let pe = 0;
  for (const l of LABELS) {
    pe += (labelCountsA[l] / total) * (labelCountsB[l] / total);
  }

  if (pe === 1) return po === 1 ? 1 : 0;
  return (po - pe) / (1 - pe);
}

function kappaInterpretation(k) {
  if (k === null) return { label: "N/A", color: "#888" };
  if (k < 0) return { label: "No agreement", color: "#e24b4a" };
  if (k < 0.2) return { label: "Slight", color: "#ef9f27" };
  if (k < 0.4) return { label: "Fair", color: "#eda100" };
  if (k < 0.6) return { label: "Moderate", color: "#639922" };
  if (k < 0.8) return { label: "Substantial", color: "#1D9E75" };
  return { label: "Almost perfect", color: "#0F6E56" };
}

function LabelBadge({ label }) {
  if (!label) return <span style={{ color: "var(--text-muted)", fontSize: 13 }}>—</span>;
  const c = LABEL_COLORS[label] || {};
  return (
    <span style={{
      background: c.bg, color: c.text, border: `1px solid ${c.border}`,
      borderRadius: 6, padding: "2px 8px", fontSize: 12, fontWeight: 500,
      whiteSpace: "nowrap"
    }}>{label}</span>
  );
}

function KappaGauge({ value, label }) {
  const threshold = 0.7;
  const passes = value !== null && value >= threshold;
  const interp = kappaInterpretation(value);
  const pct = value !== null ? Math.max(0, Math.min(1, value)) : 0;

  return (
    <div style={{ background: "var(--surface-1)", borderRadius: 12, padding: "1rem 1.25rem", border: "0.5px solid var(--border)" }}>
      <div style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 6 }}>{label}</div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginBottom: 10 }}>
        <span style={{ fontSize: 28, fontWeight: 500, color: value !== null ? interp.color : "var(--text-muted)" }}>
          {value !== null ? value.toFixed(3) : "—"}
        </span>
        {value !== null && (
          <span style={{ fontSize: 12, color: interp.color, fontWeight: 500 }}>{interp.label}</span>
        )}
      </div>
      <div style={{ height: 6, background: "var(--border)", borderRadius: 3, overflow: "hidden" }}>
        <div style={{
          height: "100%", width: `${pct * 100}%`,
          background: value !== null ? interp.color : "var(--border)",
          borderRadius: 3, transition: "width 0.4s"
        }} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4 }}>
        <span style={{ fontSize: 11, color: "var(--text-muted)" }}>0.0</span>
        <span style={{ fontSize: 11, color: value !== null && value >= threshold ? "#3b6d11" : "#a32d2d", fontWeight: 500 }}>
          threshold 0.70 {value !== null ? (passes ? "✓" : "✗") : ""}
        </span>
        <span style={{ fontSize: 11, color: "var(--text-muted)" }}>1.0</span>
      </div>
    </div>
  );
}

const INITIAL_ROWS = Array.from({ length: 10 }, (_, i) => ({
  id: i + 1,
  issueId: `#${1000 + i}`,
  ann1_ob: "", ann1_eb: "", ann1_s2r: "",
  ann2_ob: "", ann2_eb: "", ann2_s2r: "",
  llm_ob: "", llm_eb: "", llm_s2r: "",
  consensus_ob: "", consensus_eb: "", consensus_s2r: "",
}));

export default function App() {
  const [rows, setRows] = useState(INITIAL_ROWS);
  const [activeTab, setActiveTab] = useState("input");
  const [nextId, setNextId] = useState(INITIAL_ROWS.length + 1);

  const update = useCallback((id, field, value) => {
    setRows(prev => prev.map(r => r.id === id ? { ...r, [field]: value } : r));
  }, []);

  const addRow = () => {
    setRows(prev => [...prev, {
      id: nextId,
      issueId: `#${1000 + nextId - 1}`,
      ann1_ob: "", ann1_eb: "", ann1_s2r: "",
      ann2_ob: "", ann2_eb: "", ann2_s2r: "",
      llm_ob: "", llm_eb: "", llm_s2r: "",
      consensus_ob: "", consensus_eb: "", consensus_s2r: "",
    }]);
    setNextId(n => n + 1);
  };

  const removeRow = (id) => setRows(prev => prev.filter(r => r.id !== id));

  const validRows = rows.filter(r =>
    r.ann1_ob && r.ann1_eb && r.ann1_s2r &&
    r.ann2_ob && r.ann2_eb && r.ann2_s2r
  );

  const hhAnnotations = {
    OB: validRows.map(r => ({ ann1: r.ann1_ob, ann2: r.ann2_ob })),
    EB: validRows.map(r => ({ ann1: r.ann1_eb, ann2: r.ann2_eb })),
    S2R: validRows.map(r => ({ ann1: r.ann1_s2r, ann2: r.ann2_s2r })),
  };

  const llmRows = rows.filter(r =>
    r.consensus_ob && r.consensus_eb && r.consensus_s2r &&
    r.llm_ob && r.llm_eb && r.llm_s2r
  );

  const ldAnnotations = {
    OB: llmRows.map(r => ({ ann1: r.consensus_ob, ann2: r.llm_ob })),
    EB: llmRows.map(r => ({ ann1: r.consensus_eb, ann2: r.llm_eb })),
    S2R: llmRows.map(r => ({ ann1: r.consensus_s2r, ann2: r.llm_s2r })),
  };

  const hhKappas = {
    OB: computeKappa(hhAnnotations.OB),
    EB: computeKappa(hhAnnotations.EB),
    S2R: computeKappa(hhAnnotations.S2R),
  };

  const ldKappas = {
    OB: computeKappa(ldAnnotations.OB),
    EB: computeKappa(ldAnnotations.EB),
    S2R: computeKappa(ldAnnotations.S2R),
  };

  const allHH = [
    ...hhAnnotations.OB,
    ...hhAnnotations.EB,
    ...hhAnnotations.S2R,
  ];
  const allLD = [
    ...ldAnnotations.OB,
    ...ldAnnotations.EB,
    ...ldAnnotations.S2R,
  ];

  const overallHH = computeKappa(allHH);
  const overallLD = computeKappa(allLD);

  // Label distribution
  function getLabelDist(anns) {
    const dist = {};
    LABELS.forEach(l => { dist[l] = 0; });
    for (const a of anns) {
      if (a.ann1) dist[a.ann1] = (dist[a.ann1] || 0) + 1;
      if (a.ann2) dist[a.ann2] = (dist[a.ann2] || 0) + 1;
    }
    return dist;
  }

  const hhDist = getLabelDist(allHH);
  const hhTotal = Object.values(hhDist).reduce((a, b) => a + b, 0) || 1;

  // Raw agreement
  function rawAgree(anns) {
    const valid = anns.filter(a => a.ann1 && a.ann2);
    if (!valid.length) return null;
    return valid.filter(a => a.ann1 === a.ann2).length / valid.length;
  }

  const hhRaw = rawAgree(allHH);
  const ldRaw = rawAgree(allLD);

  const nValid = validRows.length;
  const nLLMValid = llmRows.length;
  const nInvalid = rows.length - nValid;

  function SelectCell({ value, onChange, small }) {
    return (
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        style={{ fontSize: small ? 11 : 12, padding: "2px 4px", minWidth: small ? 80 : 100 }}
      >
        <option value="">—</option>
        {LABELS.map(l => <option key={l} value={l}>{l}</option>)}
      </select>
    );
  }

  const tabs = [
    { id: "input", label: "Data entry" },
    { id: "iaa", label: "IAA & Kappa" },
    { id: "summary", label: "Summary" },
  ];

  return (
    <div style={{ padding: "1.5rem 0", fontFamily: "var(--font-sans)" }}>
      <h2 style={{ fontSize: 18, fontWeight: 500, margin: "0 0 4px", color: "var(--text-primary)" }}>
        Metrics & statistics — Thêm (MS)
      </h2>
      <p style={{ fontSize: 13, color: "var(--text-secondary)", margin: "0 0 1.25rem" }}>
        OB / EB / S2R annotation · Cohen's Kappa · threshold ≥ 0.70
      </p>

      <div style={{ display: "flex", gap: 4, marginBottom: "1.25rem", borderBottom: "0.5px solid var(--border)", paddingBottom: "0" }}>
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            style={{
              padding: "6px 14px", fontSize: 13, borderRadius: "var(--radius) var(--radius) 0 0",
              border: "0.5px solid var(--border)",
              borderBottom: activeTab === t.id ? "0.5px solid var(--surface-2)" : "0.5px solid var(--border)",
              background: activeTab === t.id ? "var(--surface-2)" : "var(--surface-1)",
              color: activeTab === t.id ? "var(--text-primary)" : "var(--text-secondary)",
              cursor: "pointer", fontWeight: activeTab === t.id ? 500 : 400,
              marginBottom: -1,
            }}
          >{t.label}</button>
        ))}
      </div>

      {activeTab === "input" && (
        <div>
          <p style={{ fontSize: 12, color: "var(--text-secondary)", margin: "0 0 0.75rem" }}>
            Nhập nhãn của annotator 1, annotator 2, LLM, và consensus. Các dòng thiếu sẽ bị đánh dấu invalid khi tính Kappa.
          </p>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12, tableLayout: "fixed" }}>
              <colgroup>
                <col style={{ width: 40 }} />
                <col style={{ width: 70 }} />
                <col style={{ width: 90 }} /><col style={{ width: 90 }} /><col style={{ width: 90 }} />
                <col style={{ width: 90 }} /><col style={{ width: 90 }} /><col style={{ width: 90 }} />
                <col style={{ width: 90 }} /><col style={{ width: 90 }} /><col style={{ width: 90 }} />
                <col style={{ width: 90 }} /><col style={{ width: 90 }} /><col style={{ width: 90 }} />
                <col style={{ width: 32 }} />
              </colgroup>
              <thead>
                <tr style={{ background: "var(--surface-1)" }}>
                  <th style={th}>#</th>
                  <th style={th}>Issue</th>
                  <th style={{ ...th, color: "#2a78d6" }} colSpan={3}>Annotator 1</th>
                  <th style={{ ...th, color: "#1baf7a" }} colSpan={3}>Annotator 2</th>
                  <th style={{ ...th, color: "#854f0b" }} colSpan={3}>LLM output</th>
                  <th style={{ ...th, color: "#3C3489" }} colSpan={3}>Consensus</th>
                  <th style={th}></th>
                </tr>
                <tr style={{ background: "var(--surface-1)" }}>
                  <th style={th}></th><th style={th}></th>
                  {["OB","EB","S2R","OB","EB","S2R","OB","EB","S2R","OB","EB","S2R"].map((c, i) => (
                    <th key={i} style={{ ...th, fontWeight: 400, fontSize: 11 }}>{c}</th>
                  ))}
                  <th style={th}></th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, idx) => {
                  const incomplete = !row.ann1_ob || !row.ann1_eb || !row.ann1_s2r || !row.ann2_ob || !row.ann2_eb || !row.ann2_s2r;
                  return (
                    <tr key={row.id} style={{ background: idx % 2 === 0 ? "var(--surface-2)" : "var(--surface-1)", opacity: incomplete ? 0.8 : 1 }}>
                      <td style={td}>{idx + 1}</td>
                      <td style={td}>
                        <input value={row.issueId} onChange={e => update(row.id, "issueId", e.target.value)}
                          style={{ width: "100%", fontSize: 12, padding: "2px 4px" }} />
                      </td>
                      {[
                        ["ann1_ob","ann1_eb","ann1_s2r"],
                        ["ann2_ob","ann2_eb","ann2_s2r"],
                        ["llm_ob","llm_eb","llm_s2r"],
                        ["consensus_ob","consensus_eb","consensus_s2r"],
                      ].map((group, gi) =>
                        group.map(field => (
                          <td key={field} style={td}>
                            <SelectCell value={row[field]} onChange={v => update(row.id, field, v)} small />
                          </td>
                        ))
                      )}
                      <td style={td}>
                        <button onClick={() => removeRow(row.id)}
                          style={{ background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)", fontSize: 14, padding: 0 }}>
                          <i className="ti ti-x" aria-hidden="true" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div style={{ marginTop: "0.75rem", display: "flex", gap: 8, alignItems: "center" }}>
            <button onClick={addRow} style={{ fontSize: 13 }}>
              <i className="ti ti-plus" aria-hidden="true" style={{ marginRight: 4 }} />Thêm dòng
            </button>
            <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
              {nValid} dòng hợp lệ (H-H) · {nLLMValid} dòng hợp lệ (LLM) · {nInvalid} incomplete
            </span>
          </div>
        </div>
      )}

      {activeTab === "iaa" && (
        <div>
          <p style={{ fontSize: 12, color: "var(--text-secondary)", margin: "0 0 1rem" }}>
            Tính từ {nValid} dòng có đủ nhãn của cả 2 annotator. Kappa ≥ 0.70 = đạt threshold.
          </p>
          <div style={{ marginBottom: "1.25rem" }}>
            <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text-secondary)", marginBottom: 8 }}>
              Human–Human (Annotator 1 vs Annotator 2)
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12, marginBottom: 12 }}>
              <KappaGauge value={overallHH} label="Overall Kappa (H-H)" />
              {COMPONENTS.map(c => (
                <KappaGauge key={c} value={hhKappas[c]} label={`${c} Kappa (H-H)`} />
              ))}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 10 }}>
              <div style={metricCard}>
                <div style={metricLabel}>Raw agreement (H-H)</div>
                <div style={metricValue}>{hhRaw !== null ? `${(hhRaw * 100).toFixed(1)}%` : "—"}</div>
              </div>
              <div style={metricCard}>
                <div style={metricLabel}>N valid rows</div>
                <div style={metricValue}>{nValid}</div>
              </div>
              <div style={metricCard}>
                <div style={metricLabel}>N invalid / skipped</div>
                <div style={{ ...metricValue, color: nInvalid > 0 ? "#a32d2d" : "var(--text-primary)" }}>{nInvalid}</div>
              </div>
            </div>
          </div>

          <div style={{ borderTop: "0.5px solid var(--border)", paddingTop: "1.25rem" }}>
            <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text-secondary)", marginBottom: 8 }}>
              LLM vs Developer consensus
            </div>
            {nLLMValid === 0 ? (
              <div style={{ fontSize: 13, color: "var(--text-muted)", padding: "1rem", background: "var(--surface-1)", borderRadius: "var(--radius)", border: "0.5px solid var(--border)" }}>
                Chưa có dòng nào đủ cả LLM output lẫn consensus label. Điền thêm ở tab Data entry.
              </div>
            ) : (
              <>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12, marginBottom: 12 }}>
                  <KappaGauge value={overallLD} label="Overall Kappa (LLM vs Dev)" />
                  {COMPONENTS.map(c => (
                    <KappaGauge key={c} value={ldKappas[c]} label={`${c} Kappa (LLM vs Dev)`} />
                  ))}
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 10 }}>
                  <div style={metricCard}>
                    <div style={metricLabel}>Raw agreement (LLM)</div>
                    <div style={metricValue}>{ldRaw !== null ? `${(ldRaw * 100).toFixed(1)}%` : "—"}</div>
                  </div>
                  <div style={metricCard}>
                    <div style={metricLabel}>N valid (LLM)</div>
                    <div style={metricValue}>{nLLMValid}</div>
                  </div>
                </div>
              </>
            )}
          </div>

          <div style={{ borderTop: "0.5px solid var(--border)", paddingTop: "1.25rem", marginTop: "1.25rem" }}>
            <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text-secondary)", marginBottom: 8 }}>
              Label distribution (human annotations, tất cả components)
            </div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {LABELS.map(l => {
                const count = hhDist[l] || 0;
                const pct = ((count / hhTotal) * 100).toFixed(1);
                const c = LABEL_COLORS[l];
                return (
                  <div key={l} style={{ background: c.bg, border: `1px solid ${c.border}`, borderRadius: 8, padding: "8px 14px", minWidth: 100 }}>
                    <div style={{ fontSize: 12, color: c.text, fontWeight: 500 }}>{l}</div>
                    <div style={{ fontSize: 20, fontWeight: 500, color: c.text }}>{count}</div>
                    <div style={{ fontSize: 11, color: c.text, opacity: 0.8 }}>{pct}%</div>
                  </div>
                );
              })}
            </div>
            {hhTotal > 1 && (
              <div style={{ marginTop: 12 }}>
                <div style={{ height: 10, borderRadius: 5, overflow: "hidden", display: "flex" }}>
                  {LABELS.map(l => {
                    const pct = ((hhDist[l] || 0) / hhTotal) * 100;
                    return <div key={l} style={{ width: `${pct}%`, background: LABEL_COLORS[l].border, transition: "width 0.3s" }} />;
                  })}
                </div>
                <div style={{ display: "flex", gap: 12, marginTop: 6 }}>
                  {LABELS.map(l => (
                    <span key={l} style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11, color: "var(--text-secondary)" }}>
                      <span style={{ width: 10, height: 10, borderRadius: 2, background: LABEL_COLORS[l].border, display: "inline-block" }} />
                      {l}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === "summary" && (
        <div>
          <p style={{ fontSize: 12, color: "var(--text-secondary)", margin: "0 0 1rem" }}>
            Bảng summary.csv — copy nội dung này để điền vào file.
          </p>
          <SummaryTable
            hhKappas={hhKappas} ldKappas={ldKappas}
            overallHH={overallHH} overallLD={overallLD}
            hhRaw={hhRaw} ldRaw={ldRaw}
            nValid={nValid} nLLMValid={nLLMValid}
            nInvalid={nInvalid}
            hhDist={hhDist}
          />
          <div style={{ marginTop: "1.25rem", padding: "12px 14px", background: "var(--surface-1)", borderRadius: "var(--radius)", border: "0.5px solid var(--border)" }}>
            <div style={{ fontSize: 12, fontWeight: 500, color: "var(--text-secondary)", marginBottom: 6 }}>Quyết định pilot</div>
            <DecisionBox overallHH={overallHH} overallLD={overallLD} nValid={nValid} nLLMValid={nLLMValid} />
          </div>
        </div>
      )}
    </div>
  );
}

function SummaryTable({ hhKappas, ldKappas, overallHH, overallLD, hhRaw, ldRaw, nValid, nLLMValid, nInvalid, hhDist }) {
  const rows = [
    { metric: "Human-Human Kappa (Overall)", value: overallHH, n: nValid, type: "kappa" },
    { metric: "Human-Human Kappa (OB)", value: hhKappas.OB, n: nValid, type: "kappa" },
    { metric: "Human-Human Kappa (EB)", value: hhKappas.EB, n: nValid, type: "kappa" },
    { metric: "Human-Human Kappa (S2R)", value: hhKappas.S2R, n: nValid, type: "kappa" },
    { metric: "LLM-vs-Developer Kappa (Overall)", value: overallLD, n: nLLMValid, type: "kappa" },
    { metric: "LLM-vs-Developer Kappa (OB)", value: ldKappas.OB, n: nLLMValid, type: "kappa" },
    { metric: "LLM-vs-Developer Kappa (EB)", value: ldKappas.EB, n: nLLMValid, type: "kappa" },
    { metric: "LLM-vs-Developer Kappa (S2R)", value: ldKappas.S2R, n: nLLMValid, type: "kappa" },
    { metric: "Raw agreement (H-H)", value: hhRaw, n: nValid, type: "pct" },
    { metric: "Raw agreement (LLM vs Dev)", value: ldRaw, n: nLLMValid, type: "pct" },
    { metric: "N valid (H-H)", value: nValid, n: null, type: "count" },
    { metric: "N valid (LLM)", value: nLLMValid, n: null, type: "count" },
    { metric: "N invalid / skipped", value: nInvalid, n: null, type: "count" },
  ];

  const fmt = (v, type) => {
    if (v === null || v === undefined) return "—";
    if (type === "kappa") return v.toFixed(4);
    if (type === "pct") return `${(v * 100).toFixed(2)}%`;
    return String(v);
  };

  const decision = (v, type) => {
    if (type !== "kappa" || v === null) return "—";
    return v >= 0.7 ? "PASS ✓" : "FAIL ✗";
  };

  const decColor = (v, type) => {
    if (type !== "kappa" || v === null) return "var(--text-muted)";
    return v >= 0.7 ? "#3b6d11" : "#a32d2d";
  };

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
        <thead>
          <tr style={{ background: "var(--surface-1)" }}>
            {["Metric", "Value", "N valid", "Decision"].map(h => (
              <th key={h} style={{ ...th, textAlign: h === "Value" || h === "N valid" || h === "Decision" ? "right" : "left" }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} style={{ background: i % 2 === 0 ? "var(--surface-2)" : "var(--surface-1)" }}>
              <td style={{ ...td, color: "var(--text-secondary)" }}>{row.metric}</td>
              <td style={{ ...td, textAlign: "right", fontWeight: 500 }}>{fmt(row.value, row.type)}</td>
              <td style={{ ...td, textAlign: "right", color: "var(--text-muted)" }}>{row.n ?? "—"}</td>
              <td style={{ ...td, textAlign: "right", fontWeight: 500, color: decColor(row.value, row.type) }}>
                {decision(row.value, row.type)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function DecisionBox({ overallHH, overallLD, nValid, nLLMValid }) {
  const lines = [];
  if (overallHH === null || nValid < 2) {
    lines.push({ text: "Chưa đủ dữ liệu để đánh giá IAA (H-H). Cần ít nhất 2 dòng hợp lệ.", color: "var(--text-muted)" });
  } else if (overallHH >= 0.7) {
    lines.push({ text: `IAA (H-H) = ${overallHH.toFixed(3)} ≥ 0.70 → ĐẠT. Có thể chuyển sang full experiment.`, color: "#3b6d11" });
  } else {
    lines.push({ text: `IAA (H-H) = ${overallHH.toFixed(3)} < 0.70 → KHÔNG ĐẠT. Dừng lại, báo Huy, không chạy full experiment.`, color: "#a32d2d" });
  }

  if (overallLD === null || nLLMValid < 2) {
    lines.push({ text: "Chưa đủ dữ liệu để đánh giá LLM vs Developer Kappa.", color: "var(--text-muted)" });
  } else if (overallLD >= 0.7) {
    lines.push({ text: `LLM Kappa = ${overallLD.toFixed(3)} ≥ 0.70 → ĐẠT. LLM chạy ổn như quality gate.`, color: "#3b6d11" });
  } else {
    lines.push({ text: `LLM Kappa = ${overallLD.toFixed(3)} < 0.70 → KHÔNG ĐẠT. Ghi INVALID và báo Huy.`, color: "#a32d2d" });
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      {lines.map((l, i) => (
        <div key={i} style={{ fontSize: 12, color: l.color, display: "flex", gap: 6, alignItems: "flex-start" }}>
          <i className={`ti ti-${l.color === "#3b6d11" ? "check" : l.color === "#a32d2d" ? "alert-triangle" : "info-circle"}`}
            aria-hidden="true" style={{ marginTop: 1, flexShrink: 0 }} />
          {l.text}
        </div>
      ))}
    </div>
  );
}

const th = {
  padding: "6px 8px", textAlign: "left", fontSize: 11, fontWeight: 500,
  color: "var(--text-secondary)", border: "0.5px solid var(--border)", whiteSpace: "nowrap",
};

const td = {
  padding: "5px 8px", border: "0.5px solid var(--border)", verticalAlign: "middle", fontSize: 12,
};

const metricCard = {
  background: "var(--surface-1)", borderRadius: "var(--radius)", padding: "10px 14px",
  border: "0.5px solid var(--border)",
};

const metricLabel = { fontSize: 11, color: "var(--text-secondary)", marginBottom: 4 };
const metricValue = { fontSize: 20, fontWeight: 500, color: "var(--text-primary)" };
