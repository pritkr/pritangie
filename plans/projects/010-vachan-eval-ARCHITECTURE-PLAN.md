# 010 — vachan-eval: Hindi Voice AI Eval Harness

> GitHub-ready repo spec. Future repo: `pritkr/vachan-eval` (MIT). Portfolio slot: AI/ML + Voice.
> Targets: Karya Research Intern (AI Evals), SuperKalam Voice-First ₹25-40k, Wadhwani AI, Curious Bay AI/ML ₹30-45k, Hulchul AI Eng.

## 1. Architecture (PSD)

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ web/ (Vite  │────▶│ api/ (FastAPI)  │────▶│ eval/ + data/   │
│ React dash) │ HTTP│ /transcribe /tts │     │ golden.json (25)│
│ upload/paste│     │ /eval /health    │     │ run.py → scores │
└─────────────┘     └────────┬─────────┘     └─────────────────┘
                             │ SQLite (default) / Postgres+pgvector (stretch)
                             ▼
                      audit.log JSONL (utt_id, WER, CER, p50/p95, cost)
```

- **Mock-first, no key required:** `TRANSCRIBE_MODE=mock|faster-whisper`. Mock uses deterministic noisy transform so evals run offline in CI. Real STT plugged via `stt_adapter.py` interface (faster-whisper small).
- **Metrics:** WER (jiwer-style impl, no heavy dep — own `metrics.py` with Levenshtein), CER, latency p50/p95, cost/run (tokens×rate table), refusal rate N/A here.
- **API contract:**
  - `POST /transcribe {audio_b64|text, lang: hi|bho|mag} → {transcript, confidence, latency_ms}`
  - `POST /eval → {wer, cer, p95_ms, pass: bool, per_utt[]}`
  - `GET /leaderboard → [{model, wer, p95, cost}]`
  - `GET /health → {ok, mode}`
- **Frontend:** single Vite React page: input → scores → SVG latency histogram + leaderboard table. No chart lib. Works off `file://` against mock JSON fallback.
- **Security/privacy:** audio never leaves machine in mock mode; b64 capped 5MB; allowlist, no exec.

## 2. Repo tree (GitHub-ready)

```
vachan-eval/
  api/{main.py,stt_adapter.py,metrics.py,db.py}
  data/golden.json (25 utts: ration/scholarship/RTE, hi/bho/mag + expected)
  eval/run.py (gate: WER≤0.25, p95≤1200ms, exit 1 on fail)
  web/{index.html,src/{App.tsx,api.ts},vite.config.ts}
  tests/test_metrics.py (12+), tests/test_api.py
  Dockerfile, docker-compose.yml, Makefile, requirements.txt
  .github/workflows/ci.yml (pytest + eval gate)
  README.md, LICENSE (MIT), ARCHITECTURE.md (this file condensed)
```

## 3. Detailed build plan (for aspect subagents)

- **Aspect A — backend/systems:** `api/main.py`, `stt_adapter.py`, `metrics.py` (WER/CER correct, tested on Hindi), `db.py` SQLite→Postgres switch via `DATABASE_URL`. Must `pytest -q` pass.
- **Aspect B — frontend:** `web/` dashboard, Hindi toggle, SVG chart, `api.ts` with mock fallback JSON in `web/public/mock_eval.json`.
- **Aspect C — evals/infra:** `data/golden.json` (25 realistic, hand-written, no lorem), `eval/run.py` printing markdown table, CI gate, Dockerfile (python:3.12-slim, non-root), README with real numbers + failure analysis (where Bhojpuri fails, why).
- **Quality gates:** `pytest -q` ≥12 tests green; `eval/run.py` exits 0 in mock mode; `docker build` passes; README has architecture ASCII + eval table + who-it-impresses + run steps.

## 4. Resume bullets (use after build)

- Built Hindi voice eval harness (25-utt golden set, WER/CER + p95 tracking); eval-gated CI blocks regressions (WER>0.25/p95>1.2s).
- Shipped FastAPI + React dashboard with offline mock mode; Dockerized, no API key needed for demo.
