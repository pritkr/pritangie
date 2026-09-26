# SPEC-016 — sahayak-grid v2: deadline alerts + field analytics

## v1 verified (do not regress)
Astro Hindi PWA, SW + IDB queue, Hono API (register/schemes/verify-otp/alerts/sync idempotent), 8-scheme seed, 31 tests, build 0.

## v2 goal
Turn static scheme data into a living field tool: deadline-driven alerts + analytics proving offline impact — the two things that make civic tech fundable/hireable.

## Scope (bounded)
1. **Deadline engine** — `src/lib/deadlines.ts`: parse `deadline` + `window` from schemes, compute days-left, urgency tiers (critical ≤7d, soon ≤30d, open else); `GET /alerts` returns tiered list sorted by urgency; tests ≥8 (expired, boundary 7/30, no-deadline schemes).
2. **Alert UI** — homepage countdown badges (Hindi "X din bache"), alerts page grouped by tier, TTS reads urgent alerts first.
3. **Sync analytics** — `api` tracks sync attempts (queued/replayed/failed counts in SQLite/dev + Postgres schema migration); `GET /stats` returns them; tiny SVG dashboard on new `/stats` page (no chart lib).
4. **Seed deadlines** — add realistic deadlines/windows to all 8 seed schemes (staggered: 2 critical, 3 soon, 3 open).

## Non-goals
No push notifications, no SMS gateway, no background sync API.

## Acceptance
Tests green (≥39), `bun run build` 0, alerts endpoint returns tiered ordering, stats page renders from real API data, README v2 section with airplane-mode + deadline demo script.
