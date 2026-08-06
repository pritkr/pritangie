# Plan 008: Add a real typecheck gate with `astro check`

> **Executor instructions**: You are working IN-PLACE in the user's live working
> tree (not a worktree). Treat the CURRENT on-disk file contents as your
> baseline, NOT git HEAD — the repo HEAD is stale relative to the working tree.
> Do NOT commit, stash, branch, or run any destructive git command. Run every
> verification command and confirm the expected result before moving to the next
> step. Touch only the files listed as in scope. If any STOP condition occurs,
> stop immediately and report — do not improvise. SKIP the instruction to update
> `plans/README.md` — the reviewer maintains the index.
>
> **Drift check (run first)**: Read these live files and confirm they match the
> "Current state" facts below: `package.json`, `tsconfig.json`,
> `src/components/RecentBlog.astro`, `src/pages/blog.astro`,
> `src/components/MarkdownPost.astro`, `src/components/Service.astro`. If any
> fact is materially wrong, STOP and report.

## Status

- **Priority**: P1
- **Effort**: S/M
- **Risk**: MED
- **Depends on**: none (foundational — land first so 006/007 can use `bun run check`)
- **Category**: dx
- **Planned at**: commit `05c4424`, 2026-08-03 (re-baselined + scope-expanded 2026-08-04)

## Why this matters

`tsconfig.json:2` extends `astro/tsconfigs/strict`, but nothing enforces it.
Adding `astro check` as a `check` script gives every subsequent plan a real
verification gate. Running the gate also surfaced a live runtime bug in
`Service.astro` (the Recommendations section renders `<a href={undefined}>`
with no text because `desc: [recs]` double-wraps the array), so fixing it is
in scope here — it is a one-line fix the gate naturally requires to go green.

This plan **supersedes the timid Step 4 of Plan 005**, whose STOP condition
("Stop if a quality tool requires dependency installation") would otherwise
block exactly this improvement. (The two `any` sites formerly in `Tools.astro`
are already gone — that file was rewritten to a pure-CSS marquee in the working
> tree; 009 is therefore already satisfied.)

## Current state

- `tsconfig.json`:
  ```json
  { "extends": "astro/tsconfigs/strict", "include": [".astro/types.d.ts", "**/*"], "exclude": ["dist"] }
  ```
- `package.json:5-10` scripts: `dev`, `build`, `preview`, `astro` only (NO `check`
  script). NOTE: a prior executor run may have already added `"check": "astro check"`
  and a `devDependencies` block with `@astrojs/check` + `typescript@6`. If so, do
  NOT redo Step 1; confirm they exist and proceed to Step 2.
- `package.json` dependencies (live): `@astrojs/sitemap`, `@tailwindcss/vite`,
  `astro`, `tailwindcss`, `vite`. (No `gsap` — already removed.)
- Escape hatches / untyped globs (confirmed by `bun run check` = 19 errors):
  - `src/components/RecentBlog.astro:9` and `:18` — untyped post glob +
    `({ url, frontmatter }: any)`; `:25` reads `frontmatter.subtitle`.
  - `src/pages/blog.astro:8` and `:22` — same untyped glob + `: any`.
  - `src/components/MarkdownPost.astro:12,14,45,47,51,53` — same untyped glob,
    accessing `.url`/`.frontmatter.title` on `unknown`.
  - `src/components/Service.astro:45` — `desc: [recs]` double-wraps the `recs`
    array; `:109,114` then access `r.link`/`r.name` on the wrong shape, rendering
    broken `<a href={undefined}>` links in the Recommendations section.
- `src/components/Tools.astro` is ALREADY a pure-CSS marquee with no `any` — do
  NOT touch it; it is out of scope.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Install typecheck deps | `bun add -d @astrojs/check typescript@6` | exit 0; `devDependencies` created |
| Typecheck | `bun run check` | exit 0, 0 errors |
| Build still works | `bun run build` | exit 0; 8 pages + sitemap-index.xml |

## Scope

In scope: `package.json`, `src/components/RecentBlog.astro`,
`src/pages/blog.astro`, `src/components/MarkdownPost.astro`, and
`src/components/Service.astro` (ONLY the one-line `desc: [recs]` -> `desc: recs`
fix at line 45 — do not otherwise refactor Service.astro). `tsconfig.json` only
if `astro check` requires a minor tweak — prefer not to touch it.

