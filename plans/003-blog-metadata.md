# Plan 003: Fix article previews and per-post metadata

> **Executor instructions**: You are working IN-PLACE in the user's live working
> tree (not a worktree). Treat the CURRENT on-disk file contents as your
> baseline, NOT git HEAD — the repo HEAD is stale. Do NOT commit, stash, branch,
> or run destructive git commands. Run every verification command and confirm
> the expected result before moving to the next step. Touch only the files
> listed as in scope. If any STOP condition occurs, stop immediately and report
> — do not improvise. SKIP the instruction to update `plans/README.md` — the
> reviewer maintains the index.
>
> **Drift check (run first)**: Read these live files and confirm the "Current
> state" facts: `src/components/RecentBlog.astro`, `src/components/MarkdownPost.astro`,
> `src/layouts/Layout.astro`, and the three `src/pages/posts/*.md`. If any fact
> is materially wrong, STOP and report.

## Status

- **Priority**: P1
- **Effort**: S/M
- **Risk**: LOW
- **Depends on**: none
- **Category**: bug
- **Planned at**: commit `05c4424`, 2026-08-03 (re-baselined to working tree 2026-08-04)

## Why this matters

Recent article cards render `frontmatter.description || frontmatter.subtitle`
(`RecentBlog.astro:38`), but the three posts define neither field, so every
article card on the homepage shows an EMPTY summary paragraph. Markdown posts
also render `<Layout>` without title, description, or image props
(`MarkdownPost.astro:32`), so every post shares the generic site metadata
instead of its own — bad for SEO and social previews. `Layout.astro` already
accepts `title`/`description`/`image` props (lines 2-12); they are just never
passed from the post layout.

## Current state (live working tree — verified post-008)

- `src/components/RecentBlog.astro:2-13` defines a `Post` type (added by Plan
  008) where `frontmatter.description?: string` and `frontmatter.subtitle?:
  string` are already optional fields. Line 38 renders
  `{frontmatter.description || frontmatter.subtitle}` — empty because posts
  define neither.
- `src/components/MarkdownPost.astro:11-22` defines the same `Post` type. Line
  32 is the bare `Layout` tag with NO props passed — the bug. It has `frontmatter`
  from `Astro.props` (line 9) and a typed post glob (lines 24-25).
- `src/layouts/Layout.astro:2-6` — Props interface: `title?`, `description?`,
  `image?`. Lines 8-12 provide defaults (site title, site description,
  `/assets/predirectpreview.avif`). So Layout already supports per-page metadata;
  MarkdownPost just does not pass it.
- `src/pages/posts/post-1.md`, `post-2.md`, `post-3.md` — frontmatter has
  `title`, `author.name`, `author.url`, `image.url`, `image.alt`, `tags`,
  `pubDate`. NO `description` field in any of the three (confirmed by grep).

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Build | `bun run build` | exit 0; 8 pages + sitemap-index.xml |
| Typecheck | `bun run check` | exit 0, 0 errors (gate now exists from Plan 008) |
| Check descriptions | `grep -n "description:" src/pages/posts` | exactly one description per post |
| Check built metadata | `grep -o "<title>[^<]*</title>" dist/posts/post-1/index.html` | post-1 has its own title |

## Scope

In scope: the three post frontmatter files (`src/pages/posts/post-1.md`,
`post-2.md`, `post-3.md`), `src/components/MarkdownPost.astro` (pass props to
Layout), and `src/layouts/Layout.astro` only if a metadata prop needs a tweak
(it likely does not — it already accepts the props).

Out of scope: article prose body, workshop files, analytics, URL changes,
`src/components/RecentBlog.astro` (already correct — it reads the field once
posts define it), `src/pages/blog.astro`, `src/components/Tools.astro`.

## Steps

### Step 1: Add concise frontmatter descriptions

Add a one- or two-sentence `description` to each post's frontmatter (after
`title`, before or near `image`). It must accurately state the article's subject
and be useful as a search/social preview — not a verbatim repeat of the title.
Base each description on the post's own opening sentences (do not invent facts):
- post-1 (Predirect): the one-install extension that rewrites 30+ tracked sites
  to privacy-friendly frontends.
- post-2 (BEU Connect): one static page gathering syllabus, results, and notices
  for every BEU college.
- post-3 (chaind): a Go daemon bridging chat apps to local AI over a
  permission-gated Unix socket.

**Verify**: `grep -n "description:" src/pages/posts/*.md` -> exactly three
matches, one per post.

### Step 2: Pass frontmatter into the post layout

At `src/components/MarkdownPost.astro:32`, replace the bare Layout tag with a
Layout call that passes the post's title, description, and image URL from
frontmatter. Concretely, change the bare tag to pass `title={frontmatter.title}`,
`description={frontmatter.description}`, and `image={frontmatter.image?.url}`.
Preserve the existing default behavior for non-post pages (Layout already
defaults the props). The resulting page title should be the article title; if
you want the site name appended, use `title={`${frontmatter.title} — Prit's Den`}`
— but keep it concise.

**Verify**: `bun run build` -> exit 0; then `grep -o "<title>[^<]*</title>"
dist/posts/post-1/index.html` -> post-1 has its OWN title (not the generic site
title "Prit's Den — Open Source & Privacy Tech").

### Step 3: Confirm cards now show non-empty summaries

`RecentBlog.astro:38` already reads `frontmatter.description || frontmatter.subtitle`.
After Step 1, `description` is present, so cards will show it. Do NOT change
RecentBlog.astro. Just verify the built homepage cards are non-empty.

**Verify**: `bun run build` -> exit 0; then open `dist/index.html` and confirm
all three article cards have non-empty summary text (no empty
`<p class="text-sm line-clamp-3"></p>`). A quick check:
`grep -c "line-clamp-3" dist/index.html` -> 3, and none of them are immediately
followed by `</p>` with no text between.

## Test plan

No unit-test framework. Verification is build + grep of built HTML (above).
Also run `bun run check` (the Plan 008 gate) to confirm no type errors were
introduced by the MarkdownPost prop-passing change.

## Done criteria

- [ ] `grep -n "description:" src/pages/posts/*.md` returns exactly 3 matches
- [ ] Each built post has its own title (verify post-1: its title is NOT the
  generic "Prit's Den — Open Source & Privacy Tech")
- [ ] Homepage article cards contain non-empty summaries
- [ ] `bun run build` exits 0, 8 pages
- [ ] `bun run check` exits 0, 0 errors
- [ ] `RecentBlog.astro`, `blog.astro`, `Tools.astro`, and workshop files are NOT modified
- [ ] No files outside the in-scope list are modified

## STOP conditions

- Stop if the existing Astro version does not accept the proposed Layout props
  without changing the route model (it should — Layout already declares them).
- Stop if a description would require inventing facts not present in the post —
  derive it from the post's own text instead.
- Stop if passing the image prop breaks the OG image URL resolution (Layout
  already builds `socialImageURL = new URL(image, site)` at line 16, so a
  relative path like `/assets/predirectpreview.avif` should resolve).

## Maintenance notes

Treat `description` as required frontmatter for new posts — the `Post` type in
RecentBlog/MarkdownPost already has it optional, but a missing description means
an empty card. A future content collection schema could enforce it, but that
migration is outside this plan. When adding a new post, also confirm its built
HTML has distinct metadata via the Step 2 grep.
