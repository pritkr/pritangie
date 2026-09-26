# SPEC-015 — nyaya-guard v2: freshness + production sampling loop

## v1 verified (do not regress)
Rules-decide/LLM-rephrase, hybrid BM25+hashvec RRF, 12 schemes, 33 tests green, eval 1.000s, refusal-recall 1.000.

## v2 goal
Close the #1 production-RAG blind spot (TDS/Oracle 2026): stale/conflicting documents — fluent, well-cited answers built on superseded docs — plus a production-sampling loop that grows the golden set from real traffic.

## Scope (bounded)
1. **Versioned corpus** — `data/schemes/_versions/` with 2 superseded scheme versions (e.g., old cycle-yojana amount, expired pension dates) marked `superseded_by` + `valid_until` frontmatter; `ingest.ts` tags chunks with version/freshness; retriever freshness boost (current > superseded, superseded retrievable but flagged).
2. **Staleness guard** — if top evidence is superseded, answer MUST cite the current version and note the change ("yeh rashi badal gayi hai"); 4 new eval cases (stale-amount, expired-date, superseded-doc-must-not-win, explicit old-question answered-from-new-doc). Eval stays exit 0.
3. **`eval/sample.ts`** — production sampler: reads `logs/audit*.jsonl`, clusters unanswered/low-confidence queries, proposes new golden cases into `eval/proposed.json` (human reviews before promotion). Documents the weekly loop in README.
4. **`/ingest` file upload** — admin endpoint accepting markdown with version frontmatter validation (rejects missing valid_from / bad supersedes links).

## Non-goals
No vector DB, no LLM judge, no multi-tenancy.

## Acceptance
`npm test` green (≥40 tests), `npm run eval` exit 0 incl. 4 freshness cases, sampler runs on existing logs producing proposed.json, README v2 section (freshness model + sampling loop).
