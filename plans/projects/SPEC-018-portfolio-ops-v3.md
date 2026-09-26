# SPEC-018 — Portfolio ops layer (v3): live deploys + unified proof

## v1+v2 verified (do not regress)

| Project | tests | eval |
|---|---|---|
| vachan-eval | 44 | gate+basis pass, 30 utts, mean WER .1617 |
| nyaya-guard | 54 | 1.000s + freshness 4/4 |
| sahayak-grid | 51 | build 0 |
| agent-kavach | go 45 / py 47 / npm 20 | pass@1 1.00, race-clean |

## v3 goal
Cross-project: turn four local repos into four **live URLs** + one **unified proof page**, so the job-hunt thread's "shipped, deployed, measurable" bar is met without hand-editing.

## Scope (bounded — split across 2 subagents)

### A. Deploy preflight (`scripts/preflight.sh` + `docs/DEPLOY.md` at `projects/`)
- Per project: `preflight <name>` → runs its full test suite, asserts build/eval gate green, checks Dockerfile COPY sources exist, prints env vars needed for the host (Cloudflare Pages / Workers for sahayak + nyaya, HF Space or Fly/Render for vachan, VPS/Docker for kavach) and exact commands.
- `scripts/split.sh` — one-command `git subtree split` per project into `../repos/<name>` clones with remote add + first push, ready for `pritkr/*` creation.
- `docs/DEPLOY.md` — per project: target, prerequisites, secrets list, deploy command, post-deploy smoke test URL, rollback.

### B. Unified proof page (`projects/README.md` rewrite + `projects/benchmarks.json`)
- `benchmarks.json` — machine-readable: per project {tests, eval metric names, headline numbers, stack, targets, deploy url placeholder}.
- `README.md` — badge row, 4 cards with headline numbers, honest limitations per project, mapping table project → job target → what interviewer asks → where proof lives (file path). No fabricated metrics; use verified numbers only.

## Non-goals
No actual deploys (no credentials available in this environment) — preflight + docs + split script only. No changes inside the 4 project folders.

## Acceptance
`scripts/preflight.sh all` exits 0 for all four; `scripts/split.sh --dry-run` prints plan; `benchmarks.json` valid JSON matching verified numbers; README tables complete.
