# 013 — Brutalist press feedback on every pressable element

- **Status**: TODO
- **Commit**: 3ed8291
- **Severity**: MEDIUM
- **Category**: 3. Physicality & origin
- **Estimated scope**: 10 files, class-string edits only, small–medium

**Depends on**: none technically; run AFTER 011 and 012 (shared files:
`Header.astro`, `Button.astro`, `Works.astro`, `CopyEmail.astro`,
`RecentBlog.astro`).

## Problem

Pressable elements have no `:active` state almost anywhere in the repo —
`grep -rn ":active" src/` returns exactly ONE hit, the command palette trigger.
AUDIT.md §3: press feedback is part of physicality; pressable elements with no
press feedback is a finding. The site's main CTA (`Button.astro:8`), the works
rail arrows, the mobile PritOS button, and every copy/CTA button respond to a
click with zero visual acknowledgement.

The house pattern already exists and is the exemplar:

```css
/* src/components/CommandPalette.astro:267-276 — current, the ONE place with press */
#command-trigger:hover {
  background: #bae6ff;
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 #000;
}
#command-trigger:active {
  transform: translate(1px, 1px);
  box-shadow: 2px 2px 0 #000;
}
```

Press = the element is pushed into its own hard shadow. This plan extends that
language to the rest of the site using Tailwind `active:` variants (no new CSS
blocks), at 150ms — inside AUDIT.md §2's 100–160ms press budget.

## Target

Two press idioms, chosen by whether the element already uses `translate` for
layout/hover:

- **Idiom A (scale press)** — for elements with no shadow or with `translate`
  used for centering: `transition-transform duration-150 active:scale-[0.97]`
  (rail arrows with a hard shadow additionally collapse it:
  `transition-[scale,box-shadow] duration-150 active:scale-[0.95]
  active:shadow-[1px_1px_0_#000]`).
- **Idiom B (shadow press)** — for hard-shadow buttons that lift on hover:
  replace their `transition-transform` with
  `transition-[translate,box-shadow] duration-150` and append
  `active:translate-y-0.5 active:shadow-[1px_1px_0_#000]` — press drives the
  button 2px *down* past its rest position (beating the hover lift) while the
  offset shadow collapses to 1px.

