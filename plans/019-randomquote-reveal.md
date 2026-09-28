# 019 — RandomQuote: reserve the height, reveal the quote like a receipt

- **Status**: TODO
- **Commit**: 3ed8291
- **Severity**: MEDIUM
- **Category**: 8. Missed opportunities (state change that teleports) / 5. Performance (CLS)
- **Estimated scope**: 1 file (`src/components/RandomQuote.astro`), small

## Problem

The quote card SSRs with an empty blockquote and is filled by script — the
full-height bordered card collapses to its padding, then jumps to multi-line
height when the module executes. A visible layout teleport plus CLS, on content
that is deliberately a "moment" (a quote picked for you).

```astro
<!-- src/components/RandomQuote.astro:27-33 — current -->
<blockquote class="text-center">
    <p
        id="quote-text"
        class="text-xl md:text-2xl font-medium leading-relaxed italic mb-4"
    ></p>
    <footer id="quote-author" class="text-lg font-bold"></footer>
</blockquote>
```

```js
// src/components/RandomQuote.astro:81-83 — current
const quote = quotes[Math.floor(Math.random() * quotes.length)]!;
document.getElementById("quote-text")!.textContent = `"${quote.text}"`;
document.getElementById("quote-author")!.textContent = `— ${quote.author}`;
```

There is no entrance animation on either element — the text simply appears.

## Target

### 1. Reserve the height (kills the jump for all but the longest quote)

```astro
<blockquote class="text-center min-h-[10rem]">
```

`min-h-[10rem]` (160px) covers a 3-line quote at `text-2xl` (≈117px) + the
`mb-4` gap + the author line at desktop, and most quotes on mobile
(`text-xl`). See Verification for the one known exception.

### 2. Reveal on fill (kills the teleport)

Replace lines 81–83 with:

```js
const quote = quotes[Math.floor(Math.random() * quotes.length)]!;
const quoteEl = document.getElementById("quote-text")!;
const authorEl = document.getElementById("quote-author")!;
quoteEl.textContent = `"${quote.text}"`;
authorEl.textContent = `— ${quote.author}`;

const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
if (!reduceMotion && quoteEl.animate) {
  // Curtain drops top -> bottom, like a receipt printing out of the card.
  quoteEl.animate(
    [
      { clipPath: "inset(0 0 100% 0)", transform: "translateY(-4px)" },
      { clipPath: "inset(0 0 0 0)", transform: "translateY(0)" },
    ],
    { duration: 240, easing: "cubic-bezier(0.23, 1, 0.32, 1)" },
  );
  authorEl.animate(
    [
      { opacity: 0, transform: "translateY(4px)" },
      { opacity: 1, transform: "translateY(0)" },
    ],
    {
      duration: 240,
      delay: 60,
      easing: "cubic-bezier(0.23, 1, 0.32, 1)",
      fill: "backwards",
    },
  );
}
```

Values: 240ms + `cubic-bezier(0.23, 1, 0.32, 1)` — the same entrance spec as
plan 017 (AUDIT.md §2 strong ease-out, <300ms); author 60ms behind the quote
(AUDIT.md §7 stagger 30–80ms). `clip-path: inset(top right bottom left)`:
starting at `inset(0 0 100% 0)` the bottom inset is 100% (nothing visible,
region anchored at the top) and closing it reveals downward — the hard-edged
wipe AUDIT.md §8 suggests, no soft fade. `fill: "backwards"` keeps the author
invisible during its 60ms delay. WAAPI + reduce guard is the repo pattern
(`BackToTop.astro:14`, plan 014/016).

## Repo conventions to follow

- Component-scoped script with `!` non-null assertions on getElementById —
  keep that style.
- Hard-edged motion (clip/translate), never bounce — see
  `CommandPalette.astro:547-556` for the house entrance tone.

## Steps

1. Add `min-h-[10rem]` to the `<blockquote>` (line 27).
2. Replace script lines 81–83 with Target §2 verbatim.
3. `grep -c "min-h-\[10rem\]" src/components/RandomQuote.astro` → 1;
   `grep -c "clipPath" src/components/RandomQuote.astro` → 2.

## Boundaries

- Do NOT switch to build-time (SSR) quote selection — random-per-load is the
  current product behavior; this plan keeps it.
- Do NOT restructure or reword the quotes array.
- Do NOT add a JS-side height measurement/resize — `min-h` only.
- If lines don't match (drift since 3ed8291), STOP and report.

## Verification

- **Mechanical**: `bun run check` → 0 errors; `bun run build` succeeds.
- **Feel check** (`bun run dev`, `/`, reload ~10×):
  - the card renders at full reserved height immediately (DevTools → Performance:
    no layout shift at the quote between first paint and script execution);
  - the quote prints downward out of the top of the blockquote over 240ms,
    author fades up 60ms later;
  - reload until the long Snowden privacy quote appears — it may still exceed
    `10rem` and grow the card once (known, accepted); if it reads badly, bump
    to `min-h-[11rem]` and re-check, noting the change in this plan's status;
  - Rendering → `prefers-reduced-motion: reduce`: text appears instantly,
    height still reserved;
  - DevTools → Animations at 10%: one 240ms clip-path animation, author
    starting at +60ms.
- **Done when**: no card-height jump on typical loads, the reveal plays,
  reduce-motion is instant, checks are green.
