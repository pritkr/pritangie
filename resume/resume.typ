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
      "Open-Source Developer",
      "Privacy Advocate"
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
Open-source developer and B.Tech CSE student building software that respects privacy and freedom. Maintainer of *Predirect* (Manifest V3 browser extension with *270+ ★* on GitHub) redirecting ~30 surveilled platforms to privacy-friendly frontends, published on Chrome, Firefox, and Edge. Lead of tech & programs at *Bodhya* FOSS community (aligned with FOSS United / Samagata) bringing tech opportunities, mentorship, and workshops to engineering students in Bihar.

= Projects
#resume-entry(
  title: "Predirect — Privacy Browser Extension",
  location: "github.com/pritkr/predirect",
  location-link: "https://github.com/pritkr/predirect",
  title-link: "https://github.com/pritkr/predirect",
  date: "Nov 2023 - Present",
  description: "Maintainer & Lead Developer (270+ ★ on GitHub · GPL-3.0)"
)
#resume-item[
  - Manifest V3 browser extension redirecting ~30 tracked sites (YouTube, X, Reddit, Google, Instagram, TikTok) to privacy-friendly frontends (Piped, Nitter, Redlib, SearXNG, etc.).
  - Minimal-permission architecture published on Chrome Web Store, Firefox Add-ons (incl. Android), and Microsoft Edge.
  - Automated instance health checking and sync workflows maintained via GitHub Actions (`pritkr/instances`).
]

#resume-entry(
  title: "JanSahay — Welfare Scheme Eligibility Platform",
  location: "jansahay.pages.dev",
  location-link: "https://jansahay.pages.dev",
  title-link: "https://jansahay.pages.dev",
  date: "Sep 2026",
  description: "Built with Team Tejas at TEJAS India Hackathon 2026 (GEC Sheikhpura)"
)
#resume-item[
  - JanSahay exists because people were quietly losing benefits they were already eligible for — Bihar's welfare schemes are scattered across PDFs and barely-usable portals, so I built a Hindi-first app where you register once and it instantly tells you which schemes you qualify for.
  - Designed around my own users in rural Bihar: offline-first so it works without data, 48px touch targets, and Hindi TTS that reads scheme details aloud for people who struggle with text.
  - Added a Hindi chat assistant that refuses to hallucinate — a deterministic rule engine decides eligibility, and a free LLM only rephrases the reply; no AI ever makes the call on who gets a benefit.
  - Consent-first by design: a local sahayak (helper) verifies and syncs a person's profile via OTP, and deadline alerts warn people before a scheme window closes — not after.
  - Under the hood it's a TypeScript monorepo shared between a React PWA and an Android app, deployed as a Cloudflare Worker and live at jansahay.pages.dev.
]

#resume-entry(
  title: "BEU Connect — Academic Utility Portal",
  location: "beu.prit.eu.org",
  location-link: "https://beu.prit.eu.org",
  title-link: "https://beu.prit.eu.org",
  date: "2024 - Present",
  description: "Creator & Lead Developer"
)
#resume-item[
  - Centralized portal bundling syllabus, exam results, result analytics, and official alerts for Bihar Engineering University colleges.
  - Scraped and parsed PYQ (past-year question) papers from scattered unofficial sites into a structured, searchable archive.
  - Digitized scanned question papers using OCR and Vision-Language Models (VLMs).
  - Built a bulk ingestion pipeline dumping result data for all BEU students into a queryable database powering result analytics.
  - Optimized frontend architecture ensuring rapid mobile load times and seamless navigation for thousands of BEU engineering students.
]

#resume-entry(
  title: "chaind-cli — Sovereign AI Agent Daemon",
  location: "github.com/fossism/chaind-cli",
  location-link: "https://github.com/fossism/chaind-cli",
  title-link: "https://github.com/fossism/chaind-cli",
  date: "2024 - Present",
  description: "Lead Developer"
)
#resume-item[
  - Headless Go daemon bridging messaging apps (WhatsApp, Matrix, Telegram) directly to local AI agents via permission-gated Unix sockets.
  - Designed for secure, zero-cloud interaction with self-hosted LLMs without exposing open network ports.
]

