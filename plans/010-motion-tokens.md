# 010 — Add motion tokens (strong easing + duration defaults)

- **Status**: TODO
- **Commit**: 3ed8291
- **Severity**: HIGH
- **Category**: 7. Cohesion & tokens
- **Estimated scope**: 1 file (`src/styles/global.css`), small

## Problem

The site has zero motion tokens. There is no `--ease-*` and no `--duration-*`
anywhere in `src/`. Every Tailwind `transition-*` utility in the repo therefore
inherits Tailwind's default timing function, which is a weak **ease-in-out** —
wrong for entering UI (AUDIT.md §2: "Entering or exiting → ease-out",
"Default → ease-out"):

```css
/* src/styles/global.css:1-12 — current (entire file) */

@font-face {
    font-family: 'Space Grotesk';
    font-style: normal;
    font-weight: 300 700;
    font-display: swap;
    src: url('/fonts/space-grotesk-latin.woff2') format('woff2');
}

@import "tailwindcss";
```

Evidence from the built output (`dist/_astro/Footer.D8U9Ge9E.css`):

```
--default-transition-timing-function:cubic-bezier(.4, 0, .2, 1);
.transition{...transition-timing-function:var(--tw-ease,var(--default-transition-timing-function));...}
```

`cubic-bezier(.4, 0, .2, 1)` is Material's ease-in-out: it starts slow, delaying
the exact moment the user is watching. Hand-typed durations are also scattered
(120ms/140ms/160ms in component styles, `duration-200`/`duration-300` in
utilities) with no documented scale. Five plans in this batch (011, 012, 013,
016, 017) reference tokens that this plan must create first.

## Target

Add a `@theme` block to `src/styles/global.css`, immediately after the
`@import "tailwindcss";` line. Every value is copied from AUDIT.md §2 — do not
approximate:

```css
@import "tailwindcss";

@theme {
  /* Motion tokens — added by plans/010, see AUDIT.md §2 */
  --default-transition-duration: 150ms;
  --default-transition-timing-function: cubic-bezier(0.23, 1, 0.32, 1); /* --ease-out: strong ease-out for UI */
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
  --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1); /* iOS-like drawer curve */
}
```

Effects (verified against Tailwind v4's compiled output):

- Every `transition-*` utility without an explicit `ease-*` class now uses
  `cubic-bezier(0.23, 1, 0.32, 1)` — the built `:root` value of
  `--default-transition-timing-function` changes, and utilities reference it via
  `transition-timing-function: var(--tw-ease, var(--default-transition-timing-function))`.
- `--ease-*` keys generate utilities: `ease-out`, `ease-in-out`, and (used for
  the first time by plan 011) `ease-drawer` become real Tailwind classes.
  Note: overriding `--ease-out` also changes the built-in `ease-out` utility —
  intended; no current code uses it (verified by grep).

## Repo conventions to follow

- `src/styles/global.css` is the Tailwind entry (`@import "tailwindcss"`) and is
  imported by every page/component that renders content (`index.astro:2`,
  `about.astro:2`, `blog.astro:2`, `projects.astro:2`, `404.astro:2`, all
  `src/pages/projects/*.astro`, `MarkdownPost.astro:2`, `RandomQuote.astro:2`).
  Theme tokens belong here, NOT in `Layout.astro`'s `:root` — those vars
  (`--main-bg`, `--blue`, `--yellow`) are plain CSS custom properties, not
  Tailwind theme keys, and cannot generate utilities.
- Keep the existing file structure: font-face block first, then the import.
  Append the `@theme` block after the import; do not reorder anything else.

## Steps

1. Open `src/styles/global.css`. After line 10 (`@import "tailwindcss";`), add
   the `@theme { ... }` block from Target, verbatim.
2. Run `bun run build`.
3. Confirm the built CSS picked it up (see Verification).

## Boundaries

- Do NOT touch `src/layouts/Layout.astro` `:root` variables.
- Do NOT add color/font/spacing tokens — motion tokens only.
- Do NOT change `--default-transition-duration` away from `150ms`.
- If `@theme` in this position does not change the built `:root` values, STOP
  and report instead of improvising.

## Verification

- **Mechanical**: `bun run build` succeeds; then:
  `grep -o "default-transition-timing-function:cubic-bezier([^)]*)" dist/_astro/*.css | head -1`
  → must print `cubic-bezier(.23, 1, .32, 1)` (minifier may drop leading zeros:
  `.23`/`.32`; spacing may vary). It must NOT still be `cubic-bezier(.4, 0, .2, 1)`.
- **Feel check**: run `bun run dev`, load `/`, hover a nav link and a works card:
  - the yellow underline wipe and the card shadow lift now start fast and
    settle, instead of the symmetric Material ease-in-out;
  - in DevTools → Rendering, nothing to toggle here — this is a curve change,
    watch it at 50% speed in the Animations panel: the first 30% of the
    duration should cover >50% of the distance.
- **Done when**: built CSS shows the new default easing AND the hover feel
  check passes.
