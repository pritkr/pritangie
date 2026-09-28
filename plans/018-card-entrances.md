# 018 — Card entrance stagger on scroll (works rail, blog lists, reviews)

- **Status**: TODO
- **Commit**: 3ed8291
- **Severity**: MEDIUM
- **Category**: 7. Cohesion & tokens / 8. Missed opportunities
- **Estimated scope**: 5 files (1 new component + Layout + 4 call sites), medium

**Depends on**: plan 015 (reduced-motion handling — this component also has
its own guard, so it is safe standalone, but keep the README order).

## Problem

Every card in the site only animates on hover — nothing animates on arrival.
Four bordered, shadowed, rotated objects appear all at once with no spatial
read of "these arrived here" (AUDIT.md §7: group entrances where a 30–80ms
stagger belongs). The Reviews cards are the clearest miss: they carry
scattered `rotate-2`/`-translate-y-10` offsets and look exactly like a dropped
stack that never dropped.

```astro
<!-- src/components/Works.astro:130-131 — current (no entrance) -->
<article
  class="group w-[300px] sm:w-[340px] shrink-0 snap-start flex flex-col bg-white border-2 border-black p-5 relative transition-shadow duration-200 hover:shadow-[4px_4px_0px_rgba(0,0,0,0.3)]"
>
```

(That excerpt reflects plan 011's edit — if 011 hasn't run it still reads
`transition-all duration-200`; the `data-reveal` attribute this plan adds is
unaffected either way.)

Repo-wide grep confirms there is no IntersectionObserver, no `@starting-style`,
and no entrance keyframes anywhere except the command palette dialog.

## Target

One shared reveal component — CSS + one IntersectionObserver — plus a
`data-reveal` attribute on the four card lists. No per-component scripts.

### 1. New file `src/components/Reveal.astro`

```astro
---
// Shared scroll-reveal for [data-reveal] elements. See plans/018.
---

<script is:inline>
  // Runs during parse, BEFORE the slot content below is painted — prevents a
  // visible-then-hidden flash. Absent when JS is disabled, so content simply
  // renders (graceful no-JS fallback).
  document.documentElement.classList.add("reveal-ready");
</script>

<script>
  function initReveal() {
    const targets = document.querySelectorAll<HTMLElement>(
      "[data-reveal]:not(.is-in)",
    );
    if (!targets.length) return;

    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce || !("IntersectionObserver" in window)) {
      targets.forEach((el) => el.classList.add("is-in"));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-in");
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.15 },
    );

    targets.forEach((el, index) => {
      // 50ms stagger (AUDIT.md §7: 30-80ms), cycling within each group of 4.
      el.style.setProperty("--reveal-delay", `${(index % 4) * 50}ms`);
      observer.observe(el);
    });
  }

  initReveal();
  document.addEventListener("astro:page-load", initReveal);
</script>

<style is:global>
  html.reveal-ready [data-reveal] {
    opacity: 0;
    transform: translateY(16px);
    transition:
      opacity 240ms cubic-bezier(0.23, 1, 0.32, 1) var(--reveal-delay, 0ms),
      transform 240ms cubic-bezier(0.23, 1, 0.32, 1) var(--reveal-delay, 0ms);
  }

  html.reveal-ready [data-reveal].is-in {
    opacity: 1;
    transform: translateY(0);
  }

  @media (prefers-reduced-motion: reduce) {
    html.reveal-ready [data-reveal] {
      opacity: 1;
      transform: none;
      transition: none;
    }
  }
</style>
```

Why this shape:

- **`transform`, not `translate`/`rotate`**: Tailwind v4 emits `translate:` and
  `rotate:` as INDEPENDENT properties (verified in built CSS:
  `-translate-y-10 → translate:var(--tw-translate-x) var(--tw-translate-y)`).
  Reviews cards use those utilities for their scatter; animating `transform`
  composes with them instead of clobbering them.
- **`html.reveal-ready` gate**: the class is only added by the inline script —
  with JS off, `[data-reveal]` never hides (no blank page).
- **Transition, not keyframes**: retargets if interrupted and is
  cheaper (AUDIT.md §4). Cards reveal on `opacity` + `transform` only.
- The `astro:page-load` listener matches `CommandPalette.astro:829`'s re-init
  convention (harmless with plain cross-document loads; correct if a client
  router is ever added).

