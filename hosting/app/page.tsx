const styles = {
  root: {
    backgroundColor: "#0a0a0f",
    color: "#e2e8f0",
    minHeight: "100vh",
  } as React.CSSProperties,

  // ─── Nav ────────────────────────────────────────────────────────────────────
  nav: {
    position: "sticky" as const,
    top: 0,
    zIndex: 100,
    backgroundColor: "rgba(10,10,15,0.85)",
    backdropFilter: "blur(12px)",
    borderBottom: "1px solid rgba(139,92,246,0.2)",
    padding: "0 2rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    height: "60px",
  },
  navBrand: {
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    fontWeight: 700,
    fontSize: "1rem",
    color: "#c4b5fd",
    textDecoration: "none",
  },
  navLinks: {
    display: "flex",
    gap: "1.5rem",
    listStyle: "none",
    margin: 0,
    padding: 0,
  },
  navLink: {
    color: "#94a3b8",
    textDecoration: "none",
    fontSize: "0.875rem",
    transition: "color 0.2s",
  },

  // ─── Hero ───────────────────────────────────────────────────────────────────
  hero: {
    background:
      "radial-gradient(ellipse 80% 60% at 50% -10%, rgba(139,92,246,0.25) 0%, transparent 70%), #0a0a0f",
    textAlign: "center" as const,
    padding: "6rem 1.5rem 4rem",
  },
  heroBadge: {
    display: "inline-block",
    background: "rgba(139,92,246,0.15)",
    border: "1px solid rgba(139,92,246,0.4)",
    borderRadius: "999px",
    padding: "0.3rem 0.9rem",
    fontSize: "0.75rem",
    color: "#c4b5fd",
    marginBottom: "1.5rem",
    letterSpacing: "0.08em",
    textTransform: "uppercase" as const,
  },
  heroTitle: {
    fontSize: "clamp(2rem, 5vw, 3.5rem)",
    fontWeight: 800,
    lineHeight: 1.15,
    margin: "0 0 1rem",
    background: "linear-gradient(135deg, #e2e8f0 30%, #c4b5fd 100%)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    backgroundClip: "text",
  },
  heroTagline: {
    fontSize: "clamp(0.9rem, 2vw, 1.125rem)",
    color: "#94a3b8",
    maxWidth: "600px",
    margin: "0 auto 0.75rem",
    lineHeight: 1.7,
  },
  heroSub: {
    fontSize: "0.8rem",
    color: "#64748b",
    marginBottom: "2rem",
    fontStyle: "italic" as const,
  },
  heroCta: {
    display: "inline-flex",
    gap: "1rem",
    flexWrap: "wrap" as const,
    justifyContent: "center",
    marginBottom: "3rem",
  },
  btnPrimary: {
    display: "inline-block",
    background: "linear-gradient(135deg, #7c3aed, #5b21b6)",
    color: "#fff",
    padding: "0.7rem 1.6rem",
    borderRadius: "8px",
    textDecoration: "none",
    fontWeight: 600,
    fontSize: "0.9rem",
    boxShadow: "0 0 20px rgba(124,58,237,0.4)",
  },
  btnSecondary: {
    display: "inline-block",
    background: "rgba(255,255,255,0.05)",
    border: "1px solid rgba(255,255,255,0.15)",
    color: "#e2e8f0",
    padding: "0.7rem 1.6rem",
    borderRadius: "8px",
    textDecoration: "none",
    fontWeight: 600,
    fontSize: "0.9rem",
  },
  badgeRow: {
    display: "flex",
    gap: "0.5rem",
    justifyContent: "center",
    flexWrap: "wrap" as const,
  },
  badge: {
    height: "20px",
  },

  // ─── Sections ───────────────────────────────────────────────────────────────
  section: {
    maxWidth: "1100px",
    margin: "0 auto",
    padding: "4rem 1.5rem",
  },
  sectionTitle: {
    fontSize: "clamp(1.4rem, 3vw, 2rem)",
    fontWeight: 700,
    marginBottom: "0.5rem",
    color: "#e2e8f0",
  },
  sectionSubtitle: {
    color: "#64748b",
    marginBottom: "2.5rem",
    fontSize: "0.95rem",
  },
  divider: {
    borderColor: "rgba(139,92,246,0.15)",
    margin: 0,
  },

  // ─── Components grid ────────────────────────────────────────────────────────
  grid3: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
    gap: "1.5rem",
  },
  card: {
    background: "rgba(255,255,255,0.03)",
    border: "1px solid rgba(255,255,255,0.08)",
    borderRadius: "12px",
    padding: "1.75rem",
    transition: "border-color 0.2s",
  },
  cardIcon: {
    fontSize: "2rem",
    marginBottom: "0.75rem",
    display: "block",
  },
  cardTitle: {
    fontSize: "1.1rem",
    fontWeight: 700,
    marginBottom: "0.5rem",
    color: "#c4b5fd",
  },
  cardBody: {
    fontSize: "0.875rem",
    color: "#94a3b8",
    lineHeight: 1.7,
    margin: 0,
  },
  cardList: {
    margin: "0.75rem 0 0",
    padding: "0 0 0 1.1rem",
    color: "#94a3b8",
    fontSize: "0.8rem",
    lineHeight: 1.8,
  },

  // ─── Architecture diagram ───────────────────────────────────────────────────
  archBox: {
    background: "rgba(0,0,0,0.4)",
    border: "1px solid rgba(139,92,246,0.25)",
    borderRadius: "12px",
    padding: "2rem",
    overflowX: "auto" as const,
  },
  pre: {
    margin: 0,
    color: "#a5b4fc",
    fontSize: "0.78rem",
    lineHeight: 1.6,
    whiteSpace: "pre" as const,
    fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
  },

  // ─── Code block ─────────────────────────────────────────────────────────────
  codeBlock: {
    background: "rgba(0,0,0,0.5)",
    border: "1px solid rgba(255,255,255,0.08)",
    borderRadius: "10px",
    overflow: "hidden",
  },
  codeHeader: {
    background: "rgba(255,255,255,0.04)",
    borderBottom: "1px solid rgba(255,255,255,0.06)",
    padding: "0.5rem 1rem",
    display: "flex",
    gap: "0.4rem",
    alignItems: "center",
  },
  codeDot: (color: string) =>
    ({
      width: "10px",
      height: "10px",
      borderRadius: "50%",
      background: color,
    }) as React.CSSProperties,
  codeLabel: {
    marginLeft: "0.5rem",
    fontSize: "0.75rem",
    color: "#475569",
  },
  code: {
    display: "block",
    padding: "1.25rem 1.5rem",
    color: "#a5b4fc",
    fontSize: "0.82rem",
    lineHeight: 1.7,
    whiteSpace: "pre" as const,
    fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
    overflowX: "auto" as const,
  },

  // ─── Principles ─────────────────────────────────────────────────────────────
  principleGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
    gap: "1rem",
  },
  principleCard: {
    background: "rgba(139,92,246,0.06)",
    border: "1px solid rgba(139,92,246,0.2)",
    borderRadius: "10px",
    padding: "1.25rem",
  },
  principleTitle: {
    fontWeight: 700,
    color: "#c4b5fd",
    marginBottom: "0.3rem",
    fontSize: "0.95rem",
  },
  principleBody: {
    fontSize: "0.82rem",
    color: "#94a3b8",
    margin: 0,
    lineHeight: 1.6,
  },

  // ─── Governance table ───────────────────────────────────────────────────────
  table: {
    width: "100%",
    borderCollapse: "collapse" as const,
    fontSize: "0.875rem",
  },
  th: {
    background: "rgba(139,92,246,0.12)",
    color: "#c4b5fd",
    padding: "0.7rem 1rem",
    textAlign: "left" as const,
    borderBottom: "1px solid rgba(139,92,246,0.25)",
    fontWeight: 600,
  },
  td: {
    padding: "0.7rem 1rem",
    borderBottom: "1px solid rgba(255,255,255,0.06)",
    color: "#94a3b8",
    verticalAlign: "top" as const,
  },
  tdCode: {
    padding: "0.7rem 1rem",
    borderBottom: "1px solid rgba(255,255,255,0.06)",
    color: "#a5b4fc",
    fontFamily: "monospace",
    fontSize: "0.82rem",
    verticalAlign: "top" as const,
  },

  // ─── Footer ─────────────────────────────────────────────────────────────────
  footer: {
    borderTop: "1px solid rgba(255,255,255,0.06)",
    background: "rgba(0,0,0,0.3)",
    padding: "2.5rem 1.5rem",
    textAlign: "center" as const,
  },
  footerGrid: {
    maxWidth: "900px",
    margin: "0 auto 2rem",
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: "2rem",
    textAlign: "left" as const,
  },
  footerHeading: {
    color: "#c4b5fd",
    fontWeight: 700,
    marginBottom: "0.75rem",
    fontSize: "0.85rem",
    textTransform: "uppercase" as const,
    letterSpacing: "0.08em",
  },
  footerLinks: {
    listStyle: "none",
    margin: 0,
    padding: 0,
    display: "flex",
    flexDirection: "column" as const,
    gap: "0.4rem",
  },
  footerLink: {
    color: "#64748b",
    textDecoration: "none",
    fontSize: "0.85rem",
  },
  footerCopy: {
    color: "#334155",
    fontSize: "0.8rem",
    marginTop: "1rem",
  },
  footerTagline: {
    color: "#475569",
    fontStyle: "italic" as const,
    fontSize: "0.85rem",
    marginTop: "0.5rem",
  },
};