#resume-entry(
  title: "listbrew — Contact Sync Engine",
  location: "github.com/pritkr/listbrew",
  location-link: "https://github.com/pritkr/listbrew",
  title-link: "https://github.com/pritkr/listbrew",
  date: "Dec 2025 - Present",
  description: "Creator & Maintainer"
)
#resume-item[
  - Real-time contact synchronization engine written in Python for Frappe to sync contacts directly into Listmonk.
  - Shipped with full automated CI/CD quality gates using Ruff, Semgrep, ESLint, PyUpgrade, and pip-audit.
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
  - Lead tech and programs for a FOSS community aligned with FOSS United & Samagata linking tier-2/3 college students with open-source mentors, workshops, internships, and real projects.
  - Built production tooling including automated certificate generators, event portals, and Frappe/Listmonk sync integrations.
]

#resume-entry(
  title: "Navprayas — Student-Run Non-Profit Society",
  location: "navprayas.in — Manpur Patwatoli, Gaya, Bihar",
  location-link: "https://navprayas.in",
  title-link: "https://navprayas.in",
  date: "May 2025 - Present",
  description: "Team Lead — Website, Database & Anchoring"
)
#resume-item[
  - Team lead for website, database, and anchoring at Navprayas — a student-run non-profit (est. 2000) driving education and development for the Manpur–Patwatoli society in Gaya, Bihar (15K+ participants, 700+ alumni).
  - Drove the org's first online registration transition, integrating Razorpay payment gateway, for MTSE (Manpur Talent Search Exam, classes V–X) and other events.
  - Handled issues faced by school students and their parents using the new online forms for the first time — providing end-to-end support.
  - Anchored annual felicitation ceremonies including Pratibha Milan.
]

#resume-entry(
  title: "FOSS Club GEC Sheikhpura (FOSS United)",
  location: "fossunited.org/c/gec-sheikhpura",
  location-link: "https://fossunited.org/c/gec-sheikhpura",
  title-link: "https://fossunited.org/c/gec-sheikhpura",
  date: "Aug 2025 - Present",
  description: "Core Team Member"
)
#resume-item[
  - Core team member of Bihar's first FOSS United college club — organizing Git/GitHub workshops, Linux installation parties, and GSoC career conferences.
  - Arch Linux advocate; converted ~15 student machines to Linux environments and terminal workflows.
]

= Technical Skills
#resume-skill-item(
  "Languages",
  ("Python", "TypeScript", "JavaScript", "Go", "C", "C++", "Bash", "SQL")
)
#resume-skill-item(
  "Web & Stack",
  ("React", "Astro", "Tailwind CSS", "HTML/CSS", "REST APIs", "Node.js")
)
#resume-skill-item(
  "Tools & Systems",
  ("Git/GitHub", "GitHub Actions", "Linux (Arch)", "Docker", "Nginx", "PostgreSQL", "Supabase", "Frappe")
)
#resume-skill-item(
  "Data & Automation",
  ("Web Scraping & Parsing", "OCR & Vision-Language Models", "ETL Pipelines", "CI/CD")
)
#resume-skill-item(
  "Agentic AI",
  ("OpenCode", "Claude Code", "AI Agent Workflows", "LLM-Assisted Development")
)
#resume-skill-item(
  "Focus Areas",
  ("Privacy Tech", "FOSS", "Self-Hosting", "Community Building")
)

= Education
#resume-entry(
  title: "Government Engineering College (GEC), Sheikhpura",
  location: "Sheikhpura, Bihar, India",
  date: "2024 - 2028",
  description: "B.Tech in Computer Science & Engineering — Bihar Engineering University (BEU)"
)