Out of scope: `src/components/Tools.astro` (already fixed), workshop files,
refactoring beyond the type fixes + the one-line Service.astro bug fix,
ESLint/Prettier, content changes, any other visual/behavior change.

## Steps

### Step 1: Add the typecheck tooling (may already be done)

Run `bun add -d @astrojs/check typescript@6` (pin TS6 — `@astrojs/check`'s peer
range is `^5 || ^6`; TS7 dropped the programmatic API `astro check` needs).

**Verify**: `grep -E "@astrojs/check|typescript" package.json` -> both present
under `devDependencies`; `bun run check --version` or `bunx astro check` runs
without a peer-version error. If a prior executor already did this, confirm and
skip.

### Step 2: Add the `check` script (may already be done)

In `package.json`, add `"check": "astro check"` to `scripts` (after `"build"`).

**Verify**: `bun run check` runs and reports errors (expected non-zero at this
point). Capture the full error list. If a prior executor already added the
script, confirm and skip to Step 3.

### Step 3: Fix the flagged sites — do NOT suppress with `@ts-ignore`

Do **not** add `// @ts-ignore` and do **not** loosen `tsconfig.json`. Two fixes:

**(a) Type the post glob.** Define a local `Post` type and apply it to the glob
results in `RecentBlog.astro`, `blog.astro`, and `MarkdownPost.astro`:

```ts
type Post = {
  url: string;
  frontmatter: {
    title: string;
    pubDate: string;
    image?: { url: string; alt?: string };
    description?: string;
    subtitle?: string; // RecentBlog.astro:25 reads frontmatter.subtitle
    author?: { name: string; url: string };
    tags?: string[];
  };
};
```

Cast the glob result `as Post[]` (or type the `.map` callbacks with `: Post`).
This resolves the 17 in-scope errors.

**(b) Fix the Service.astro bug.** At `src/components/Service.astro:45`, change
`desc: [recs]` to `desc: recs`. This removes the extra array wrap so that
`item.desc.map((r) => r.link / r.name)` at lines 107-114 works — the
Recommendations links will now render with real hrefs and text. This is a
one-line fix; do not otherwise refactor Service.astro.

**Verify**: `bun run check` -> exit 0, 0 errors.

### Step 4: Confirm the build is unaffected (and the recs now render)

**Verify**: `bun run build` -> exit 0, 8 pages + `sitemap-index.xml`. Then
`grep -o 'href="https://brave.com"' dist/index.html` -> at least one match
(proves the Recommendations links now render with real hrefs after the
Service.astro fix).

## Test plan

The gate itself is the test. The `grep` for a real recommendation href in the
built HTML confirms the Service.astro bug fix took effect. No new unit-test
files (the repo has no test framework).

## Done criteria

- [ ] `bun run check` exits 0 with 0 errors
- [ ] `bun run build` exits 0, 8 pages + sitemap-index.xml
- [ ] `grep -rnE ': any|as any' src/components/RecentBlog.astro src/pages/blog.astro` returns no matches (or each remaining one is documented as unavoidable)
- [ ] No `// @ts-ignore` added anywhere (`grep -rn "@ts-ignore" src` -> no matches)
- [ ] `package.json` has a `check` script and a `devDependencies` block with `typescript@6`
- [ ] `Service.astro:45` is `desc: recs` (not `desc: [recs]`); `dist/index.html` contains a real recommendation href (e.g. `href="https://brave.com"`)
- [ ] No files outside the in-scope list are modified; `Tools.astro` and workshop files unchanged

## STOP conditions

- Stop if `bun run check` still surfaces errors AFTER the Step 3 fixes that are
  NOT the 19 already catalogued (i.e., new/widespread pre-existing type errors
  appear elsewhere) — do NOT attempt a broad refactor; report the full list.
- Stop if `@astrojs/check` requires an Astro or Vite version bump — do not
  upgrade the framework here. (Pinning `typescript@6` is fine and expected.)
- Stop if fixing a flagged site requires changing runtime behavior BEYOND the
  one-line `Service.astro` fix already authorized — report it.

## Maintenance notes

- `bun run check` is now the typecheck gate; every subsequent plan should
  include it in its done criteria.
- Plan 005 Step 4 is superseded by this plan.
- In review, push back on new `: any` / `as any` — the gate exists to prevent
  regressions. The `Service.astro` `desc: [recs]` bug is a cautionary example of
  what the gate catches that a build-only workflow misses.
