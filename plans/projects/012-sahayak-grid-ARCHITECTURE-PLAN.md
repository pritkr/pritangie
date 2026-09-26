# 012 — sahayak-grid: Offline-first civic PWA kit

> Future repo: `pritkr/sahayak-grid` (MIT). Slot: Full Stack MERN + PWA + Edge.
> Targets: Qubixo/Trinity/Blazeline/Skillzenloop MERN, BEMPU Health REST+PWA, Android Kotlin, Vibencode/ETark.

## 1. Architecture

```
┌─ web/ (Astro + Tailwind, Hindi-first, 48px, <50kb initial)
│   sw.js (app-shell + /schemes cache-first, API network-first w/ queue)
│   idb queue (offline writes) → replay on online ─┐
└──────────────────────────────────────────────────┤
┌─ api/ (Hono, CF Worker compat, Node dev) ◀───────┘
│  POST /register, GET /schemes?q=, POST /verify-otp (mock 6-digit),
│  GET /alerts, POST /sync  →  Postgres (Supabase) / SQLite dev
└─ db/schema.sql (profiles, schemes, alerts, consent_log)
```

- **Offline contract:** airplane-mode demo — register + checklist + search work; writes queue in IndexedDB; sync badge shows pending count; replay idempotent via `client_uuid`.
- **i18n:** Hindi default, English toggle, `speechSynthesis` TTS button per scheme, transliteration-tolerant search (normalize anusvara/chandrabindu, s/sh).
- **Perf:** no large images, system fonts, lazy chart SVG, Lighthouse target 95+.

## 2. Repo tree

```
sahayak-grid/
  web/{src/pages, src/components, public/sw.js, astro.config.mjs}
  api/{src/index.ts (Hono), package.json, wrangler.toml}
  db/{schema.sql, seed.sql (8 schemes hi+en)}
  tests/{web.test.ts, api.test.ts} (≥10)
  Dockerfile, README, LICENSE
```

## 3. Build plan by aspect

- **Aspect A — backend:** Hono API + schema + seed + OTP mock + sync replay + REST docs in README.
- **Aspect B — frontend:** Astro pages (home/register/schemes/alerts), SW, IDB queue, TTS, 48px a11y, Hindi toggle.
- **Aspect C — evals/infra:** Lighthouse checklist, `bun run build` green, tests green, Dockerfile, offline demo script in README, screenshots placeholders.
- **Gates:** `bun run build` exits 0; tests ≥10 green; offline demo steps verified.

## 4. Resume bullets

- Shipped Hindi-first offline PWA kit (service worker + IDB sync queue, OTP sahayak verify) with Hono edge API + Postgres; <50kb initial JS.
