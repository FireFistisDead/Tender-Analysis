import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Tender Sustainability Analyzer | AI-Powered SDG Compliance",
  description:
    "Upload government tender PDFs and get AI-powered sustainability analysis against SDG 11 (Sustainable Cities) and SDG 12 (Responsible Consumption). Extract environmental clauses, identify gaps, and generate compliance reports.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <nav className="navbar">
          <div className="navbar-inner">
            <a href="/" className="navbar-brand">
              <div className="navbar-brand-icon">🌿</div>
              TenderGreen AI
            </a>
            <ul className="navbar-links">
              <li><a href="/#features">Features</a></li>
              <li><a href="/#how-it-works">How It Works</a></li>
              <li><a href="/#sdg-focus">SDG Focus</a></li>
              <li>
                <a href="/analyze" className="btn btn-primary" style={{ padding: '8px 20px', fontSize: '0.85rem' }}>
                  Analyze Tender
                </a>
              </li>
            </ul>
          </div>
        </nav>
        {children}
        <footer className="footer">
          <div className="container">
            <p>© 2025 TenderGreen AI — Powered by SDG 11 & SDG 12 Intelligence</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