const ARCH_DIAGRAM = `┌─────────────────────────────────────────────────────────────────┐
│              NeuroLift Agent Solidarity Kit                      │
│          "The Layer Between the Model and the Agent"             │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │  RRT Advocate     │  │  NLT-OTOI        │  │  Sleepwalker  │ │
│  │  (Protective)     │◄─┤  (Constitutional)│◄─┤  (Continuity) │ │
│  │                   │  │                  │  │               │ │
│  │ • Crisis Detection│  │ • TOI Governance │  │ • Emotional   │ │
│  │ • Emergency       │  │ • OTOI Orchestr. │  │   State       │ │
│  │   Response        │  │ • Privacy Guard  │  │   Detection   │ │
│  │ • Tiered Alerts   │  │ • User Prefs     │  │ • Session     │ │
│  │ • Agency Preserv. │  │ • Multi-Agent    │  │   Continuity  │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                        Unified Core                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │  Supervisor AI    │  │  Component Comms │  │  State Manager│ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────────┘`;

const QUICK_START = `import asyncio
from unified_core.neurolift_foundation import create_foundation

async def main():
    # Initialize the Agent Solidarity Kit
    foundation = await create_foundation("user_001")

    # Assess emotional state via Sleepwalker Protocol
    assessment = await foundation.assess_emotional_state(
        "I'm feeling overwhelmed today",
        context={"mood": "anxious", "energy": "low"}
    )

    # Crisis support (if needed) via RRT Advocate
    crisis_response = await foundation.crisis_alert({
        "stress_level": "high",
        "indicators": ["overwhelmed", "panic"],
        "context": "work deadline pressure"
    })

    # Update preferences via NLT-OTOI
    await foundation.update_preferences({
        "toi_updates": {"crisis_response": {"privacy_level": "high"}}
    })

    status = await foundation.get_system_status()
    print(f"System Status: {status}")

asyncio.run(main())`;

