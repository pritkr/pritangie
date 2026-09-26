#import "modern-cv/lib.typ": *

#show: resume.with(
  author: (
    firstname: "Prit Kumar",
    lastname: "",
    email: "pritform@gmail.com",
    github: "pritkr",
    linkedin: "prit-kumar",
    address: "Bihar, India",
    positions: (
      "Systems & AI Security Developer",
      "Open-Source Builder"
    )
  ),
  profile-picture: none,
  date: datetime.today().display("[month repr:long] [day], [year]"),
  accent-color: rgb("#1e40af"),
  font: ("EB Garamond", "Georgia", "Times New Roman", "Liberation Serif"),
  header-font: ("EB Garamond", "Georgia", "Times New Roman"),
  show-footer: false,
  paper-size: "a4"
)

#set text(fill: rgb("#191919"))

#let dark-ink = rgb("#141414")

#let resume-entry(
  title: none,
  location: "",
  location-link: none,
  date: "",
  description: "",
  title-link: none,
) = {
  let title-content = if title-link != none {
    link(title-link)[#title]
  } else {
    title
  }
  let location-content = if location-link != none {
    link(location-link)[#location]
  } else {
    location
  }
  block(above: 1em, below: 0.65em)[
    #pad[
      #justified-header(title-content, location-content)
      #if description != "" or date != "" [
        #block[
          #box(width: 1fr)[
            #align(left)[
              #text(fill: dark-ink, size: 11pt, weight: "regular")[
                #description
              ]
            ]
          ]
          #box(width: 1fr)[
            #align(right)[
              #text(fill: dark-ink, size: 11pt, weight: "regular")[#date]
            ]
          ]
        ]
      ]
    ]
  ]
}

#let resume-item(body) = {
  set text(
    size: 11pt,
    style: "normal",
    weight: "regular",
    fill: dark-ink,
  )
  set block(
    above: 0.75em,
    below: 1.25em,
  )
  set par(leading: 0.65em)
  block(above: 0.5em)[
    #body
  ]
}

= Summary
Systems and open-source developer (B.Tech CSE) building privacy-respecting platforms, local-first distributed architectures, and AI security runtime tooling. Maintainer of *Predirect* (270+ ★ on GitHub) and creator of *sentinel-mcp* (Go capability proxy for Model Context Protocol) and *dhvani-eval* (vernacular voice AI eval harness). Founding tech lead at *Bodhya* FOSS community (aligned with FOSS United & Samagata) mentoring engineering students across Bihar.

= Featured Engineering Projects

#resume-entry(
  title: "sentinel-mcp — Model Context Protocol Security Proxy",
  location: "github.com/pritkr/sentinel-mcp",
  location-link: "https://github.com/pritkr/sentinel-mcp",
  title-link: "https://github.com/pritkr/sentinel-mcp",
  date: "2026",
  description: "Creator & Lead Developer (Go · Systems & AI Security)"
)
#resume-item[
  - Engineered a zero-overhead (sub-0.2ms latency) capability-gated security reverse proxy in Go for Model Context Protocol (MCP) JSON-RPC execution, sandboxing LLM agent actions.
  - Implemented real-time taint analysis and Shannon entropy anomaly detection on tool responses to intercept credential leakage (AWS tokens, private keys) before context ingestion.
  - Designed declarative capability policies enforcing directory path whitelisting and SSRF egress blocking (blocking RFC 1918 private subnets and 169.254.169.254 cloud metadata).
]

#resume-entry(
  title: "dhvani-eval — Indic Voice AI & Telephony Benchmark Suite",
  location: "github.com/pritkr/dhvani-eval",
  location-link: "https://github.com/pritkr/dhvani-eval",
  title-link: "https://github.com/pritkr/dhvani-eval",
  date: "2026",
  description: "Creator & Researcher (Python · Speech AI & Audio DSP)"
)
#resume-item[
  - Architected an open-source evaluation suite for Indic voice models, benchmarking Devanagari Unicode normalization, character/word error rates (CER/WER), and code-mixed Hinglish alignment.
  - Built an acoustic telephony degradation engine simulating rural Indian network conditions (8kHz ITU-T bandpass downsampling, burst packet jitter via Gilbert-Elliott modeling, and ambient noise injection).
  - Measured streaming voice turnaround metrics (Time to First Token [TTFT], End of Utterance [EOU]) to quantify latency and hallucination degradation under 2G bandwidth.
]

