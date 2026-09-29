#import "modern-cv/lib.typ": *

#show: resume.with(
  author: (
    firstname: "Prit Kumar",
    lastname: "",
    email: "pritform@gmail.com",
    phone: "+91 9508364740",
    github: "pritkr",
    linkedin: "prit-kumar",
    website: "https://prit.eu.org",
    address: "Bihar, India",
    positions: (
      "Software Engineering Intern",
      "Full-Stack · Backend · Open Source"
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
    link(title-link)[#title #text(size: 8pt, fill: rgb("#5d5d5d"))[↗]]
  } else {
    title
  }
  let location-content = if location-link != none {
    link(location-link)[#location]
  } else {
    location
  }
  block(above: 0.55em, below: 0.3em)[
    #pad[
      #justified-header(title-content, location-content)
      #if description != "" or date != "" [
        #block[
          #box(width: 1fr)[
            #align(left)[
              #text(fill: dark-ink, size: 10pt, weight: "regular")[
                #description
              ]
            ]
          ]
          #box(width: 1fr)[
            #align(right)[
              #text(fill: dark-ink, size: 10pt, weight: "regular")[#date]
            ]
          ]
        ]
      ]
    ]
  ]
}

#let resume-item(body) = {
  set text(
    size: 10pt,
    style: "normal",
    weight: "regular",
    fill: dark-ink,
  )
  set block(
    above: 0.5em,
    below: 0.65em,
  )
  set par(leading: 0.5em)
  block(above: 0.3em)[
    #body
  ]
}

= Summary
I build software that gives people more control: private browsing, easier access to university data, and clearer paths to public benefits. My work spans a browser extension with 1,000+ installs, tools for 30,000+ student records, and eligibility across 1,000+ schemes. B.Tech CSE student seeking remote SWE internships and full-time roles.

= Projects
#resume-entry(
  title: "Predirect — Privacy Browser Extension",
  location: "Manifest V3 · Browser APIs",
  title-link: "https://github.com/pritkr/predirect",
  date: "Nov 2023 – Present",
  description: "Maintainer & Lead Developer (270+ ★ on GitHub · GPL-3.0)"
)
#resume-item[
  - Redirects 30+ tracking-heavy sites (YouTube, X, Reddit, Google, Instagram, TikTok) to privacy-friendly frontends such as Piped, Redlib, and SearXNG.
  - Reached 1,000+ installs across Chrome, Firefox (including Android), and Microsoft Edge; built with minimal permissions.
  - Automated frontend-instance health checks and synchronization with GitHub Actions (pritkr/instances).
]

#resume-entry(
  title: "BEU Connect — Academic Utility Portal",
  location: "OCR · Vision-Language Models · ETL",
  title-link: "https://beu.prit.eu.org",
  date: "2024 – Present",
  description: "Creator & Lead Developer"
)
#resume-item[
  - Built a student portal consolidating syllabi, exam results, analytics, and official alerts for Bihar Engineering University.
  - Scraped and parsed past-year papers into a searchable archive; digitized scanned papers with OCR and vision-language models.
  - Loaded results for 30,000+ BEU student records through a bulk-ingestion pipeline into a queryable database for analytics.
]

#resume-entry(
  title: "chaind-cli — Chat Apps to Local AI Agents",
  location: "Go · Unix Sockets",
  title-link: "https://github.com/fossism/chaind-cli",
  date: "2024 – Present",
  description: "Lead Developer"
)
#resume-item[
  - Built a headless Go daemon connecting WhatsApp, Matrix, and Telegram to local AI agents over permission-gated Unix sockets.
  - Enables self-hosted LLM use without cloud dependencies or exposed network ports.
]

#resume-entry(
  title: "listbrew — Contact Sync Engine",
  location: "Python · Frappe · CI",
  title-link: "https://github.com/pritkr/listbrew",
  date: "Dec 2025 – Present",
  description: "Creator & Maintainer"
)
#resume-item[
  - Built a Python contact-sync engine connecting Frappe with Listmonk; added CI checks with Ruff, Semgrep, PyUpgrade, and pip-audit.
]

#resume-entry(
  title: "JanSahay — Welfare Scheme Eligibility Platform",
  location: "React PWA · Android · Cloudflare Workers",
  title-link: "https://jansahay.pages.dev",
  date: "Sep 2026",
  description: "Finalist · TEJAS India Hackathon 2026 (GEC Sheikhpura)"
)
#resume-item[
  - Catalogs 1,000+ central and state schemes from myScheme in an India-wide, Hindi-first eligibility app; users create a profile once to find matching benefits.
  - Uses deterministic rules for eligibility and an LLM only to rephrase results; includes offline access, Hindi text-to-speech, OTP-assisted profile sync, and deadline alerts.
  - Shares a TypeScript monorepo across a React PWA and Android app, with backend services on Cloudflare Workers.
]

= Experience
#resume-entry(
  title: "Bodhya FOSS Community",
  location: "bodhya.net — Bihar, India",
  location-link: "https://bodhya.net",
  title-link: "https://bodhya.net",
  date: "Jan 2026 – Present",
  description: "Tech & Programs Lead — Founding Core Team"
)
#resume-item[
  - Lead technology and programs connecting engineering students in Bihar with open-source mentors, workshops, internships, and projects.
  - Built certificate-generation and event tools, plus Frappe/Listmonk integrations.
]

#resume-entry(
  title: "Navprayas — Student-Run Non-Profit Society",
  location: "navprayas.in — Manpur Patwatoli, Gaya, Bihar",
  location-link: "https://navprayas.in",
  title-link: "https://navprayas.in",
  date: "May 2025 – Present",
  description: "Team Lead — Website, Database & Anchoring"
)
#resume-item[
  - Led website and database work for a student-run nonprofit serving Manpur-Patwatoli, Gaya.
  - Delivered the organization's first online registration flow with Razorpay for MTSE and other events.
]

#resume-entry(
  title: "FOSS Club GEC Sheikhpura (FOSS United)",
  location: "fossunited.org/c/gec-sheikhpura",
  location-link: "https://fossunited.org/c/gec-sheikhpura",
  title-link: "https://fossunited.org/c/gec-sheikhpura",
  date: "Aug 2025 – Present",
  description: "Core Team Member"
)
#resume-item[
  - Organized Git/GitHub workshops, Linux installation events, and GSoC career sessions with the FOSS United college club.
  - Migrated 15 student machines to Linux and terminal-based workflows.
]

= Technical Skills
#v(0.35em)
#resume-item[
  #set par(leading: 0.8em)
  *Languages:* Python, TypeScript, JavaScript, Go, C, Bash, SQL \
  *Frontend:* React, Astro, Tailwind CSS, HTML/CSS \
  *Backend & Cloud:* Node.js, REST APIs, PostgreSQL, Supabase, Cloudflare Workers \
  *Tools & Systems:* Git/GitHub, GitHub Actions, Linux (Arch), Docker, Nginx, Frappe \
  *Data & Automation:* Web scraping, OCR, vision-language models, ETL, CI/CD
]

= Education
#resume-entry(
  title: "Government Engineering College (GEC), Sheikhpura",
  location: "Sheikhpura, Bihar, India",
  date: "Expected 2028",
  description: "B.Tech CSE · Bihar Engineering University (BEU)"
)