Why `transition-[translate,box-shadow]` and not `transition-transform`: Tailwind
v4 translate utilities emit the **`translate`** property, which
`transition-transform` does cover — but these buttons also tween
`box-shadow` (hover lift changes it, press collapses it), so the property list
must name both. Do not write `transition-all` (finding #2, plan 011).

### Exact edits

Each `Replace` is a unique substring within that line — keep all other classes.

| # | File:line | Replace | With |
|---|-----------|---------|------|
| 1 | `src/components/Button.astro:8` | `class="bg-[var(--blue)] text-black text-md font-medium flex items-center h-12 px-6 border-3 rounded-full "` | `class="bg-[var(--blue)] text-black text-md font-medium flex items-center h-12 px-6 border-3 rounded-full transition-transform duration-150 active:scale-[0.97]"` |
| 2 | `src/components/Works.astro:123` | `shadow-[3px_3px_0_#000]"` | `shadow-[3px_3px_0_#000] transition-[scale,box-shadow] duration-150 active:scale-[0.95] active:shadow-[1px_1px_0_#000]"` |
| 3 | `src/components/Works.astro:205` | `shadow-[3px_3px_0_#000]"` | `shadow-[3px_3px_0_#000] transition-[scale,box-shadow] duration-150 active:scale-[0.95] active:shadow-[1px_1px_0_#000]"` |
| 4 | `src/components/Header.astro:67` | `bg-[var(--yellow)] px-2 py-1 font-mono text-xs font-bold"` | `bg-[var(--yellow)] px-2 py-1 font-mono text-xs font-bold transition-transform duration-150 active:scale-[0.97]"` |
| 5 | `src/components/CopyEmail.astro:16` | `hover:-translate-y-0.5 transition-transform` | `hover:-translate-y-0.5 transition-[translate,box-shadow] duration-150 active:translate-y-0.5 active:shadow-[1px_1px_0_#000]` |
| 6 | `src/components/CopyEmail.astro:18` | `hover:-translate-y-0.5 transition-transform` | `hover:-translate-y-0.5 transition-[translate,box-shadow] duration-150 active:translate-y-0.5 active:shadow-[1px_1px_0_#000]` |
| 7 | `src/components/CopyEmail.astro:19` | `hover:-translate-y-0.5 transition-transform` | `hover:-translate-y-0.5 transition-[translate,box-shadow] duration-150 active:translate-y-0.5 active:shadow-[1px_1px_0_#000]` |
| 8 | `src/pages/about.astro:111,120,127` (3×) | `transition-transform duration-200` | `transition-[translate,box-shadow] duration-150 active:translate-y-0.5 active:shadow-[1px_1px_0_#000]` |
| 9 | `src/components/RecentBlog.astro:44` | `transition-transform duration-200` | `transition-[translate,box-shadow] duration-150 active:translate-y-0.5 active:shadow-[1px_1px_0_#000]` |
| 10 | `src/pages/projects/predirect.astro:38` | `hover:-translate-y-0.5 transition-transform` | `hover:-translate-y-0.5 transition-[translate,box-shadow] duration-150 active:translate-y-0.5 active:shadow-[1px_1px_0_#000]` |
| 11 | `src/pages/projects/predirect.astro:44` | `hover:-translate-y-0.5 transition-transform` | same as row 10 |
| 12 | `src/pages/projects/sentinel-mcp.astro:34` | `hover:-translate-y-0.5 transition-transform` | same as row 10 |
| 13 | `src/pages/projects/dhvani-eval.astro:34` | `hover:-translate-y-0.5 transition-transform` | same as row 10 |
| 14 | `src/pages/projects/pebble-sync.astro:34` | `hover:-translate-y-0.5 transition-transform` | same as row 10 |
| 15 | `src/pages/projects/spec-forge.astro:34` | `hover:-translate-y-0.5 transition-transform` | same as row 10 |

Notes on the trickier rows:

- **Rows 2–3 (rail arrows)**: these are centered with `-translate-y-1/2`
  (Tailwind translate utilities all write `--tw-translate-y`). An
  `active:translate-y-0.5` would clobber the centering and yank the button off
  center — that is why the rail arrows press with the **`scale` property**
  instead (independent of `translate`), plus the shadow collapse.
- **Rows 5–15 (Idiom B)**: `hover:-translate-y-0.5` and
  `active:translate-y-0.5` both assign `--tw-translate-y`; whichever rule wins
  the cascade decides the press direction. Tailwind orders `active` after
  `hover` — but this MUST be verified in step 3 of Verification, with a
  documented fallback.

## Repo conventions to follow

- Exemplar: `CommandPalette.astro:267-276` (hover lift + press-into-shadow,
  quoted in Problem) — the direction and magnitudes here (±2px, shadow 3px→1px)
  match it.
- Variant style: keep classes appended at the end of the class string, as in
  the table.
- Durations: this plan normalizes press/hover motion to `duration-150`
  (AUDIT.md §2 press budget 100–160ms); where a `duration-200` existed on a
  pressable (rows 8–9), it becomes `duration-150`.

## Steps

1. Apply rows 1–4 (Idiom A) — pure appends, exact strings.
2. Apply rows 5–15 (Idiom B) — replace + append per table.
3. Verify cascade direction (Verification step 3). If `active` loses to
   `hover`, apply the fallback there.
4. `grep -rn "transition-transform" src/` and confirm the remaining hits are
   only non-pressable elements (e.g. image zooms like `Works.astro:137`).

## Boundaries

- Do NOT touch `src/components/WorkshopBooking.astro` (lines 51, 86, 95 have
  the same pattern but the file is explicitly excluded by plans/README.md).
- Do NOT add `:active` to plain text links (`Service.astro:112`,
  `predirect.astro:52` etc.) — press feedback is for buttons/cards, not
  inline links.
- Do NOT introduce any `<style>` block — Tailwind variants only.
- Do NOT change hover directions or shadow sizes at rest.
- If a line doesn't match (drift since 3ed8291), STOP and report.

## Verification

- **Mechanical**: `bun run check` → 0 errors; `bun run build` succeeds;
  `grep -c "active:" src/components/CopyEmail.astro` → 3.
- **Feel check** (`bun run dev`, desktop):
  - press-and-hold the "See Works" pill: it shrinks to 97% under the cursor;
  - press-and-hold a works-rail arrow: it scales to 95% and its 3px shadow
    collapses to 1px;
  - hover a project CTA, then press: it must sink **below** its rest position
    (hover lifts −2px, press drives +2px → net +2px from rest) with a 1px
    shadow. In DevTools, with the pointer down, check the Computed panel:
    `translate: … 2px (0.125rem)` and `box-shadow: 1px 1px 0 #000`.
- **Cascade fallback**: if computed `translate` shows `-2px` while pressed
  (hover beating active), append `!` to the active utilities on the affected
  rows: `active:translate-y-0.5!` and re-check. Record in this plan's status
  note if the fallback was needed.
- **Touch**: in a mobile viewport, tap and hold a CTA — the press state fires
  (there is no hover on touch, so `:active` is the only feedback there).
- **Done when**: every table element shows press feedback, computed-style check
  passes, checks are green.
