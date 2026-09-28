# 012 — Stop animating layout properties (nav underline width, hero arrow bottom)

- **Status**: TODO
- **Commit**: 3ed8291
- **Severity**: MEDIUM
- **Category**: 5. Performance
- **Estimated scope**: 2 files, one class-string edit each, small

**Depends on**: none (works standalone; run after 011 to avoid two agents
editing `Header.astro`).

## Problem

Two high-frequency hover targets animate **layout properties** — `width` on
every nav-link hover, `bottom` on the hero CTA hover. AUDIT.md §5: animate
`transform` and `opacity` only; width/bottom trigger layout + paint.

```astro
<!-- src/components/Header.astro:85 — current -->
class="whitespace-nowrap relative flex items-center before:absolute before:left-0 before:bottom-1 before:h-[8px] before:w-0 before:bg-[var(--yellow)] before:transition-all before:duration-300 hover:before:w-full"
```

The yellow highlight underline grows by tweening `width: 0 → 100%` on a
pseudo-element, via `before:transition-all`. The pseudo is absolutely positioned
so sibling reflow is contained, but it is still a layout+paint tween on the
site's most-hovered element, and `transition-all` on top of it (finding #2).

```astro
<!-- src/components/Button.astro:9 — current -->
<img src={svgHl.src} width="30"  class="absolute -right-7 -bottom-3 transition-all duration-200 group-hover:-bottom-4" />
```

The decorative arrow next to the primary CTA slides by tweening `bottom:
-12px → -16px` (4px) through `transition-all`.

## Target

**Header.astro:85** — same visual (underline wipes left→right over 300ms),
now a composited `scale` tween:

```astro
class="whitespace-nowrap relative flex items-center before:absolute before:left-0 before:bottom-1 before:h-[8px] before:w-full before:origin-left before:scale-x-0 before:bg-[var(--yellow)] before:transition-transform before:duration-300 hover:before:scale-x-100"
```

Diffs vs current, exactly:
- `before:w-0` → `before:w-full` (width is now static; scaling does the motion)
- add `before:origin-left` (so scaleX grows from the left edge — without it the
  origin is center and the wipe grows both ways)
- add `before:scale-x-0`
- `before:transition-all` → `before:transition-transform`
- `hover:before:w-full` → `hover:before:scale-x-100`

Notes: Tailwind v4 scale utilities emit the `scale` property;
`transition-transform` covers `transform, translate, scale, rotate` (confirmed
in built CSS); `scale` respects `transform-origin`, so `before:origin-left` is
required. Keep `before:duration-300` (within the 150–250ms… note: 300ms is the
existing tuned value for this highlight — do not change it; it is an on-screen
morph, and plan 010's strong ease-out already makes it feel snappier).

**Button.astro:9** — same 4px lift, now via `translate`:

```astro
<img src={svgHl.src} width="30" class="absolute -right-7 -bottom-3 transition-transform duration-200 group-hover:-translate-y-1" />
```

Diffs vs current, exactly:
- `transition-all` → `transition-transform`
- `group-hover:-bottom-4` → `group-hover:-translate-y-1`

(`-bottom-3` = -12px, `-bottom-4` = -16px ⇒ the old hover moved the arrow 4px
up; `-translate-y-1` = -4px ⇒ identical motion.)

## Repo conventions to follow

- Variant stacking order like `group-hover:` / `hover:` before the utility is
  the house style — keep it (`group-hover:-translate-y-1`, not
  `-translate-y-1 group-hover:`).
- Exemplar of a correct composited hover in this repo: `Works.astro:137`
  (`group-hover:scale-105 transition-transform duration-300`) — transform-only,
  scoped transition.

## Steps

1. Edit `src/components/Header.astro:85` per Target (one string replacement).
2. Edit `src/components/Button.astro:9` per Target (one string replacement).
3. `grep -rn "transition-all" src/` → **zero** hits (011 must have landed;
   if 011 hasn't run, the two 011-owned `transition-all` sites will still show
   — run 011 too before considering this verified).

## Boundaries

- Do NOT change `before:h-[8px]`, `before:bottom-1`, `before:left-0`,
  `before:bg-[var(--yellow)]`, `before:duration-300` — geometry and timing stay.
- Do NOT touch any other line in either file (plan 013 edits
  `Header.astro:67`'s PritOS button and `Button.astro:8`'s `<a>` — different
  lines).
- Do NOT touch `WorkshopBooking.astro` (excluded).
- If the lines don't match the excerpt (drift since 3ed8291), STOP and report.

## Verification

- **Mechanical**: `bun run check` → 0 errors; `bun run build` succeeds.
- **Feel check** (`bun run dev`, desktop viewport):
  - hover each nav link repeatedly: the yellow bar wipes left→right, growing
    from the left edge (not from center, not right→left) over 300ms; exit wipes
    back the same way;
  - hover the "See Works" CTA: the arrow doodge slides up exactly 4px —
    compare against the pre-change build if unsure; same distance, same 200ms;
  - DevTools → Performance, enable CPU throttling 4×, record while hovering
    nav links: hovering must produce **no Layout (purple)** events for the
    pseudo-element — only Paint/Composite;
  - DevTools → Elements, select the `::before`, check `Computed`: `scale:
    scaleX(0)` at rest, `scaleX(1)` on hover, `width` never changes.
- **Done when**: both hovers look identical to before, `grep -rn
  "transition-all" src/` returns nothing, and no Layout events fire on hover.
