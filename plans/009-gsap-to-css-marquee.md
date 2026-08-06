# Plan 009: Replace the GSAP marquee with CSS and drop the GSAP dependency

> **Executor instructions**: Follow this plan step by step. Run every verification
> command and confirm the expected result before moving to the next step. Touch
> only the files listed as in scope. If any STOP condition occurs, stop
> immediately and report — do not improvise. When done, update the status row
> for this plan in `plans/README.md` unless a reviewer maintains the index.
>
> **Drift check (run first)**: `git diff --stat 05c4424..HEAD -- src/components/Tools.astro package.json`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: MED
- **Depends on**: none (run after 008 if landed, so the result typechecks)
- **Category**: tech-debt
- **Planned at**: commit `05c4424`, 2026-08-03

## Why this matters

The site's footer promises "No trackers · No cookies · Built with Astro"
(`src/components/Footer.astro:32-34`), marketing minimalism and privacy. Yet
`gsap` (a large animation library) is a production dependency
(`package.json:14`) used for exactly one effect: an infinite horizontal marquee
in `Tools.astro`. The effect is a pure linear infinite scroll
(`gsap.timeline({ repeat: -1 }).to(el, { x: -(scrollWidth/2), duration: 30, ease: 'none' })`
— `Tools.astro:17-20`), which CSS keyframes replicate exactly with no
JavaScript and no library. Removing GSAP shrinks the shipped JS, removes a
dependency to maintain, and makes the site's "minimal" claim true. GSAP is
imported nowhere else in `src/` (confirmed: only `src/components/Tools.astro:7`
imports it).

## Current state

Full file `src/components/Tools.astro` (37 lines):

```astro
---
const mytools = [
  'Figma', 'React', 'Astro', 'Tailwind CSS', 'Python', 'Canva', 'C', 'C++(DSA)', 'Go', 'Linux', 'Bash', 'Git', 'PostgreSQL'
]
---
<script>
  import { gsap } from 'gsap';

  document.addEventListener('DOMContentLoaded', function () {
    const clonedContainer = document.querySelector('#cloned') as any

    Array.from(clonedContainer.children).forEach((img: any) => {
      const clone = img.cloneNode(true); 
      clonedContainer.appendChild(clone)
    })

    const tl = gsap.timeline({ repeat: -1 });
    tl.to(clonedContainer, {
      x: -(clonedContainer.scrollWidth / 2),  duration: 30, ease: 'none'
    })
  });
</script>
  

<section class="bg-black py-6 relative z-5">
    <div class="overflow-hidden">
        <div class="flex items-center gap-10 md:gap-30" id="cloned">
            {mytools.map(item => (
              <div class="text-white flex-1 text-2xl whitespace-nowrap"> {item} </div>
            ))}
        </div>
    </div>
</section>
```

- The script clones all children once (doubling the list) then animates `x` from
  `0` to `-(scrollWidth/2)` over 30s, looping forever — the second half scrolls
  into view seamlessly.
- `package.json:14` — `"gsap": "^3.15.0"`.
- The build currently succeeds with 8 pages (verified).

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Build | `bun run build` | exit 0; 8 pages |
| No gsap import | `grep -rn "gsap" src` | no matches |
| No gsap dep | `grep '"gsap"' package.json` | no match after removal |
| (if 008 landed) Typecheck | `bun run check` | exit 0 |

## Scope

In scope: `src/components/Tools.astro`, `package.json` (remove the `gsap` dep).

Out of scope: workshop files, any other component, the marquee copy, the visual
design beyond preserving the scroll, `src/sample.ts`.

## Steps

### Step 1: Replace the GSAP script with a CSS animation

Rewrite `Tools.astro` so the doubled list is produced in markup (render
`mytools` twice via `{[...mytools, ...mytools].map(...)}`) and the animation is a
CSS keyframe. Remove the entire `<script>` block. Add a scoped `<style>`:

```css
.marquee { display: flex; width: max-content; animation: marquee 30s linear infinite; }
@keyframes marquee { from { transform: translateX(0); } to { transform: translateX(-50%); } }
```

Set the inner track `<div class="marquee ...">` to render the doubled list.
`translateX(-50%)` is seamless because the doubled content makes "50% of the
track width" exactly one full list width. Keep `overflow-hidden`, `bg-black`,
`gap`, and `whitespace-nowrap` on the items so the look is preserved.

**Verify**:
- `bun run build` -> exit 0.
- `grep -rn "gsap" src` -> no matches.
- (Manual/visual via `bun run preview`) the marquee still scrolls infinitely
  with no visible jump at the loop boundary.

### Step 2: Remove the GSAP dependency

Run `bun remove gsap`.

**Verify**:
- `grep '"gsap"' package.json` -> no match.
- `bun run build` -> exit 0, 8 pages.
- (If 008 landed) `bun run check` -> exit 0.

## Test plan

No unit tests in this repo. Acceptance: build passes, no `gsap` reference
remains in `src` or `package.json`, and the marquee visibly scrolls the same
way as before (open the built site, confirm continuous motion with no jump).

## Done criteria

- [ ] `bun run build` exits 0, 8 pages
- [ ] `grep -rn "gsap" src` returns no matches
- [ ] `grep '"gsap"' package.json` returns no match
- [ ] The marquee still animates as an infinite linear scroll (manual/visual check)
- [ ] No files outside `src/components/Tools.astro` and `package.json` are modified
- [ ] Workshop files unchanged

## STOP conditions

- Stop if removing GSAP breaks the build in a way unrelated to the marquee
  (GSAP may be transitively relied on) — report it.
- Stop if the CSS `translateX(-50%)` approach does not produce a seamless loop
  (e.g., flex `gap` adds to width and offsets the wrap) — do not ship a janky
  marquee. Report it; a pixel-value animation keyed to `scrollWidth` is the
  fallback, but try the `%` approach first.
- Stop if the marquee's visual identity (speed, direction, content) cannot be
  matched.

## Maintenance notes

- Adding new tools to `mytools` still Just Works — the track auto-doubles.
- If a richer animation is ever needed elsewhere, re-evaluate reintroducing a
  library; until then, prefer CSS.
- The `<style>` is scoped to `Tools.astro` by Astro, so the `@keyframes marquee`
  name will not collide with other pages.
