"use client";

import React, { useState, useRef, useCallback, useEffect } from "react";
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, ResponsiveContainer, Tooltip,
} from "recharts";
import { uploadTender, getStatus, getAnalysis, chatWithTender } from "@/lib/api";
import type {
  AnalysisResult, StatusResponse, ChatMessage,
  EnvironmentalClause, MissingRequirement,
} from "@/lib/types";

/* ── helpers ─────────────────────────────────────── */

function strengthIcon(s: string) {
  if (s === "strong") return "✅";
  if (s === "moderate") return "🔵";
  return "⚠️";
}

function severityLabel(s: string) {
  if (s === "high") return "🔴 HIGH";
  if (s === "medium") return "🟡 MEDIUM";
  return "🔵 LOW";
}

function ScoreRing({ score, color, label }: { score: number; color: string; label: string }) {
  const r = 48, c = 2 * Math.PI * r;
  const offset = c - (score / 100) * c;
  return (
    <div className="score-card glass-card">
      <div className="score-ring-container">
        <svg className="score-ring" width="120" height="120" viewBox="0 0 120 120">
          <circle className="score-ring-bg" cx="60" cy="60" r={r} />
          <circle
            className="score-ring-fill"
            cx="60" cy="60" r={r}
            stroke={color}
            strokeDasharray={c}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="score-value" style={{ color }}>{score}%</div>
      </div>
      <div className="score-label">{label}</div>
    </div>
  );
}

/* ── main component ──────────────────────────────── */

