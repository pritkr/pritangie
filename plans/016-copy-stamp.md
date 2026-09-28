# 016 — Copy confirmation: stop the teleport and the width jump

- **Status**: TODO
- **Commit**: 3ed8291
- **Severity**: MEDIUM
- **Category**: 8. Missed opportunities / state indication
- **Estimated scope**: 2 files (`src/components/Hero.astro`,
  `src/components/CopyEmail.astro`), small

**Depends on**: none; run after 013 (shares both files).

## Problem

The copy-to-clipboard confirmation on the site's main conversion actions
teleports twice: the label hard-swaps to "Copied!" in one frame, then hard-swaps
back 2s later. Worse, the strings differ in length, so the bordered button
**changes width twice** — a layout jump on the exact element the user just
clicked.

```js
// src/components/Hero.astro:180-185 — current
if (labelEl) {
  labelEl.textContent = ok ? "Copied!" : original;
  setTimeout(() => {
    labelEl.textContent = original;
  }, 2000);
}
```

```js
// src/components/CopyEmail.astro:69-73 — current
if (labelEl && !isIconOnly) {
  labelEl.textContent = ok ? "Copied!" : "Copy failed";
  setTimeout(() => {
    labelEl.textContent = original;
  }, 2000);
}
```

Markup (the label spans):

```astro
<!-- src/components/Hero.astro:76 — current -->
<span data-copy-label>pritform@gmail.com</span>

<!-- src/components/CopyEmail.astro:30 — current -->
<span data-copy-label>{variant === "icon" ? "" : label}</span>
```

Note: BOTH scripts bind ALL `[data-copy-email]` buttons (each guards with
`dataset.bound`, so whichever runs first owns every button — Hero's script and
CopyEmail's `attachCopyButtons` race). Existing quirk, out of scope to fix —
but it means the animation snippet must be added to BOTH handlers identically,
or behavior would depend on script order.

## Target

### 1. Reserve the width (kills the double resize)

`Hero.astro:76` → the email is 18 chars in a `font-mono` button (ch units are
exact in monospace), "Copied!" is 7:

```astro
<span data-copy-label class="inline-block min-w-[18ch] text-left">pritform@gmail.com</span>
```

`CopyEmail.astro:30` → longest string wins: "Copy failed" = 11 chars
("Copy email" = 10, "Copied!" = 7). The icon variant renders an EMPTY span, so
the min-width must be conditional or the fixed `size-10` icon button would
stretch:

```astro
<span
  data-copy-label
  class={variant === "icon" ? "" : "inline-block min-w-[11ch] text-left"}
>
  {variant === "icon" ? "" : label}
</span>
```

### 2. Animated swap (kills the teleport)

Add this helper INSIDE each click handler, right after the existing
`const original = labelEl?.textContent ?? "";` line (Hero.astro:42 /
CopyEmail.astro:42):

```ts
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const swapLabel = (text: string) => {
  if (!labelEl) return;
  labelEl.textContent = text;
  if (!reduceMotion && labelEl.animate) {
    labelEl.animate(
      [
        { opacity: 0, transform: "translateY(6px)" },
        { opacity: 1, transform: "translateY(0)" },
      ],
      { duration: 160, easing: "cubic-bezier(0.23, 1, 0.32, 1)" },
    );
  }
};
```

Then replace the swap sites:

**Hero.astro** — replace lines 180–185 with (failure keeps the original text,
same semantics as today, but skips the pointless revert timer):

```ts
if (ok) {
  swapLabel("Copied!");
  setTimeout(() => swapLabel(original), 2000);
}
```

**CopyEmail.astro** — replace lines 69–73 with (failure MUST show
"Copy failed", so the revert timer always runs):

```ts
if (labelEl && !isIconOnly) {
  swapLabel(ok ? "Copied!" : "Copy failed");
  setTimeout(() => swapLabel(original), 2000);
} else {
```

(The `} else {` keeps the existing icon-only branch at lines 74–82 untouched.)

Values: 160ms is AUDIT.md §2's button-feedback ceiling; easing
`cubic-bezier(0.23, 1, 0.32, 1)` is plan 010's `--ease-out` written literally
(component JS uses literals — see `BackToTop.astro:14` for the reduce-guard
pattern).

## Repo conventions to follow

- WAAPI (`element.animate`) + `matchMedia("(prefers-reduced-motion: reduce)")`
  guard: `BackToTop.astro:14`, `Works.astro:224`, and plan 014's toast.
- Tailwind arbitrary utilities inline in `class="..."`: the whole repo's style.

## Steps

1. Hero.astro: markup edit (§1), helper insert after line 42, swap-site
   replacement (§2).
2. CopyEmail.astro: markup edit with the CONDITIONAL class (§1), helper insert
   after line 42, swap-site replacement keeping the `else` branch (§2).
3. Confirm both scripts have the snippet:
   `grep -c "swapLabel" src/components/Hero.astro src/components/CopyEmail.astro`
   → ≥ 4 each (definition + call sites).

## Boundaries

- Do NOT touch the icon-only branch (`CopyEmail.astro:74-82`) beyond keeping it
  as the `else` of the edited `if`.
- Do NOT try to de-duplicate the two copy handlers (separate concern; would
  need markup/data-attribute changes).
- Do NOT change the 2000ms revert timing.
- Do NOT touch `WorkshopBooking.astro` (excluded).
- If lines don't match (drift since 3ed8291), STOP and report.

## Verification

- **Mechanical**: `bun run check` → 0 errors; `bun run build` succeeds.
- **Feel check** (`bun run dev`, `/`):
  - click the hero copy-email button: label rises+fades in as "Copied!" over
    160ms; the button width does NOT change (compare button borders before /
    during / after — no horizontal jump);
  - after 2s it swaps back the same way;
  - on `/` scroll to the CTA, click its blue "Copy email": same, and the
    failure path (deny clipboard permission) shows "Copy failed" with the same
    animation, still no width change;
  - DevTools → Animations panel at 10% speed: one 160ms opacity+translate
    animation on the label per swap;
  - Rendering panel → `prefers-reduced-motion: reduce`: text swaps instantly,
    width still reserved (no jump).
- **Done when**: zero visible width change on either button, both swaps
  animate, reduce-motion swaps instantly, checks are green.
