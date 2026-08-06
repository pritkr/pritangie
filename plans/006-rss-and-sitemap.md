# Plan 006: Add an RSS feed (sitemap half already done in the working tree)

> **Executor instructions**: You are working IN-PLACE in the user's live working
> tree (not a worktree). Treat the CURRENT on-disk file contents as your
> baseline, NOT git HEAD. Do NOT commit, stash, branch, or run destructive git
> commands. Run every verification command and confirm the expected result
> before moving to the next step. Touch only the files listed as in scope. If
> any STOP condition occurs, stop immediately and report — do not improvise.
> SKIP the instruction to update `plans/README.md` — the reviewer maintains the
> index.
>
> **Drift check (run first)**: Read these live files and confirm the "Current
> state" facts: `package.json`, `astro.config.mjs`, `public/robots.txt`,
> `src/layouts/Layout.astro`. If any fact is materially wrong, STOP and report.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none (run after 008 if 008 has landed, so the new endpoint is type-checked)
- **Category**: dx
- **Planned at**: commit `05c4424`, 2026-08-03 (re-baselined to working tree 2026-08-04)

## Why this matters

The site's footer advertises "No trackers · No cookies · Built with Astro ·
Hosted on my own terms" (`src/components/Footer.astro:32-34`). The
privacy-respecting way for readers to follow such a site is RSS — but the site
has no feed. The sitemap half of this work is ALREADY done in the working tree
(`@astrojs/sitemap` installed, wired in `astro.config.mjs`, generating
`sitemap-index.xml`, hand-written `public/sitemap.xml` deleted, `robots.txt`
pointing at the generated index). This plan now covers only the remaining RSS
half: add an `@astrojs/rss` endpoint and advertise it in the document head.

## Current state (live working tree — verified)

- `astro.config.mjs:4,9` already imports and wires `@astrojs/sitemap`:
  `integrations: [sitemap()]`. Build logs confirm `sitemap-index.xml` is created.
- `package.json:12` already lists `"@astrojs/sitemap": "^3.7.3"`.
- `public/sitemap.xml` (hand-written) is already DELETED — do not recreate it.
- `public/robots.txt:4` already reads `Sitemap: https://prit.eu.org/sitemap-index.xml`.
- `src/layouts/Layout.astro` head (lines 21-69) has Open Graph, Twitter, icons,
  manifest, and the remixicon stylesheet, but NO `<link rel="alternate"
  type="application/rss+xml">`.
- `src/pages/rss.xml.ts` does NOT exist; `dist/rss.xml` is not generated.
- `package.json` has NO `@astrojs/rss` dependency.
- `src/pages/posts/` has three Markdown posts. Frontmatter shape (from
  `post-1.md:1-12`): `title`, `author.name`, `author.url`, `image.url`,
  `image.alt`, `tags`, `pubDate`. No `description` field yet (Plan 003 owns it).
- The existing post-glob pattern lives in `src/components/RecentBlog.astro:2-4`:
  ```ts
  const allPosts = Object.values(
    import.meta.glob("../pages/posts/*.md", { eager: true }),
  );
  ```
  Reuse this exact glob for the feed.
- `astro.config.mjs:8` defines `site: "https://prit.eu.org"`.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Install RSS dep | `bun add @astrojs/rss` | exit 0; added to `package.json` |
| Build | `bun run build` | exit 0; 8 pages + sitemap-index.xml + rss.xml |
| Feed present | `test -f dist/rss.xml && grep -c "<item>" dist/rss.xml` | file exists; >=3 items |
| Feed advertised | `grep -o "application/rss+xml" dist/index.html` | one match |
| (if 008 landed) Typecheck | `bun run check` | exit 0 |

## Scope

In scope: `package.json` (add `@astrojs/rss`), new file `src/pages/rss.xml.ts`,
and `src/layouts/Layout.astro` (add one `<link rel="alternate">` line).

Out of scope: `astro.config.mjs` (sitemap already wired — do not touch),
`public/sitemap.xml` (already deleted — do not recreate), `public/robots.txt`
(already correct), post frontmatter content (Plan 003), workshop files, the
service worker, anything in `src/components/`.

## Steps

### Step 1: Install the RSS integration

Run `bun add @astrojs/rss`. It must appear under `dependencies` in `package.json`.

**Verify**: `grep "@astrojs/rss" package.json` -> one match.

### Step 2: Add the RSS endpoint

Create `src/pages/rss.xml.ts` exporting a `GET` handler using `@astrojs/rss`.
Model the post glob on `RecentBlog.astro:2-4`:

```ts
import rss from "@astrojs/rss";
import type { APIContext } from "astro";

const posts = Object.values(import.meta.glob("./posts/*.md", { eager: true })) as any[];

export async function GET(context: APIContext) {
  const sorted = posts.sort(
    (a, b) => new Date(b.frontmatter.pubDate) - new Date(a.frontmatter.pubDate)
  );
  return rss({
    title: "Prit's Den",
    description: "Open-source, privacy tech, and FOSS community building — Prit Kumar.",
    site: context.site ?? "https://prit.eu.org",
    items: sorted.map((p) => ({
      title: p.frontmatter.title,
      pubDate: new Date(p.frontmatter.pubDate),
      link: p.url,
      description: p.frontmatter.description, // optional until Plan 003 lands
    })),
  });
}
```

The `as any[]` cast mirrors the existing `: any` pattern in `RecentBlog.astro:18`.
If Plan 008 has landed and introduced a stricter `Post` type, use that instead
of `any`.

**Verify**: `bun run build` -> exit 0; `test -f dist/rss.xml` succeeds;
`grep -c "<item>" dist/rss.xml` -> at least 3.

### Step 3: Advertise the feed in the document head

In `src/layouts/Layout.astro`, inside `<head>`, after the stylesheet link at
line 68 (`<link rel="stylesheet" href="/fonts/remixicon/remixicon.css" />`), add:

```astro
<link rel="alternate" type="application/rss+xml" title="Prit's Den" href={new URL("/rss.xml", site).href} />
```

(`site` is already defined at `Layout.astro:14`.)

**Verify**: `bun run build` -> exit 0; `grep -o "application/rss+xml" dist/index.html`
-> one match.

## Test plan

No test framework; verification is build + file presence (above). If Plan 008
has landed, run `bun run check` and ensure `rss.xml.ts` typechecks.

## Done criteria

- [ ] `bun run build` exits 0
- [ ] `test -f dist/rss.xml` succeeds and contains >=3 `<item>`s
- [ ] `grep "application/rss+xml" dist/index.html` returns one match
- [ ] `@astrojs/rss` is in `package.json` dependencies
- [ ] `astro.config.mjs`, `public/robots.txt`, and `public/sitemap.xml` are NOT modified by you (already correct/absent)
- [ ] No files outside the in-scope list are modified; workshop files unchanged

## STOP conditions

- Stop if `@astrojs/rss` cannot be installed without upgrading Astro or Vite
  (peer-version conflicts) — do not upgrade the framework.
- Stop if `src/pages/rss.xml.ts` requires an Astro routing change beyond a
  standard endpoint in this Astro version.
- Stop if the live `astro.config.mjs` does NOT already have the sitemap wired
  (it does as of this writing — if it doesn't, the sitemap half is not done and
  you should STOP and report rather than re-doing it here).

## Maintenance notes

- Every new post automatically appears in the feed — no manual edits.
- Treat `pubDate` as required frontmatter for posts; without it the feed sort breaks.
- Plan 003 adds `description`; once present, feed items gain summaries automatically.
- The feed URL `/rss.xml` is stable — do not rename it without updating the
  `<link rel="alternate">` and any external directory listings.
