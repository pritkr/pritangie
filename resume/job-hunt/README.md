# job-hunt — remote internship scanner & leads

Reusable, login-free job scanner built for Prit Kumar (B.Tech CSE, GEC Sheikhpura, 2024–2028)
targeting **remote internships / part-time technical work**.

## Start here
- **`leads-board.html`** — open this in your browser (double-click / open in Brave): every scored lead as a
  clickable card with search, source/type/stack filters and an "open top 10 in tabs" button.
- **`leads-2026-09-24.md`** — the curated deliverable: best matches to apply to, FOSS/privacy targets,
  paid programs with dates, ready-to-click LinkedIn searches, and copy-paste application kit.
- `leads-shortlist.md` — auto-generated ranked tables from the last scan.

## Data
- `raw-leads.json` — LinkedIn / Internshala / Unstop rows.
- `raw-leads-extra.json` — Himalayas / RemoteOK / Remotive / Jobicy / Arbeitnow / We Work Remotely /
  Hacker News "Who is hiring" / fossjobs rows.
- `raw-leads-ranked.json` — all rows merged, de-duplicated and scored for fit.
- `board-hits.json`, `board-focus.json` — intern/entry and remote-engineering hits from Ashby + Greenhouse boards.

## Scripts
| Script | What it does |
|---|---|
| `scan.py` | LinkedIn public jobs API (50 keyword/filter combos × 3 pages) + 31 Internshala WFH/part-time pages + Unstop public API (15 pages) |
| `scan3.py` | **Your niche**: 33 targeted LinkedIn combos (browser extensions, privacy, FOSS, scraping/OCR, Frappe/ERPNext/Supabase, agentic AI…) + 23 Internshala keyword pages + YC Work at a Startup + Wellfound |
| `sources.py` | Global remote aggregators: Himalayas (cursor-paged), RemoteOK, Remotive, Jobicy, Arbeitnow, We Work Remotely RSS, Hacker News "Who is hiring", fossjobs RSS |
| `boards.py` | Asks 31 Ashby/Greenhouse boards (Brave, Supabase, Canonical, GitLab, Bitwarden, Proton, Tailscale, Cloudflare, PostHog, Vercel…) for intern/entry + remote engineering roles |
| `rank.py` | Merges everything, de-duplicates, scores for stack fit (Python/TS/Go/React/Linux/privacy/FOSS/LLM) × role type (intern/part-time/contract) × remote-India eligibility × paid × recency; kills senior/sales/HR/unpaid |
| `shortlist.py` | Renders ranked rows into `leads-shortlist.md` |
| `make_board.py` | Renders ranked rows into the self-contained `leads-board.html` board |

Run the whole pipeline (~12 minutes; needs `curl`, `python3`, `beautifulsoup4`, `lxml`):

```bash
cd job-hunt
python3 scan.py && python3 scan3.py && python3 scan4.py && python3 sources.py && python3 boards.py && python3 rank.py && python3 shortlist.py && python3 make_board.py
open leads-board.html
```

`opened.txt` is the registry of every posting already opened in your browser — applied-entry filters
in future rounds read it so nothing shown before is ever re-served. The current applied-entry table is
Section I of `leads-2026-09-24.md` (the definitive Top 20); the next round serves only new entries.

## Tuning it
- More LinkedIn searches: add `(keywords, location, job_type, workplace)` tuples to `LINKEDIN_COMBOS`
  in `scan.py` (`I` = internship, `P` = part-time, `2` = remote).
- More Internshala categories: add `(label, url)` to `INTERNSHALA_PAGES` in `scan.py`.
- More employers: add Ashby slugs to `ASHBY` or Greenhouse slugs to `GREENHOUSE` in `boards.py`.
- Change scoring for your priorities: edit `STRONG`, `WEAK`, `PAID`, `GOOD_COMPANY` and `score()` in `rank.py`.

## Known caveats
- LinkedIn's public jobs API **ignores the part-time filter** and reports an unreliable remote flag —
  always open the posting and confirm the workplace type.
- LinkedIn guest results are capped (~10 per call, 2 pages requested per combo), so this is a snapshot,
  not the whole market.
- No login is used or stored anywhere; nothing is submitted on your behalf.