export default function AnalyzePage() {
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  /* ── upload & poll ── */

  const handleUpload = useCallback(async (f: File) => {
    setFile(f);
    setError("");
    setResult(null);
    setChatMessages([]);
    try {
      const res = await uploadTender(f);
      setStatus({ upload_id: res.upload_id, status: "processing", progress: 10, message: "Uploading..." });
      pollStatus(res.upload_id);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Upload failed");
    }
  }, []);

  async function pollStatus(id: string) {
    const poll = async () => {
      try {
        const s: StatusResponse = await getStatus(id);
        setStatus(s);
        if (s.status === "complete") {
          const a: AnalysisResult = await getAnalysis(id);
          setResult(a);
        } else if (s.status === "error") {
          setError(s.message);
        } else {
          setTimeout(poll, 2000);
        }
      } catch {
        setTimeout(poll, 3000);
      }
    };
    poll();
  }

  /* ── chat ── */

  async function handleChat() {
    if (!chatInput.trim() || !result) return;
    const q = chatInput.trim();
    setChatInput("");
    setChatMessages((m) => [...m, { role: "user", content: q }]);
    setChatLoading(true);
    try {
      const res = await chatWithTender(result.upload_id, q);
      setChatMessages((m) => [
        ...m,
        { role: "assistant", content: res.answer, source_pages: res.source_pages },
      ]);
    } catch {
      setChatMessages((m) => [...m, { role: "assistant", content: "Sorry, I couldn't process that question." }]);
    }
    setChatLoading(false);
  }

  /* ── drag & drop ── */

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const f = e.dataTransfer.files[0];
      if (f && f.type === "application/pdf") handleUpload(f);
      else setError("Please upload a PDF file.");
    },
    [handleUpload]
  );

  const onFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const f = e.target.files?.[0];
      if (f) handleUpload(f);
    },
    [handleUpload]
  );

  /* ── radar data ── */

  const radarData = result
    ? [
        { target: "11.1 Housing", value: getTargetCoverage(result, "11.1") },
        { target: "11.2 Transport", value: getTargetCoverage(result, "11.2") },
        { target: "11.5 Disaster", value: getTargetCoverage(result, "11.5") },
        { target: "11.6 Environ.", value: getTargetCoverage(result, "11.6") },
        { target: "11.7 Green Sp.", value: getTargetCoverage(result, "11.7") },
        { target: "12.2 Resources", value: getTargetCoverage(result, "12.2") },
        { target: "12.4 Chemicals", value: getTargetCoverage(result, "12.4") },
        { target: "12.5 Waste", value: getTargetCoverage(result, "12.5") },
        { target: "12.7 Procure.", value: getTargetCoverage(result, "12.7") },
        { target: "12.c Energy", value: getTargetCoverage(result, "12.c") },
      ]
    : [];

  /* ── RENDER ── */

  // Upload screen
  if (!result && !status) {
    return (
      <main className="upload-page">
        <div className="container" style={{ maxWidth: 720 }}>
          <div style={{ textAlign: "center", marginBottom: "var(--space-2xl)" }}>
            <h1 style={{ fontSize: "2rem", marginBottom: "var(--space-sm)" }}>
              <span className="gradient-text">Analyze</span> Your Tender
            </h1>
            <p style={{ color: "var(--text-secondary)" }}>
              Upload a government tender PDF to get an AI sustainability report.
            </p>
          </div>

          <div
            className={`upload-zone glass-card ${dragOver ? "drag-over" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
          >
            <div className="upload-icon">📄</div>
            <h3>Drag &amp; Drop your Tender PDF</h3>
            <p>or click to browse • PDF only • Max 50MB</p>
            <input
              ref={inputRef}
              type="file"
              accept=".pdf"
              style={{ display: "none" }}
              onChange={onFileSelect}
            />
          </div>

          {error && (
            <div
              style={{
                marginTop: "var(--space-lg)",
                padding: "var(--space-md)",
                background: "rgba(239,68,68,0.1)",
                borderRadius: "var(--radius-md)",
                color: "var(--color-danger)",
                textAlign: "center",
              }}
            >
              {error}
            </div>
          )}
        </div>
      </main>
    );
  }

  // Processing screen
  if (status && status.status === "processing") {
    return (
      <main className="upload-page">
        <div className="container" style={{ maxWidth: 600, textAlign: "center" }}>
          <div className="spinner" style={{ marginTop: 100 }} />
          <h2 style={{ marginTop: "var(--space-xl)" }}>
            Analyzing <span className="gradient-text">{file?.name}</span>
          </h2>
          <div className="progress-container" style={{ marginTop: "var(--space-xl)" }}>
            <div className="progress-bar-track">
              <div className="progress-bar-fill" style={{ width: `${status.progress}%` }} />
            </div>
            <div className="progress-text">
              <span>{status.message}</span>
              <span>{status.progress}%</span>
            </div>
          </div>
        </div>
      </main>
    );
  }

  // Error screen
  if (status && status.status === "error") {
    return (
      <main className="upload-page">
        <div className="container" style={{ maxWidth: 600, textAlign: "center", paddingTop: 120 }}>
          <div style={{ fontSize: "3rem" }}>❌</div>
          <h2 style={{ margin: "var(--space-lg) 0" }}>Analysis Failed</h2>
          <p style={{ color: "var(--text-secondary)" }}>{error || status.message}</p>
          <button className="btn btn-primary" style={{ marginTop: "var(--space-xl)" }} onClick={() => { setStatus(null); setResult(null); setError(""); }}>
            Try Again
          </button>
        </div>
      </main>
    );
  }

  // Results dashboard
  if (!result) return null;

  return (
    <main className="dashboard">
      <div className="container">
        {/* Header */}
        <div className="dashboard-header">
          <h1>
            📊 Sustainability Report:{" "}
            <span className="gradient-text">{result.filename}</span>
          </h1>
          <p>{result.total_pages} pages analyzed • Upload ID: {result.upload_id}</p>
        </div>

        {/* Score Cards */}
        <div className="score-grid">
          <ScoreRing score={result.overall_sustainability_score} color="#10b981" label="Overall Score" />
          <ScoreRing score={result.sdg11_score} color="#f59e0b" label="SDG 11 Score" />
          <ScoreRing score={result.sdg12_score} color="#b45309" label="SDG 12 Score" />
        </div>

        {/* Executive Summary */}
        {result.executive_summary && (
          <div className="panel">
            <div className="panel-header"><h2>📝 Executive Summary</h2></div>
            <div className="glass-card executive-summary">{result.executive_summary}</div>
          </div>
        )}

        {/* Environmental Clauses */}
        <div className="panel">
          <div className="panel-header">
            <h2>
              🔍 Environmental Clauses Found
              <span className="panel-count">({result.environmental_clauses.length})</span>
            </h2>
          </div>
          <div className="clause-list">
            {result.environmental_clauses.map((cl: EnvironmentalClause, i: number) => (
              <div key={i} className="glass-card clause-card">
                <div className={`clause-icon ${cl.strength}`}>{strengthIcon(cl.strength)}</div>
                <div className="clause-content">
                  <h4>{cl.category}</h4>
                  <p>{cl.clause_text}</p>
                  <div className="clause-meta">
                    <span>Page {cl.page}</span>
                    <span className={`badge badge-${cl.strength === "strong" ? "success" : cl.strength === "moderate" ? "info" : "warning"}`}>
                      {cl.strength}
                    </span>
                    {cl.sdg_alignment.map((s, j) => (
                      <span key={j} className="badge badge-info">SDG {s}</span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Missing Requirements */}
        <div className="panel">
          <div className="panel-header">
            <h2>
              ⚠️ Missing SDG Requirements
              <span className="panel-count">({result.missing_requirements.length})</span>
            </h2>
          </div>
          <div className="gap-list">
            {result.missing_requirements.map((m: MissingRequirement, i: number) => (
              <div key={i} className="glass-card gap-card">
                <div className={`gap-severity ${m.severity}`} />
                <div className="gap-content">
                  <h4>
                    {severityLabel(m.severity)} — SDG {m.sdg_target}: {m.target_name}
                  </h4>
                  <p>{m.gap}</p>
                  {m.recommendation && (
                    <div className="gap-recommendation">
                      💡 <strong>Recommendation:</strong> {m.recommendation}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* SDG Radar Chart */}
        <div className="panel">
          <div className="panel-header"><h2>📈 SDG Coverage Radar</h2></div>
          <div className="glass-card chart-container">
            <ResponsiveContainer width="100%" height={380}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(148,163,184,0.15)" />
                <PolarAngleAxis dataKey="target" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <PolarRadiusAxis domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 10 }} />
                <Tooltip />
                <Radar
                  name="Coverage %"
                  dataKey="value"
                  stroke="#10b981"
                  fill="#10b981"
                  fillOpacity={0.2}
                  strokeWidth={2}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recommendations */}
        {result.recommendations.length > 0 && (
          <div className="panel">
            <div className="panel-header"><h2>💡 Recommendations</h2></div>
            <div className="glass-card" style={{ padding: "var(--space-xl)" }}>
              <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "var(--space-md)" }}>
                {result.recommendations.map((r, i) => (
                  <li key={i} style={{ display: "flex", gap: "var(--space-sm)", alignItems: "flex-start", color: "var(--text-secondary)", fontSize: "0.9rem" }}>
                    <span style={{ color: "var(--accent-primary)", flexShrink: 0 }}>→</span>
                    {r}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Chat with Tender */}
        <div className="panel">
          <div className="panel-header"><h2>💬 Chat with Your Tender</h2></div>
          <div className="glass-card chat-container">
            <div className="chat-messages">
              {chatMessages.length === 0 && (
                <p style={{ color: "var(--text-tertiary)", textAlign: "center", padding: "var(--space-xl)" }}>
                  Ask any question about this tender...
                  <br />
                  <em style={{ fontSize: "0.8rem" }}>
                    e.g. &quot;Does this tender require ISO 14001?&quot;
                  </em>
                </p>
              )}
              {chatMessages.map((m, i) => (
                <div key={i} className={`chat-message ${m.role}`}>
                  {m.content}
                  {m.source_pages && m.source_pages.length > 0 && (
                    <div style={{ marginTop: 6, fontSize: "0.75rem", opacity: 0.7 }}>
                      📄 Sources: Page {m.source_pages.join(", ")}
                    </div>
                  )}
                </div>
              ))}
              {chatLoading && (
                <div className="chat-message assistant animate-pulse">Thinking...</div>
              )}
            </div>
            <div className="chat-input-container">
              <input
                className="chat-input"
                placeholder="Ask about this tender..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleChat()}
              />
              <button
                className="chat-send-btn"
                onClick={handleChat}
                disabled={chatLoading || !chatInput.trim()}
              >
                Send
              </button>
            </div>
          </div>
        </div>

        {/* Analyze Another */}
        <div style={{ textAlign: "center", padding: "var(--space-2xl) 0" }}>
          <button className="btn btn-secondary btn-lg" onClick={() => { setStatus(null); setResult(null); setFile(null); setError(""); setChatMessages([]); }}>
            📄 Analyze Another Tender
          </button>
        </div>
      </div>
    </main>
  );
}

/* ── utility: estimate target coverage from analysis data ── */

function getTargetCoverage(r: AnalysisResult, targetId: string): number {
  // Check if any clause aligns with this target
  const hasClause = r.environmental_clauses.some((c) =>
    c.sdg_alignment.some((a) => a === targetId)
  );
  // Check if it's in missing requirements
  const isMissing = r.missing_requirements.some(
    (m) => m.sdg_target === targetId
  );
  const missingSeverity = r.missing_requirements.find(
    (m) => m.sdg_target === targetId
  )?.severity;

  if (hasClause && !isMissing) return 85 + Math.random() * 15;
  if (hasClause && isMissing) return 40 + Math.random() * 20;
  if (!hasClause && isMissing && missingSeverity === "high") return 5 + Math.random() * 15;
  if (!hasClause && isMissing) return 20 + Math.random() * 15;
  return 50;
}