export default function Page() {
  return (
    <div style={styles.root}>
      {/* ── Navigation ─────────────────────────────────────────────────────── */}
      <nav style={styles.nav}>
        <a
          href="https://github.com/NeuroLift-Technologies/solidarity-framework"
          style={styles.navBrand}
        >
          <span>⚡</span>
          <span>Solidarity Framework</span>
        </a>
        <ul style={styles.navLinks}>
          <li>
            <a href="#components" style={styles.navLink}>
              Components
            </a>
          </li>
          <li>
            <a href="#quickstart" style={styles.navLink}>
              Quick Start
            </a>
          </li>
          <li>
            <a href="#governance" style={styles.navLink}>
              Governance
            </a>
          </li>
          <li>
            <a
              href="https://github.com/NeuroLift-Technologies/solidarity-framework"
              style={styles.navLink}
            >
              GitHub ↗
            </a>
          </li>
        </ul>
      </nav>

      {/* ── Hero ───────────────────────────────────────────────────────────── */}
      <section style={styles.hero}>
        <div style={styles.heroBadge}>ORG-DEV-OTOI-1.0.0 · v2.0.0</div>
        <h1 style={styles.heroTitle}>
          NeuroLift Technologies&apos;
          <br />
          Agent Solidarity Kit
        </h1>
        <p style={styles.heroTagline}>
          The unified agent development framework — the layer between the model
          and the agent. Combining crisis intervention, interaction governance,
          and emotional continuity into one cohesive kit.
        </p>
        <p style={styles.heroSub}>
          &ldquo;Tech That Gets You, Nothing About Us Without Us, ElevAIte Your
          Mind&rdquo;
        </p>
        <div style={styles.heroCta}>
          <a
            href="https://github.com/NeuroLift-Technologies/solidarity-framework"
            style={styles.btnPrimary}
          >
            View on GitHub
          </a>
          <a href="#quickstart" style={styles.btnSecondary}>
            Quick Start →
          </a>
        </div>
        <div style={styles.badgeRow}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="https://img.shields.io/badge/License-Apache%202.0-blue.svg"
            alt="License Apache 2.0"
            style={styles.badge}
          />
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="https://img.shields.io/badge/python-3.10+-blue.svg"
            alt="Python 3.10+"
            style={styles.badge}
          />
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="https://img.shields.io/badge/governance-ORG--DEV--OTOI--1.0.0-green.svg"
            alt="OTOI Governance"
            style={styles.badge}
          />
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="https://img.shields.io/badge/status-Active%20Development-brightgreen.svg"
            alt="Status"
            style={styles.badge}
          />
        </div>
      </section>

      <hr style={styles.divider} />

      {/* ── Core Components ────────────────────────────────────────────────── */}
      <section id="components" style={styles.section}>
        <h2 style={styles.sectionTitle}>🔩 Core Components</h2>
        <p style={styles.sectionSubtitle}>
          Three specialized modules, unified into one foundational layer.
        </p>
        <div style={styles.grid3}>
          <div style={styles.card}>
            <span style={styles.cardIcon}>🚨</span>
            <div style={styles.cardTitle}>RRT Advocate</div>
            <p style={styles.cardBody}>
              Rapid Response Team for crisis intervention and immediate safety
              protocols. Detects distress signals and coordinates tiered
              emergency responses.
            </p>
            <ul style={styles.cardList}>
              <li>Real-time crisis detection</li>
              <li>Tiered alert escalation</li>
              <li>Agency preservation</li>
              <li>Emergency response coordination</li>
            </ul>
          </div>
          <div style={styles.card}>
            <span style={styles.cardIcon}>📋</span>
            <div style={styles.cardTitle}>NLT-OTOI Framework</div>
            <p style={styles.cardBody}>
              Orchestrated Terms of Interaction for governance, user preferences,
              and multi-agent coordination. The constitutional layer of every NLT
              agent.
            </p>
            <ul style={styles.cardList}>
              <li>TOI governance engine</li>
              <li>OTOI orchestration</li>
              <li>Privacy guardian</li>
              <li>Multi-agent coordination</li>
            </ul>
          </div>
          <div style={styles.card}>
            <span style={styles.cardIcon}>🌙</span>
            <div style={styles.cardTitle}>Sleepwalker Protocol (SWP)</div>
            <p style={styles.cardBody}>
              Emotional continuity governance for long-term safety across
              sessions. Detects and tracks emotional state to maintain coherent,
              compassionate interactions.
            </p>
            <ul style={styles.cardList}>
              <li>Emotional state detection</li>
              <li>Cross-session continuity</li>
              <li>Python &amp; TypeScript implementations</li>
              <li>Privacy-first design</li>
            </ul>
          </div>
        </div>
      </section>

      <hr style={styles.divider} />

      {/* ── Architecture ───────────────────────────────────────────────────── */}
      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>🏗️ Architecture</h2>
        <p style={styles.sectionSubtitle}>
          Every NLT agent must integrate this kit as its foundational layer.
        </p>
        <div style={styles.archBox}>
          <pre style={styles.pre}>{ARCH_DIAGRAM}</pre>
        </div>
        <div style={{ marginTop: "1.5rem", overflowX: "auto" }}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Component</th>
                <th style={styles.th}>Repository</th>
                <th style={styles.th}>Purpose</th>
              </tr>
            </thead>
            <tbody>
              {[
                {
                  name: "RRT Advocate",
                  repo: "NeuroLift-Technologies/rrt-advocate",
                  purpose: "Crisis intervention & safety",
                },
                {
                  name: "NLT-OTOI",
                  repo: "NeuroLift-Technologies/nlt-otoi",
                  purpose: "Interaction governance & orchestration",
                },
                {
                  name: "Sleepwalker",
                  repo: "NeuroLift-Technologies/sleepwalker",
                  purpose: "Emotional continuity across sessions",
                },
              ].map((row) => (
                <tr key={row.repo}>
                  <td style={{ ...styles.td, color: "#c4b5fd", fontWeight: 600 }}>
                    {row.name}
                  </td>
                  <td style={styles.tdCode}>
                    <a
                      href={`https://github.com/${row.repo}`}
                      style={{ color: "#a5b4fc", textDecoration: "none" }}
                    >
                      {row.repo}
                    </a>
                  </td>
                  <td style={styles.td}>{row.purpose}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <hr style={styles.divider} />

      {/* ── Quick Start ────────────────────────────────────────────────────── */}
      <section id="quickstart" style={styles.section}>
        <h2 style={styles.sectionTitle}>🚀 Quick Start</h2>
        <p style={styles.sectionSubtitle}>
          Get running in minutes. Requires Python 3.10+ and Node.js 18+.
        </p>

        {/* Installation steps */}
        <div style={{ marginBottom: "1.5rem" }}>
          <div style={styles.codeBlock}>
            <div style={styles.codeHeader}>
              <div style={styles.codeDot("#ff5f56")} />
              <div style={styles.codeDot("#ffbd2e")} />
              <div style={styles.codeDot("#27c93f")} />
              <span style={styles.codeLabel}>bash — installation</span>
            </div>
            <code style={styles.code}>{`git clone https://github.com/NeuroLift-Technologies/solidarity-framework.git
cd solidarity-framework
pip install -r requirements.txt`}</code>
          </div>
        </div>

        {/* Usage example */}
        <div style={styles.codeBlock}>
          <div style={styles.codeHeader}>
            <div style={styles.codeDot("#ff5f56")} />
            <div style={styles.codeDot("#ffbd2e")} />
            <div style={styles.codeDot("#27c93f")} />
            <span style={styles.codeLabel}>python — basic usage</span>
          </div>
          <code style={styles.code}>{QUICK_START}</code>
        </div>
      </section>

      <hr style={styles.divider} />

      {/* ── Solidarity Principles ──────────────────────────────────────────── */}
      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>🛡️ Solidarity Framework Principles</h2>
        <p style={styles.sectionSubtitle}>
          Six non-negotiable commitments that govern every NLT agent.
        </p>
        <div style={styles.principleGrid}>
          {[
            {
              title: "Transparency",
              body: "All agent actions are logged and fully auditable by humans at any time.",
            },
            {
              title: "Minimal Footprint",
              body: "Agents only modify what is strictly necessary to complete the requested task.",
            },
            {
              title: "Escalation Culture",
              body: "When in doubt, escalate to human authority. Guessing is never acceptable.",
            },
            {
              title: "Human Flourishing",
              body: "Technology serves people, not the other way around. People come first.",
            },
            {
              title: "Privacy First",
              body: "Local-only processing wherever possible. Minimal data collection by design.",
            },
            {
              title: "Agency Preservation",
              body: "User autonomy is never overridden. Consent and control always remain with the user.",
            },
          ].map((p) => (
            <div key={p.title} style={styles.principleCard}>
              <div style={styles.principleTitle}>{p.title}</div>
              <p style={styles.principleBody}>{p.body}</p>
            </div>
          ))}
        </div>
      </section>

      <hr style={styles.divider} />

      {/* ── Governance ─────────────────────────────────────────────────────── */}
      <section id="governance" style={styles.section}>
        <h2 style={styles.sectionTitle}>🔐 Governance (ORG-DEV-OTOI-1.0.0)</h2>
        <p style={styles.sectionSubtitle}>
          All NLT agents are bound by the Orchestrated Terms of Interaction
          contract.
        </p>
        <div style={styles.grid3}>
          <div style={styles.card}>
            <div style={styles.cardTitle}>For AI Agents</div>
            <p style={styles.cardBody}>Every coding agent must:</p>
            <ul style={styles.cardList}>
              <li>Read CLAUDE.md for repo context</li>
              <li>Read AGENTS.md for coordination</li>
              <li>Check docs/active-threads.md</li>
              <li>Self-register before starting work</li>
              <li>Follow commit format [AGENT] type(scope)</li>
              <li>Escalate when required</li>
            </ul>
          </div>
          <div style={styles.card}>
            <div style={styles.cardTitle}>Non-Negotiable Guardrails</div>
            <ul style={styles.cardList}>
              <li>No LLM provider lock-in</li>
              <li>No architecture decisions without approval</li>
              <li>No production deployments without human sign-off</li>
              <li>No credential storage in VCS</li>
              <li>No external integrations without approval</li>
              <li>No OTOI self-amendment</li>
            </ul>
          </div>
          <div style={styles.card}>
            <div style={styles.cardTitle}>Escalation Authority</div>
            <p style={styles.cardBody}>
              Escalate to{" "}
              <strong style={{ color: "#c4b5fd" }}>
                Joshua W. Dorsey, Sr.
              </strong>{" "}
              when scope is unclear, a blocker exists, an architectural decision
              is needed, or an ethical concern arises.
            </p>
            <ul style={styles.cardList}>
              <li>info@neuroliftsolutions.com</li>
              <li>Use templates/escalation.md</li>
              <li>Or file a GitHub Issue</li>
            </ul>
          </div>
        </div>
      </section>

      <hr style={styles.divider} />

      {/* ── Privacy & Security ─────────────────────────────────────────────── */}
      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>🔒 Privacy &amp; Security</h2>
        <p style={styles.sectionSubtitle}>
          Privacy-first design, encrypted storage, minimal data collection.
        </p>
        <div style={styles.grid3}>
          {[
            {
              icon: "🏠",
              title: "Local Processing",
              body: "Core functionality operates locally without external dependencies wherever possible.",
            },
            {
              icon: "🔐",
              title: "Encrypted Storage",
              body: "All user data is encrypted at rest and in transit. Zero plaintext sensitive data.",
            },
            {
              icon: "📊",
              title: "Minimal Data Collection",
              body: "Only essential data is collected for functionality. Nothing more, nothing less.",
            },
            {
              icon: "🎛️",
              title: "User Control",
              body: "Complete user control over data sharing and retention. Opt-out at any time.",
            },
            {
              icon: "📋",
              title: "Audit Trail",
              body: "All agent actions are logged with full audit trails for accountability.",
            },
            {
              icon: "🛡️",
              title: "Vulnerability Disclosure",
              body: "Responsible disclosure policy in SECURITY.md. Report issues privately first.",
            },
          ].map((item) => (
            <div key={item.title} style={styles.card}>
              <span style={styles.cardIcon}>{item.icon}</span>
              <div style={styles.cardTitle}>{item.title}</div>
              <p style={styles.cardBody}>{item.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Footer ─────────────────────────────────────────────────────────── */}
      <footer style={styles.footer}>
        <div style={styles.footerGrid}>
          <div>
            <div style={styles.footerHeading}>Framework</div>
            <ul style={styles.footerLinks}>
              {[
                {
                  label: "GitHub Repository",
                  href: "https://github.com/NeuroLift-Technologies/solidarity-framework",
                },
                {
                  label: "README",
                  href: "https://github.com/NeuroLift-Technologies/solidarity-framework#readme",
                },
                {
                  label: "Releases",
                  href: "https://github.com/NeuroLift-Technologies/solidarity-framework/releases",
                },
                {
                  label: "License (Apache 2.0)",
                  href: "https://github.com/NeuroLift-Technologies/solidarity-framework/blob/main/LICENSE",
                },
              ].map((l) => (
                <li key={l.href}>
                  <a href={l.href} style={styles.footerLink}>
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <div style={styles.footerHeading}>Components</div>
            <ul style={styles.footerLinks}>
              {[
                {
                  label: "RRT Advocate",
                  href: "https://github.com/NeuroLift-Technologies/rrt-advocate",
                },
                {
                  label: "NLT-OTOI",
                  href: "https://github.com/NeuroLift-Technologies/nlt-otoi",
                },
                {
                  label: "Sleepwalker Protocol",
                  href: "https://github.com/NeuroLift-Technologies/sleepwalker",
                },
                {
                  label: "Unified Core",
                  href: "https://github.com/NeuroLift-Technologies/solidarity-framework/tree/main/unified-core",
                },
              ].map((l) => (
                <li key={l.href}>
                  <a href={l.href} style={styles.footerLink}>
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <div style={styles.footerHeading}>Community</div>
            <ul style={styles.footerLinks}>
              {[
                {
                  label: "Contributing",
                  href: "https://github.com/NeuroLift-Technologies/solidarity-framework/blob/main/CONTRIBUTING.md",
                },
                {
                  label: "Code of Conduct",
                  href: "https://github.com/NeuroLift-Technologies/solidarity-framework/blob/main/CODE_OF_CONDUCT.md",
                },
                {
                  label: "Security Policy",
                  href: "https://github.com/NeuroLift-Technologies/solidarity-framework/blob/main/SECURITY.md",
                },
                {
                  label: "Support",
                  href: "https://github.com/NeuroLift-Technologies/solidarity-framework/blob/main/SUPPORT.md",
                },
              ].map((l) => (
                <li key={l.href}>
                  <a href={l.href} style={styles.footerLink}>
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <div style={styles.footerHeading}>Contact</div>
            <ul style={styles.footerLinks}>
              <li>
                <a
                  href="mailto:info@neuroliftsolutions.com"
                  style={styles.footerLink}
                >
                  info@neuroliftsolutions.com
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/NeuroLift-Technologies/solidarity-framework/issues"
                  style={styles.footerLink}
                >
                  Open an Issue
                </a>
              </li>
              <li>
                <a href="https://elevaitionfoundation.org" style={styles.footerLink}>
                  HAIEF ↗
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div style={{ borderTop: "1px solid rgba(255,255,255,0.06)", paddingTop: "1.5rem" }}>
          <p style={styles.footerCopy}>
            © {new Date().getFullYear()} NeuroLift Technologies · Apache 2.0
            License · Framework v2.0.0 · Governance ORG-DEV-OTOI-1.0.0
          </p>
          <p style={styles.footerTagline}>
            &ldquo;Tech That Gets You, Nothing About Us Without Us, ElevAIte
            Your Mind&rdquo;
          </p>
        </div>
      </footer>
    </div>
  );
}
