# SPEC-014 — vachan-eval v2: production-grade eval discipline

## v1 verified (do not regress)
Mock-first FastAPI, 25-utt golden set, WER/CER + p95, eval gate PASS (mean WER 0.1287, p95 593ms), 24 pytest, React dash + mock fallback, CI.

## v2 goal
Apply production-RAG eval discipline (Oracle/LangSmith/RAGAS practice) to voice: categorized golden sets, regression-vs-baseline gates, input normalization.

## Scope (bounded — this is ALL v2 is)
1. **`app/normalize.py`** — Unicode NFC + Hindi normalization (anusvara/chandrabindra folding, nukta, whitespace/punct strip, digit-word map for ०-९) applied to hypothesis AND reference before scoring. Unit tests ≥8 (bho/mag variants, noisy punct).
2. **Category gates in `eval/run.py`** — group golden.json by `category` (easy/medium/hard/noise/adversarial — add `adversarial` 5 utts: homophones, code-mixed Hinglish, truncated audio-text). Per-category thresholds (easy WER≤0.10, med ≤0.20, hard ≤0.30, noise ≤0.35, adversarial report-only). Gate fails with category named.
3. **Leaderboard history** — `eval/history.jsonl` appends every run (model, mean WER/CER, p95, per-category); `GET /leaderboard` serves history + delta vs previous run; web shows delta arrows.
4. **Regression-vs-baseline** — `eval/baseline.json` (commit current numbers); run.py exits 1 if any metric regresses >0.03 absolute vs baseline (production-sampling practice).

## Non-goals
No real Whisper wiring, no pgvector, no auth.

## Acceptance
`pytest -q` green (≥32 tests), `eval/run.py` exit 0 with category table + baseline check printed, `/leaderboard` returns history, README v2 section documents categories + baseline workflow.
