# 020 — Replace the default view-transition crossfade with a hard wipe

- **Status**: TODO
- **Commit**: 3ed8291
- **Severity**: LOW
- **Category**: 7. Cohesion & tokens (motion personality)
- **Estimated scope**: 1 file (`src/layouts/Layout.astro`), small

## Problem

Cross-page navigation uses the browser's stock cross-document view transition —
a 250ms crossfade that double-exposes two full pages (AUDIT.md §7: jarring
crossfades that show two overlapping states) and is a soft dissolve in a design
language built from hard edges and offset shadows. It is the only
view-transition rule in the repo:

```css
/* src/layouts/Layout.astro:99-101 — current */
@view-transition {
	navigation: auto;
}
```

There are no `::view-transition-old/new` rules anywhere (`grep -rn
"view-transition" src/` → this one hit), so the UA default applies.

## Target

Keep the activation, define the wipe (tab indentation matches the file's
existing `<style>` block):

```css
@view-transition {
	navigation: auto;
}

::view-transition-old(root) {
	animation: none;
}

::view-transition-new(root) {
	animation: vt-wipe 200ms cubic-bezier(0.23, 1, 0.32, 1) both;
}

@keyframes vt-wipe {
	from {
		clip-path: inset(0 100% 0 0);
	}
	to {
		clip-path: inset(0 0 0 0);
	}
}

@media (prefers-reduced-motion: reduce) {
	::view-transition-old(root),
	::view-transition-new(root) {
		animation: none;
	}
}
```

How it works, so the executor doesn't "fix" it:

- `::view-transition-old(root) { animation: none }` removes the UA fade — the
  outgoing page's snapshot stays frozen and fully visible underneath.
- `::view-transition-new(root)` is stacked above it and wipes in from the LEFT
  edge: `clip-path: inset(top right bottom left)` starting at
  `inset(0 100% 0 0)` = right inset 100% (zero-width region anchored left),
  closing to `inset(0)` reveals left→right over 200ms. New page over static old
  — no double-exposure, no dissolve.
- 200ms + `cubic-bezier(0.23, 1, 0.32, 1)`: AUDIT.md §2 strong ease-out; page
  navigation is occasional, well inside the 200–500ms allowance.
- The explicit reduce-media query is required: plan 015's global `*` block
  cannot reach pseudo-elements in the view-transition overlay tree.
- Browsers without cross-document view transitions (e.g. Safari < 18.2) ignore
  all of this and perform a plain navigation — no breakage, just no wipe.

## Repo conventions to follow

- Tab indentation inside Layout.astro's `<style>` block (the file uses tabs
  there — match lines 90–98).
- Literal curves in component styles (house pattern; see plan 017).

## Steps

1. In `src/layouts/Layout.astro`, replace the `@view-transition { … }` rule
   (lines 99–101) with the full Target block verbatim.
2. `grep -n "vt-wipe" src/layouts/Layout.astro` → keyframe + usage hits.

## Boundaries

- Do NOT add `view-transition-name` to any element — root-only wipe, whole
  page moves as one sheet.
- Do NOT touch anything else in the style block (`html, body`,
  `scroll-behavior` — that is plan 015's concern).
- Do NOT animate individual sections/cards per page (would need
  `view-transition-name` plumbing — explicitly out of scope).
- If the rule doesn't match (drift since 3ed8291), STOP and report.

## Verification

- **Mechanical**: `bun run build` succeeds; `bun run check` → 0 errors.
- **Feel check** (`bun run dev`):
  - click "Blog" in the nav: the blog page wipes in left→right over 200ms on
    top of the frozen home page — no ghosted/double-exposed crossfade;
  - go Back: wipe plays again in the reverse-navigation direction the browser
    assigns (still a wipe, never a dissolve);
  - DevTools → Animations panel during a nav: one ~200ms `vt-wipe` on
    `::view-transition-new(root)`, no animation on `old(root)`;
  - Rendering → `prefers-reduced-motion: reduce`: navigation is instant (both
    pseudo-elements `animation: none`);
  - DevTools → Rendering → check `prefers-reduced-motion` OFF again and feel
    it at slow CPU (4× throttle): wipe stays smooth (clip-path on the root
    snapshot is compositor-friendly in Chromium).
- **Done when**: every in-site navigation wipes instead of crossfading,
  reduce-motion navigates instantly, checks are green.
