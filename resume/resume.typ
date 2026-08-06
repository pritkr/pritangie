#import "@preview/modern-cv:0.8.0": *

#show: resume.with(
  author: (
    firstname: "Prit",
    lastname: "Kumar",
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
  paper-size: "a4"
)

= Summary
Open-source developer and B.Tech CSE student building software that respects privacy and freedom. Maintainer of *Predirect* (Manifest V3 browser extension with *260+ ★* on GitHub) redirecting ~30 surveilled platforms to privacy-friendly frontends, published on Chrome, Firefox, and Edge. Co-founder of *Bodhya* FOSS community (aligned with FOSS United / Samagata) bringing tech opportunities, mentorship, and workshops to engineering students in Bihar.

= Featured Project
#resume-entry(
  title: "Predirect — Privacy Browser Extension",
  location: "github.com/pritkr/predirect",
  date: "Nov 2023 - Present",
  description: "Maintainer & Lead Developer (260+ ★ on GitHub · GPL-3.0)"
)
#resume-item[
  - Manifest V3 browser extension redirecting ~30 tracked sites (YouTube, X, Reddit, Google, Instagram, TikTok) to privacy-friendly frontends (Piped, Nitter, Redlib, SearXNG, etc.).
  - Minimal-permission architecture published on Chrome Web Store, Firefox Add-ons (incl. Android), and Microsoft Edge.
  - Automated instance health checking and sync workflows maintained via GitHub Actions (`pritkr/instances`).
]

= Experience & Community
#resume-entry(
  title: "Bodhya FOSS Community",
  location: "bodhya.net — Bihar, India",
  date: "Jan 2026 - Present",
  description: "Co-founder & Core Maintainer"
)
#resume-item[
  - Co-founded a FOSS community aligned with FOSS United & Samagata linking tier-2/3 college students with open-source mentors, workshops, internships, and real projects.
  - Built production tooling including automated certificate generators, event portals, and Frappe/Listmonk sync integrations.
]

#resume-entry(
  title: "listbrew",
  location: "github.com/pritkr/listbrew",
  date: "Dec 2025 - Present",
  description: "Creator & Maintainer"
)
#resume-item[
  - Real-time contact synchronization engine written in Python for Frappe to sync contacts directly into Listmonk.
  - Shipped with full automated CI/CD quality gates using Ruff, Semgrep, ESLint, PyUpgrade, and pip-audit.
]

#resume-entry(
  title: "Bihar FOSS Workshops",
  location: "Community & Install Parties",
  date: "2024 - Present",
  description: "Core Community Organizer"
)
#resume-item[
  - Core member of Bihar-focused FOSS efforts — hosting Linux install weekends, self-hosting workshops, and privacy sessions.
  - Arch Linux advocate; converted ~15 student machines to Linux environments and terminal workflows.
]

= Key Projects
#resume-entry(
  title: "BEU Connect — Academic Utility Portal",
  location: "prit.eu.org/BEUConnect",
  date: "2024 - Present",
  description: "Creator & Lead Developer"
)
#resume-item[
  - Centralized portal bundling syllabus, exam results, result analytics, and official alerts for Bihar Engineering University colleges.
  - Optimized frontend architecture ensuring rapid mobile load times and seamless navigation for thousands of BEU engineering students.
]

#resume-entry(
  title: "chaind-cli — Sovereign AI Agent Daemon",
  location: "github.com/fossism/chaind-cli",
  date: "2024 - Present",
  description: "Collaborator (with @fossism)"
)
#resume-item[
  - Headless Go daemon bridging messaging apps (WhatsApp, Matrix, Telegram) directly to local AI agents via permission-gated Unix sockets.
  - Designed for secure, zero-cloud interaction with self-hosted LLMs without exposing open network ports.
]

= Technical Skills
#resume-skill-item(
  "Languages",
  ("Python", "JavaScript", "Go", "C", "C++ (DSA)", "Bash", "SQL")
)
#resume-skill-item(
  "Web & Stack",
  ("React", "Astro", "Tailwind CSS", "HTML/CSS", "REST APIs")
)
#resume-skill-item(
  "Tools & Systems",
  ("Git/GitHub", "Linux (Arch)", "Figma", "PostgreSQL", "Frappe")
)
#resume-skill-item(
  "Focus Areas",
  ("Privacy Tech", "FOSS", "Self-Hosting", "Community Building")
)

= Education
#resume-entry(
  title: "Bihar Engineering University (BEU)",
  location: "Sheikhpura, Bihar, India",
  date: "2023 - 2027",
  description: "B.Tech in Computer Science & Engineering — Government Engineering College (GEC)"
)