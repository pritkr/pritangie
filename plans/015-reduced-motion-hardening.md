# 015 — Global reduced-motion hardening + remove the pointless pings

- **Status**: TODO
- **Commit**: 3ed8291
- **Severity**: MEDIUM
- **Category**: 6. Accessibility + 1. Purpose & frequency
- **Estimated scope**: 2 files (`src/styles/global.css`, `src/components/Works.astro`), small

## Problem

Three separate gaps:

1. **`html { scroll-behavior: smooth }` has no reduced-motion gate.**
   `src/layouts/Layout.astro:97` smooth-scrolls every anchor navigation for
   users who asked the OS for less motion. The one JS scroll that respects it
   (`BackToTop.astro:14`) is fine; the CSS global is not.

2. **Most motion has no reduced-motion branch.** Grep confirms the only
   per-component guards are `Tools.astro:29-31` (marquee),
   `CommandPalette.astro:587-596`, and `PredirectDemo.astro:430-437`. Every
   hover lift, the mobile drawer (`Header.astro:101`), and the back-to-top
   reveal run at full tilt under `prefers-reduced-motion: reduce`.

```css
/* src/layouts/Layout.astro:90-98 — current */
html,
body {
    margin: 0;
    width: 100%;
    height: 100%;
    background-color: var(--main-bg);
    font-family: "Space Grotesk", sans-serif;
    scroll-behavior: smooth;
}
```

3. **`animate-ping` runs forever with no state to communicate.**
   `Works.astro:155` puts a Tailwind `animate-ping` pulse inside every project
   card that has a repo — seven simultaneous infinite pulses on a horizontal
   rail, none of them indicating a state change (the badge text already says
   "on GitHub"). It is also the only perpetual animation in the repo with no
   reduce gate. AUDIT.md §1: decorative motion on constantly-visible elements
   is a finding; the strongest fix is often deletion. The Hero's single
   "open to work" ping (`Hero.astro:61`) is kept — one status dot on a rare
   high-emotion badge earns its keep, and this plan's global block gates it.

## Target

### 1. One global reduced-motion block in `src/styles/global.css`

Append after the `@theme` block added by plan 010 (this file is loaded on every
page — see plans/010 Problem for the import list):

```css
@media (prefers-reduced-motion: reduce) {
  html {
    scroll-behavior: auto !important;
  }
  *,
  *::before,
  *::after {
    /* Keep color/opacity feedback; drop movement (position/transform) and endless loops. */
    transition-property: opacity, color, background-color, border-color,
      box-shadow, text-decoration-color, outline-color, fill, stroke !important;
    transition-duration: 150ms !important;
    animation-duration: 1ms !important;
    animation-delay: 0ms !important;
    animation-iteration-count: 1 !important;
  }
}
```

Why this shape (AUDIT.md §6): reduced motion means *fewer and gentler*
animations, **not zero** — so transitions are not nuked; instead the property
list is narrowed to color/opacity-class properties (movement snaps instantly,
feedback still fades in over 150ms). Animations collapse to a single 1ms frame,
which lands `both`-filled entrance animations (plans 017/018) on their final
state instantly, freezes the marquee (which already sets `animation: none` —
unaffected) and the Hero ping (ends at its keyframe's `opacity: 0`, leaving the
solid dot beneath). `!important` is required to beat Layout.astro's
`scroll-behavior: smooth` and component styles that set `transition: none`
(which would otherwise re-enable… note: our narrowed property list re-enabling
color fades on those elements is harmless).

### 2. Delete the pings in `src/components/Works.astro`

Current (lines 154–157, inside every card's badge):

```html
<span class="relative flex size-2">
  <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-500 opacity-75"></span>
  <span class="relative inline-flex size-2 rounded-full bg-green-600"></span>
</span>
```

Target:

```html
<span class="relative flex size-2">
  <span class="relative inline-flex size-2 rounded-full bg-green-600"></span>
</span>
```

(Keep the wrapper and the solid `bg-green-600` dot — only the pulsing span is
removed. There are 8 cards; this is ONE template occurrence in the file, hit
once.)

## Repo conventions to follow

- Exemplar for a scoped guard already in the repo: `Tools.astro:29-33`
  (`@media (prefers-reduced-motion: reduce) { … animation: none; }`) — this
  plan adds the repo-wide version because per-component guards are missing in
  10+ places.
- `global.css` is the shared stylesheet (imported everywhere); global media
  queries belong here, not in Layout.astro's component-scoped `<style>`.

## Steps

1. Add the `@media (prefers-reduced-motion: reduce)` block to
   `src/styles/global.css`, after the `@theme` block (plan 010 — if 010 hasn't
   run, add it at the end of the file and note the ordering in status).
2. Apply the Works.astro ping deletion (Target §2).
3. Leave `Hero.astro:61`'s ping in place (deliberate).
4. Leave the existing per-component reduce blocks alone (redundant, harmless).

## Boundaries

- Do NOT remove the Hero "open to work" ping.
- Do NOT touch `Tools.astro`, `PredirectDemo.astro`, or `CommandPalette.astro`
  reduce blocks.
- Do NOT add `@media (hover: hover)` gating to Tailwind `hover:` utilities —
  Tailwind v4 ALREADY gates every `hover:` utility behind
  `@media (hover:hover)` (verified in `dist/_astro/Footer.*.css`:
  `.hover\:-translate-y-0\.5:hover{…}` is emitted inside `@media (hover:hover)`).
  The only ungated raw `:hover` rules live in `PredirectDemo.astro:232-239` and
  `CommandPalette.astro:267,377,446` — leaving them is accepted (LOW; the
  palette trigger is `display:none` under 768px anyway). Record this in
  plans/README.md as a refuted finding.
- Do NOT touch `WorkshopBooking.astro` (excluded).

## Verification

- **Mechanical**: `bun run build` succeeds; `grep -c "animate-ping"
  src/components/Works.astro` → 0; `grep -c "animate-ping" src/components/Hero.astro`
  → 1.
- **Feel check** (`bun run dev`):
  - DevTools → Rendering → emulate `prefers-reduced-motion: reduce`:
    - anchor navigation (nav links, "See Works") jumps instantly — no smooth
      scroll;
    - hovering cards/nav: the lift/underline **does not move**, but the yellow
      underline and yellow link highlights still *appear* (color feedback
      survives at 150ms);
    - works rail: zero pulsing dots; Hero's single "open to work" dot is static
      (its ping animation collapses to 1ms/1 iteration);
    - marquee: static (pre-existing behavior unchanged).
  - Without reduce emulation: nothing about normal motion changed — rail badges
    show a static green dot, Hero ping still pulses.
- **Done when**: reduce emulation shows no movement anywhere (colors still
  fade), Works has no `animate-ping`, normal mode looks unchanged otherwise.