### 2. Mount it in `src/layouts/Layout.astro`

Frontmatter (after the `BackToTop` import, line 10):

```astro
import Reveal from "../components/Reveal.astro";
```

Body (between `ScrollProgress` and `<slot />`, lines 76–77):

```astro
<body>
    <ScrollProgress />
    <Reveal />
    <slot />
```

The component must come BEFORE the slot so the `reveal-ready` class exists
before card markup parses.

### 3. Add `data-reveal` to the four card lists

| File:line | Element | Edit |
|---|---|---|
| `src/components/Works.astro:130-131` | `<article class="group …">` | add `data-reveal` attribute |
| `src/components/RecentBlog.astro:32` | `<a href={url} class="block …">` | add `data-reveal` attribute |
| `src/pages/blog.astro:37` | `<a href={url} class="flex …">` | add `data-reveal` attribute |
| `src/components/Reviews.astro:57` | `<div class={\`flex flex-col gap-3 …\`}>` | add `data-reveal` attribute |

Example (Works):

```astro
<article
  data-reveal
  class="group w-[300px] sm:w-[340px] shrink-0 snap-start flex flex-col bg-white border-2 border-black p-5 relative transition-shadow duration-200 hover:shadow-[4px_4px_0px_rgba(0,0,0,0.3)]"
>
```

For the Reviews template literal, put `data-reveal` before `class={...}`:
`<div data-reveal class={\`flex flex-col gap-3 p-5 pr-15 bg-white border-2 shadow-[6px_6px_0px_rgba(0,0,0,0.3)] ${item.cls}\`}>`

Stagger note: `index` is document order across ALL `[data-reveal]` on the page
— works cards cycle 0/50/100/150ms, reviews get 0/50/100/150ms as a group of
4. Decorative only; it never blocks interaction (the element is clickable
regardless — it is just visually offset; `pointer-events` are never removed).

## Repo conventions to follow

- One concern per component, scripts re-run on `astro:page-load`:
  `CommandPalette.astro:610-613,829`.
- Astro scoped styles default to the component's own markup; since these rules
  target OTHER components' elements, `<style is:global>` is required (same
  reason `CommandPalette.astro:241` uses `:global([hidden])`).

## Steps

1. Create `src/components/Reveal.astro` verbatim from Target §1.
2. Edit `src/layouts/Layout.astro` (import + mount) per Target §2.
3. Add `data-reveal` to the four call sites per Target §3.
4. `grep -rn "data-reveal" src/` → 4 call sites + the component (2 in CSS, 2
   in JS selector strings).

## Boundaries

- Do NOT add per-card scripts or per-component observers.
- Do NOT reveal the hero (plan 017 owns above-the-fold; a scroll observer on
  viewport-top content would double-animate it).
- Do NOT remove or alter the cards' existing hover/rotation classes.
- Do NOT change `threshold` or durations if the feel check feels off — report
  instead.
- Do NOT touch `WorkshopBooking.astro` (excluded).
- If cited lines don't match (drift since 3ed8291), STOP and report.

## Verification

- **Mechanical**: `bun run check` → 0 errors; `bun run build` succeeds.
- **Feel check** (`bun run dev`):
  - load `/`, scroll to "My Works": cards rise 16px + fade in as they enter,
    staggered ~50ms apart (first four);
  - scroll to Reviews: the four scattered cards settle in sequence — reads as a
    stack being laid down; rotations/offsets are untouched;
  - scroll to RecentBlog and `/blog`: same rise-in;
  - **spam scroll up/down across a section boundary**: elements that already
    revealed stay revealed (unobserve) — nothing re-hides or re-flickers;
  - horizontal: in the works rail, cards off to the right reveal when scrolled
    into view (`threshold: 0.15`), not before;
  - DevTools → Rendering → `prefers-reduced-motion: reduce`: cards are simply
    visible, no movement;
  - **disable JS (DevTools → Settings → Disable JavaScript), reload**: all
    cards visible immediately (no `reveal-ready` class → no hidden state);
  - DevTools → Performance at 4× CPU throttle: the reveal runs on
    opacity/transform compositing — scrolling stays smooth (no layout thrash).
- **Done when**: all four lists stagger in on scroll, the no-JS and
  reduce-motion paths show content instantly, checks are green.
