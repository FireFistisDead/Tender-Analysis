import React from "react";

const features = [
  {
    icon: "📄",
    title: "Smart PDF Extraction",
    desc: "Hybrid OCR + native text extraction handles both digital and scanned tender documents with page-level traceability.",
  },
  {
    icon: "🤖",
    title: "RAG-Powered Analysis",
    desc: "Retrieval-Augmented Generation ensures accurate, grounded analysis by referencing the actual tender text — no hallucinations.",
  },
  {
    icon: "🎯",
    title: "SDG Gap Detection",
    desc: "Automatically identifies missing sustainability requirements against all SDG 11 and SDG 12 targets with severity ratings.",
  },
  {
    icon: "📊",
    title: "Visual Scorecard",
    desc: "Instant sustainability scoring with interactive radar charts showing coverage across all SDG sub-targets.",
  },
  {
    icon: "💬",
    title: "Chat with Your Tender",
    desc: "Ask natural-language questions about any uploaded tender — 'Does this require ISO 14001?' — and get instant answers.",
  },
  {
    icon: "📋",
    title: "Actionable Recommendations",
    desc: "For every gap identified, get specific clause text suggestions that can be directly added to improve sustainability.",
  },
];

const sdg11Targets = ["11.1 Housing", "11.2 Transport", "11.3 Urbanization", "11.5 Disaster Risk", "11.6 Environment", "11.7 Green Spaces", "11.b Resilience"];
const sdg12Targets = ["12.2 Resources", "12.4 Chemicals", "12.5 Waste Reduction", "12.6 Reporting", "12.7 Green Procurement", "12.8 Awareness", "12.c Fossil Fuels"];

export default function Home() {
  return (
    <main>
      {/* Hero */}
      <section className="hero" id="hero">
        <div className="hero-particles">
          {Array.from({ length: 20 }).map((_, i) => (
            <div
              key={i}
              className="particle"
              style={{
                left: `${Math.random() * 100}%`,
                animationDuration: `${8 + Math.random() * 12}s`,
                animationDelay: `${Math.random() * 5}s`,
                width: `${2 + Math.random() * 4}px`,
                height: `${2 + Math.random() * 4}px`,
              }}
            />
          ))}
        </div>
        <div className="hero-content">
          <div className="hero-badge">🌍 SDG 11 + SDG 12 Intelligence</div>
          <h1>
            Decode <span className="gradient-text">Sustainability</span> in
            Every Tender
          </h1>
          <p>
            Upload any government tender PDF. Our AI extracts environmental
            clauses, evaluates sustainability commitments, and identifies
            missing SDG requirements — in seconds.
          </p>
          <div className="hero-cta">
            <a href="/analyze" className="btn btn-primary btn-lg">
              🚀 Analyze Your Tender
            </a>
            <a href="#how-it-works" className="btn btn-secondary btn-lg">
              Learn More ↓
            </a>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="section" id="features">
        <div className="container">
          <div className="section-header">
            <h2>
              Why <span className="gradient-text">TenderGreen AI</span>?
            </h2>
            <p>
              Six powerful AI capabilities that transform how you evaluate
              tender sustainability.
            </p>
          </div>
          <div className="features-grid">
            {features.map((f, i) => (
              <div key={i} className="glass-card feature-card">
                <div className="feature-icon">{f.icon}</div>
                <h3>{f.title}</h3>
                <p>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="section" id="how-it-works">
        <div className="container">
          <div className="section-header">
            <h2>How It Works</h2>
            <p>Three simple steps to comprehensive sustainability analysis.</p>
          </div>
          <div className="steps-container">
            <div className="glass-card step-card">
              <div className="step-number">1</div>
              <h3>Upload PDF</h3>
              <p>
                Drag and drop your government tender document. We support native
                PDFs and scanned documents via OCR.
              </p>
            </div>
            <div className="glass-card step-card">
              <div className="step-number">2</div>
              <h3>AI Analyzes</h3>
              <p>
                Our RAG pipeline extracts text, indexes it, and runs deep
                analysis against SDG 11 &amp; 12 frameworks.
              </p>
            </div>
            <div className="glass-card step-card">
              <div className="step-number">3</div>
              <h3>Get Report</h3>
              <p>
                View your interactive sustainability dashboard with scores,
                clauses, gaps, and actionable recommendations.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* SDG Focus */}
      <section className="section" id="sdg-focus">
        <div className="container">
          <div className="section-header">
            <h2>
              Focused on <span className="gradient-text">What Matters</span>
            </h2>
            <p>
              Deep compliance analysis against two critical Sustainable
              Development Goals.
            </p>
          </div>
          <div className="sdg-grid">
            <div className="glass-card sdg-card">
              <div className="sdg-card-header">
                <div className="sdg-number sdg-11">11</div>
                <div>
                  <h3>Sustainable Cities &amp; Communities</h3>
                  <p style={{ fontSize: "0.8rem", color: "var(--text-tertiary)" }}>
                    Inclusive, safe, resilient, sustainable
                  </p>
                </div>
              </div>
              <p>
                Evaluates tenders for urban sustainability — from public
                transport and green spaces to disaster resilience and air
                quality management.
              </p>
              <div className="sdg-targets">
                {sdg11Targets.map((t, i) => (
                  <span key={i} className="sdg-target-tag">{t}</span>
                ))}
              </div>
            </div>
            <div className="glass-card sdg-card">
              <div className="sdg-card-header">
                <div className="sdg-number sdg-12">12</div>
                <div>
                  <h3>Responsible Consumption &amp; Production</h3>
                  <p style={{ fontSize: "0.8rem", color: "var(--text-tertiary)" }}>
                    Sustainable consumption and production patterns
                  </p>
                </div>
              </div>
              <p>
                Checks for responsible procurement practices — waste
                management, recycling, green standards compliance, and
                lifecycle costing.
              </p>
              <div className="sdg-targets">
                {sdg12Targets.map((t, i) => (
                  <span key={i} className="sdg-target-tag">{t}</span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="section" style={{ textAlign: "center" }}>
        <div className="container">
          <h2 style={{ marginBottom: "var(--space-md)" }}>
            Ready to analyze your first tender?
          </h2>
          <p
            style={{
              color: "var(--text-secondary)",
              marginBottom: "var(--space-xl)",
              fontSize: "1.05rem",
            }}
          >
            Upload a PDF and get results in under 60 seconds.
          </p>
          <a href="/analyze" className="btn btn-primary btn-lg">
            🌿 Get Started Free
          </a>
        </div>
      </section>
    </main>
  );
}