#resume-entry(
  title: "pebble-sync — Offline-First CRDT Sync Engine",
  location: "github.com/pritkr/pebble-sync",
  location-link: "https://github.com/pritkr/pebble-sync",
  title-link: "https://github.com/pritkr/pebble-sync",
  date: "2026",
  description: "Creator (TypeScript · Distributed Systems)"
)
#resume-item[
  - Developed a zero-dependency state-based CRDT engine supporting hierarchical documents, OR-Sets, and LWW-Registers with mathematically proven eventual consistency convergence.
  - Implemented Merkle clock differential replication, slashing wire transfer payloads by >80% over high-latency connections compared to full-state replication.
  - Integrated tamper-evident SHA-256 cryptographic hash chains and signature verification for zero-trust edge/mesh synchronization.
]

#resume-entry(
  title: "Predirect — Privacy Browser Extension",
  location: "github.com/pritkr/predirect",
  location-link: "https://github.com/pritkr/predirect",
  title-link: "https://github.com/pritkr/predirect",
  date: "Nov 2023 - Present",
  description: "Maintainer & Lead Developer (270+ ★ on GitHub · GPL-3.0)"
)
#resume-item[
  - Manifest V3 browser extension redirecting ~30 tracked sites (YouTube, X, Reddit, Google, Instagram, TikTok) to privacy-friendly frontends (Piped, Nitter, Redlib, SearXNG).
  - Minimal-permission architecture published on Chrome Web Store, Firefox Add-ons (incl. Android), and Microsoft Edge.
  - Automated instance health checking and sync workflows maintained via GitHub Actions (`pritkr/instances`).
]

#resume-entry(
  title: "JanSahay — Rural Welfare Eligibility Platform",
  location: "jansahay.pages.dev",
  location-link: "https://jansahay.pages.dev",
  title-link: "https://jansahay.pages.dev",
  date: "Sep 2026",
  description: "Built with Team Tejas at TEJAS India Hackathon 2026 (GEC Sheikhpura)"
)
#resume-item[
  - Built an offline-first welfare entitlement assistant designed for rural citizens in Bihar with Devanagari TTS and 48px touch targets.
  - Engineered a deterministic rule engine decoupled from LLMs to ensure zero hallucination on benefit eligibility decisions.
  - Monorepo deployed on Cloudflare Workers and React PWA with local sahayak verification workflows.
]

#resume-entry(
  title: "chaind-cli — Sovereign AI Agent Daemon",
  location: "github.com/fossism/chaind-cli",
  location-link: "https://github.com/fossism/chaind-cli",
  title-link: "https://github.com/fossism/chaind-cli",
  date: "2024 - Present",
  description: "Lead Developer (Go)"
)
#resume-item[
  - Headless Go daemon bridging messaging apps (WhatsApp, Matrix, Telegram) directly to local AI agents via permission-gated Unix sockets.
  - Designed for secure, zero-cloud interaction with self-hosted LLMs without exposing open network ports.
]

= Experience & Community
#resume-entry(
  title: "Bodhya FOSS Community",
  location: "bodhya.net — Bihar, India",
  location-link: "https://bodhya.net",
  title-link: "https://bodhya.net",
  date: "Jan 2026 - Present",
  description: "Tech & Programs Lead — Founding Core Team"
)
#resume-item[
  - Lead tech and programs for a FOSS community aligned with FOSS United & Samagata linking tier-2/3 college students with open-source mentors, workshops, and real projects.
  - Built production tooling including automated certificate generators, event portals, and Frappe/Listmonk sync integrations (`listbrew`).
]

#resume-entry(
  title: "Navprayas — Student-Run Non-Profit Society",
  location: "navprayas.in — Gaya, Bihar",
  location-link: "https://navprayas.in",
  title-link: "https://navprayas.in",
  date: "May 2025 - Present",
  description: "Team Lead — Website, Database & Operations"
)
#resume-item[
  - Directed database operations and registration platforms for educational initiatives serving 15,000+ rural students.
  - Handled online registration transitions with Razorpay gateway and anchored annual felicitation ceremonies.
]

= Technical Skills
#resume-skill-item(
  "Languages",
  ("Go", "Python", "TypeScript", "JavaScript", "C", "C++", "Bash", "SQL")
)
#resume-skill-item(
  "Systems & AI",
  ("Model Context Protocol (MCP)", "Unix Sockets & IPC", "AST Program Analysis", "Speech DSP & Telephony", "CRDTs & Merkle DAGs")
)
#resume-skill-item(
  "Web & Edge",
  ("React", "Astro", "Tailwind CSS", "Node.js", "Cloudflare Workers", "Web Crypto", "PWA")
)
#resume-skill-item(
  "Tools & Infra",
  ("Linux (Arch)", "Git/GitHub", "Docker", "GitHub Actions CI/CD", "Nginx", "PostgreSQL", "Supabase")
)

= Education
#resume-entry(
  title: "Government Engineering College (GEC), Sheikhpura",
  location: "Sheikhpura, Bihar, India",
  date: "2024 - 2028",
  description: "B.Tech in Computer Science & Engineering — Bihar Engineering University (BEU)"
)
