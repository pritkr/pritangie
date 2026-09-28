# 017 — Hero entrance choreography (the front door currently renders static)

- **Status**: TODO
- **Commit**: 3ed8291
- **Severity**: HIGH
- **Category**: 8. Missed opportunities (rare/first-time delight)
- **Estimated scope**: 1 file (`src/components/Hero.astro`), small–medium

**Depends on**: plan 015 (its global reduced-motion block is what parks these
animations instantly — without 015, reduce users see the full entrance).

## Problem

The entire above-the-fold of the site's front door — logo, h1 with the yellow
"human" highlight, sub-paragraph, badges, CTAs, photo card — is static on first
paint. Repo-wide grep finds zero entrance motion anywhere
(no `opacity-0`/`animate-*`/`@starting-style`/IntersectionObserver outside the
command palette's 180ms dialog). Per AUDIT.md §1, a rare/first-time moment can
earn delight; this one gets none, so the page reads as "already finished
loading" rather than arriving.

```astro
<!-- src/components/Hero.astro:26-40 — current -->
<section class="pb-20 relative">
  <div class="max-w-4xl mx-auto p-4 pt-20 md:pt-30">
    <div class="grid grid-cols-1 md:grid-cols-[60%_40%] items-center">
      <div class="flex flex-col gap-4 pr-0 md:pr-10">
        <img src={svgheroContent.src} alt="logo" width="80" />
        <h1 class="text-5xl font-medium">
          <span>I build tech <br /> that feels</span>
          <span class="relative">
            <span
              class="absolute bg-[var(--yellow)] w-full h-[50%] left-0 bottom-0 z-1"
            ></span>
            <span class="relative z-5">human</span>
          </span>
        </h1>
```

## Target

Pure CSS (no JS, works without scripts). Add a `<style>` block to
`Hero.astro` (before the existing `<script>` at line 154):

```css
<style>
  .hero-enter {
    animation: hero-enter 240ms cubic-bezier(0.23, 1, 0.32, 1) both;
  }

  @keyframes hero-enter {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .hero-highlight {
    animation: hero-wipe 240ms cubic-bezier(0.23, 1, 0.32, 1) 250ms both;
  }

  @keyframes hero-wipe {
    from {
      clip-path: inset(0 100% 0 0);
    }
    to {
      clip-path: inset(0 0 0 0);
    }
  }
</style>
```

Values: 240ms + `cubic-bezier(0.23, 1, 0.32, 1)` = AUDIT.md §2 strong ease-out
for entrances (under the 300ms UI budget); stagger 50ms per group (AUDIT.md §7:
30–80ms); the highlight wipe uses `clip-path: inset()` (AUDIT.md §8's suggested
tool) so it reads as a marker stroke left→right — `inset(0 100% 0 0)` is
`top right bottom left`, so right=100% collapses the visible region to the left
edge and it grows rightward.

### Element → class → delay table

Add `hero-enter` to the class list and `style="animation-delay: Nms"` to each:

| Element (current line) | Current class/attrs | Add |
|---|---|---|
| logo `<img>` (30) | no class attr | `class="hero-enter"` + `style="animation-delay: 0ms"` (omit the style attr — 0 is default) |
| `<h1>` (32) | `class="text-5xl font-medium"` | ` hero-enter` + `style="animation-delay: 50ms"` |
| sub-paragraph `<p>` (41) | `class="text-xl"` | ` hero-enter` + `style="animation-delay: 100ms"` |
| badge row `<div>` (46) | `class="flex flex-wrap items-center gap-2 text-sm mt-3"` | ` hero-enter` + `style="animation-delay: 150ms"` |
| CTA/socials `<div>` (53) | `class="flex flex-wrap items-center gap-8 mt-5"` | ` hero-enter` + `style="animation-delay: 200ms"` |
| copy-email row `<div>` (68) | `class="mt-4 flex flex-wrap items-center gap-3"` | ` hero-enter` + `style="animation-delay: 250ms"` |
| photo column `<div>` (81) | `class="relative mt-40 md:mt-0"` | ` hero-enter` + `style="animation-delay: 150ms"` |
| yellow highlight `<span>` (35–37) | `class="absolute bg-[var(--yellow)] w-full h-[50%] left-0 bottom-0 z-1"` | ` hero-highlight` (delay is baked into the CSS — do NOT add an inline delay) |

Resulting excerpt for the h1 (pattern for all rows):

```astro
<h1 class="text-5xl font-medium hero-enter" style="animation-delay: 50ms">
```

Safety notes:
- Keyframes animate `transform`; none of these elements carry Tailwind
  translate/rotate/scale utilities, so nothing is clobbered (the `-rotate-30
  translate-y-3` name badge at line 84 is a DESCENDANT of the animated photo
  column — a parent `transform` composes with children's own
  translate/rotate properties, which is correct: the whole card rises together).
- `both` fill means elements are invisible (opacity 0) until their delay
  passes — max delay is 250ms.
- Under reduced motion, plan 015's global block forces
  `animation-duration: 1ms !important; animation-delay: 0ms !important` → the
  entrance lands on its final frame instantly.

## Repo conventions to follow

- Component-scoped `<style>` blocks with literal curves are the house pattern:
  `Tools.astro:19-34`, `CommandPalette.astro:547-556`. Astro scopes the
  `.hero-enter` selector to this component's elements automatically.
- The one existing keyframe entrance in the repo —
  `CommandPalette.astro:547-556` (`opacity 0 → 1` + small translate + scale,
  ease-out) — is the tone reference: short, small offsets, no bounce.

## Steps

1. Add the `<style>` block (Target) immediately before Hero's `<script>` tag.
2. Apply the 8-row class/attribute table.
3. `grep -c "hero-enter" src/components/Hero.astro` → ≥ 8 (7 classes + 1
   keyframe name reference… expect 9 with the `.hero-enter` rule; just confirm
   ≥ 8).
4. `grep -c "hero-highlight" src/components/Hero.astro` → 2 (rule + usage).

## Boundaries

- Do NOT add JS/IntersectionObserver — above-the-fold content must animate on
  pure CSS (works with scripts disabled).
- Do NOT touch the `socials` list, the copy-email script, or any content/wording.
- Do NOT animate the whole `<section>` as one block — the stagger IS the
  design.
- Do NOT add spring/bounce curves — this site's personality is crisp.
- If lines don't match (drift since 3ed8291), STOP and report.

## Verification

- **Mechanical**: `bun run check` → 0 errors; `bun run build` succeeds.
- **Feel check** (`bun run dev`, hard-reload `/` several times):
  - logo → h1 → paragraph → badges → CTAs → copy button rise in sequence
    (50ms apart), photo card joins at 150ms; total choreography ≈ 500ms;
  - the yellow highlight under "human" wipes in left→right like a marker
    stroke, after the h1 has landed;
  - DevTools → Animations panel, 10% speed: each element shows one 240ms
    `hero-enter` animation; the highlight shows `hero-wipe` starting at 250ms;
    no element is stuck at opacity 0 after its delay;
  - Rendering panel → `prefers-reduced-motion: reduce` (plan 015 must be
    applied): everything is visible immediately, only the final frame;
  - disable JavaScript and reload: entrance still plays (CSS-only);
  - navigate away to `/about` and back: the entrance replays on load — that is
    expected for a cross-document view transition and reads as a fresh arrival.
- **Done when**: the sequence plays as specced, reduce-motion parks it, and
  checks are green.
