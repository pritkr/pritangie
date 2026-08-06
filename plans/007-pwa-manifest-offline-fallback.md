# Plan 007: Fix the PWA manifest theme color and add an offline fallback

> **Executor instructions**: Follow this plan step by step. Run every verification
> command and confirm the expected result before moving to the next step. Touch
> only the files listed as in scope. If any STOP condition occurs, stop
> immediately and report — do not improvise. When done, update the status row
> for this plan in `plans/README.md` unless a reviewer maintains the index.
>
> **Drift check (run first)**: `git diff --stat 05c4424..HEAD -- public/site.webmanifest public/sw.js src/layouts/Layout.astro`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: bug
- **Planned at**: commit `05c4424`, 2026-08-03

## Why this matters

The site registers a service worker (`src/layouts/Layout.astro:95-106`) and
ships a web manifest, so it installs as a PWA. Two things are wrong:

1. `public/site.webmanifest:1` declares `theme_color` **twice** (`#ffffff`
   then `#0b5cff`). Duplicate JSON keys are undefined behavior; the effective
   value (`#0b5cff`, blue) contradicts both the HTML meta `theme-color`
   (`#fefff0`, cream, at `Layout.astro:65`) and the site's cream background
   (`Layout.astro:77` `--main-bg: #fefff0`).
2. The service worker (`public/sw.js`) returns a bare `undefined` when an
   offline navigation hits a page that is not cached (`sw.js:32`
   `.catch(() => cached)` where `cached` is `undefined`), so an installed PWA
   shows the browser's generic offline error instead of a branded fallback.

Both are cheap, additive correctness fixes.

## Current state

- `public/site.webmanifest:1` (single-line JSON):
  ```json
  {"name":"Prit's Den","short_name":"Prit's Den","start_url":"/","icons":[{"src":"/android-chrome-192x192.png","sizes":"192x192","type":"image/png"},{"src":"/android-chrome-512x512.png","sizes":"512x512","type":"image/png"}],"theme_color":"#ffffff","background_color":"#ffffff","theme_color":"#0b5cff","display":"standalone"}
  ```
  Note the two `theme_color` keys.
- `src/layouts/Layout.astro:65` — `<meta name="theme-color" content="#fefff0" />`.
- `src/layouts/Layout.astro:76-80` — CSS palette:
  `--main-bg: #fefff0; --blue: #bae6ff; --yellow: #ffdc58;`.
- `public/sw.js:16-40` — the fetch handler. Key lines:
  ```js
  const cached = await cache.match(request);
  const network = fetch(request)
    .then((resp) => { if (resp && resp.ok) cache.put(request, resp.clone()); return resp; })
    .catch(() => cached);
  if (request.mode === 'navigate' && cached) return cached;
  return cached || network;
  ```
  When offline and `cached` is `undefined`, `network` rejects ->
  `.catch(() => cached)` returns `undefined` -> `event.respondWith(undefined)`
  -> browser offline error.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Build | `bun run build` | exit 0; 8 pages + offline page present |
| SW syntax | `node --check public/sw.js` | no output, exit 0 |
| Manifest valid JSON | `node -e "JSON.parse(require('fs').readFileSync('public/site.webmanifest','utf8'))"` | no error |
| No dup theme_color | `grep -o 'theme_color' public/site.webmanifest \| wc -l` | `1` |
| Offline route built | `test -f dist/offline/index.html` | succeeds |

## Scope

In scope: `public/site.webmanifest`, `public/sw.js`, and one new fallback file:
`src/pages/offline.astro` (preferred — matches the site shell).

Out of scope: workshop files, the rest of the SW caching strategy, manifest
icons, visual redesign, any component other than the new offline page.

## Steps

### Step 1: De-duplicate and align the manifest theme color

Rewrite `public/site.webmanifest` so `theme_color` and `background_color` match
the site palette: `theme_color: #fefff0` (matches `Layout.astro:65` meta and
`--main-bg`) and `background_color: #fefff0`. Add a `description` field
(`"Prit Kumar — open-source & privacy tech."`). Keep the existing `name`,
`short_name`, `start_url`, `icons`, `display` exactly. The result must contain
**exactly one** `theme_color` key. (Pretty-printing the JSON to multiple lines
is fine and recommended for readability.)

**Verify**:
- `grep -o 'theme_color' public/site.webmanifest | wc -l` -> `1`
- `node -e "JSON.parse(require('fs').readFileSync('public/site.webmanifest','utf8'))"`
  -> no error.

### Step 2: Create the offline fallback page

Create `src/pages/offline.astro` so the fallback is on-brand: use the `Layout`
shell and the palette, with a short "You're offline" message and a "Back Home"
button. Model it directly on `src/pages/404.astro:9-37`, which already does this
exact pattern (Layout + Header + a centered card + a `Button` + a text link).
Keep it dependency-free — no GSAP, no external images — so it loads from cache
instantly.

**Verify**: `bun run build` -> exit 0; `test -f dist/offline/index.html`
succeeds.

### Step 3: Serve the fallback when a navigation has no cached response

In `public/sw.js`, change the navigation branch so a failed/missing navigation
returns the cached offline page instead of `undefined`. Concretely, for
`request.mode === 'navigate'` with no `cached`, race the network and, on
failure, `return (await caches.match('/offline/')) ?? Response.error();`.
Preserve the existing background `cache.put` update behavior and the
`skipWaiting()` / `clients.claim()` lifecycle. The `CACHE` constant stays
`'pritden-v1'` (bump to `'pritden-v2'` only if you want to force a clean cache
swap — optional).

**Verify**:
- `node --check public/sw.js` -> no output, exit 0.
- `grep -n "offline" public/sw.js` -> the `/offline/` fallback URL appears in the
  navigation branch.
- `bun run build` -> exit 0.

## Test plan

No unit-test framework in this repo. Acceptance check (record in the PR): build,
serve `dist/` with `bun run preview`, in DevTools -> Application -> Service
Workers, tick Offline, then navigate to a never-visited path -> the branded
offline page appears.

## Done criteria

- [ ] `public/site.webmanifest` has exactly one `theme_color` key, value `#fefff0`
- [ ] `node --check public/sw.js` exits 0
- [ ] `dist/offline/index.html` exists after build
- [ ] `public/sw.js` references `/offline/` in the navigation branch
- [ ] `bun run build` exits 0
- [ ] No files outside the in-scope list are modified; workshop files unchanged

## STOP conditions

- Stop if `node --check public/sw.js` fails after your edit and you cannot fix
  it in one pass — report the syntax error.
- Stop if the offline page requires routing changes beyond adding
  `src/pages/offline.astro`.
- Stop if changing the SW navigation logic would require rewriting the whole
  fetch strategy rather than the navigation branch only.

## Maintenance notes

- Bump `CACHE` in `public/sw.js` whenever cached asset filenames change
  significantly, so returning visitors do not get a stale shell.
- Keep `offline.astro` dependency-free (no GSAP, no remote images) so it loads
  instantly from cache.
- If the site's theme-color palette changes, update the manifest, the
  `Layout.astro:65` meta, and `--main-bg` together so they stay consistent.
