# 014 — Animate the command palette exit and the toast in/out

- **Status**: TODO
- **Commit**: 3ed8291
- **Severity**: MEDIUM
- **Category**: 4. Interruptibility (asymmetric enter/exit, teleporting toast)
- **Estimated scope**: 1 file (`src/components/CommandPalette.astro`), small–medium

## Problem

The palette **enters** over 180ms but **exits by teleport** — `setOpen(false)`
flips `hidden` immediately, so the dialog vanishes in one frame while its
entrance took 180ms. The confirmation toast teleports on both edges (shown and
hidden by `hidden` toggles with no motion at all).

```js
// src/components/CommandPalette.astro:676-693 — current
const setOpen = (open: boolean) => {
  palette.hidden = !open;
  palette.setAttribute("aria-hidden", String(!open));
  trigger.setAttribute("aria-expanded", String(open));

  if (open) {
    previouslyFocused = document.activeElement as HTMLElement | null;
    previousOverflow = document.body.style.overflow;
    document.body.classList.add("command-palette-open");
    search.value = "";
    filterItems();
    window.setTimeout(() => search.focus(), 0);
  } else {
    document.body.classList.remove("command-palette-open");
    document.body.style.overflow = previousOverflow;
    previouslyFocused?.focus();
  }
};
```

```js
// src/components/CommandPalette.astro:717-724 — current
const showToast = (message: string) => {
  window.clearTimeout(toastTimer);
  toast.textContent = message;
  toast.hidden = false;
  toastTimer = window.setTimeout(() => {
    toast.hidden = true;
  }, 2200);
};
```

A 180ms entrance followed by a 0ms exit reads as a glitch, not a decision —
especially on the keyboard-driven ⌘K path. Modals are the "occasional"
frequency class and get standard motion (AUDIT.md §1); the entrance is already
correct (scale 0.98, not 0 — keep it).

## Target

### 1. CSS — exit keyframes (add inside the existing `<style>` block, after
the `command-palette-enter` keyframes at lines 547–556)

```css
@keyframes command-palette-exit {
  from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateY(-0.75rem) scale(0.98);
  }
}

@keyframes backdrop-enter {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes backdrop-exit {
  from { opacity: 1; }
  to { opacity: 0; }
}

.command-palette-backdrop {
  animation: backdrop-enter 180ms cubic-bezier(0.23, 1, 0.32, 1) both;
}

.command-palette-shell.is-closing .command-palette-dialog {
  animation: command-palette-exit 150ms cubic-bezier(0.23, 1, 0.32, 1) both;
}

.command-palette-shell.is-closing .command-palette-backdrop {
  animation: backdrop-exit 150ms cubic-bezier(0.23, 1, 0.32, 1) both;
}
```

Notes:
- The exit mirrors the entrance (`command-palette-enter`, lines 547–556) at
  150ms — shorter than the 180ms enter, which is fine (exits may be quicker);
  easing is `cubic-bezier(0.23, 1, 0.32, 1)` (AUDIT.md §2: entering **or
  exiting** → ease-out; token from plan 010, but write the literal here — this
  is a component-scoped stylesheet, not a Tailwind utility).
- The backdrop previously popped in/out with the `hidden` toggle; it now fades
  with the same curve on both edges. The `.command-palette-backdrop` rule
  above MERGES with the existing rule at lines 305–313 (same selector) — add
  the `animation` declaration to it rather than creating a duplicate rule, or
  append the new rule after it; either is fine, but there must be exactly one
  `.command-palette-backdrop { … }` block with the animation.
- The specificity of `.command-palette-shell.is-closing .command-palette-backdrop`
  (0,3,0) beats `.command-palette-backdrop` (0,1,0), so the exit wins during
  close.

### 2. JS — replace `setOpen` (lines 676–693) with this exact function

```ts
let closeTimer: number | undefined;
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

const setOpen = (open: boolean) => {
  window.clearTimeout(closeTimer);
  palette.classList.remove("is-closing");
  trigger.setAttribute("aria-expanded", String(open));

  if (open) {
    palette.hidden = false;
    palette.setAttribute("aria-hidden", "false");
    previouslyFocused = document.activeElement as HTMLElement | null;
    previousOverflow = document.body.style.overflow;
    document.body.classList.add("command-palette-open");
    search.value = "";
    filterItems();
    window.setTimeout(() => search.focus(), 0);
    return;
  }

  document.body.classList.remove("command-palette-open");
  document.body.style.overflow = previousOverflow;
  previouslyFocused?.focus();
  palette.setAttribute("aria-hidden", "true");

  const finishClose = () => {
    palette.hidden = true;
    palette.classList.remove("is-closing");
  };

  if (reduceMotion.matches) {
    finishClose();
    return;
  }
  palette.classList.add("is-closing");
  closeTimer = window.setTimeout(finishClose, 150);
};
```

Declare `closeTimer` and `reduceMotion` alongside the existing state at lines
630–633 (`let activeIndex = 0;` … `let toastTimer: number | undefined;`) — not
inside `setOpen`.

Behavioral contract:
- Close: aria/body/focus cleanup happens immediately (screen readers and scroll
  unlock must not wait 150ms); the shell stays visible for 150ms playing the
  exit, then `hidden` flips.
- Reopen during the exit: the timer is cleared and `is-closing` removed at the
  top of `setOpen` — the dialog snaps back to its completed enter state
  (interruptible, no stuck palette). Do NOT add animation-restart hacks.
- Reduce motion: hide immediately, no timer (existing `animation: none` rules
  at lines 587–596 already kill the enter).

### 3. JS — replace `showToast` (lines 717–724) with this exact function

```ts
const showToast = (message: string) => {
  window.clearTimeout(toastTimer);
  toast.getAnimations?.().forEach((animation) => animation.cancel());
  toast.textContent = message;
  toast.hidden = false;

  if (!reduceMotion.matches && toast.animate) {
    toast.animate(
      [
        { opacity: 0, transform: "translate(-50%, 8px)" },
        { opacity: 1, transform: "translate(-50%, 0)" },
      ],
      { duration: 150, easing: "cubic-bezier(0.23, 1, 0.32, 1)" },
    );
  }

  toastTimer = window.setTimeout(() => {
    if (reduceMotion.matches || !toast.animate) {
      toast.hidden = true;
      return;
    }
    const outgoing = toast.animate(
      [
        { opacity: 1, transform: "translate(-50%, 0)" },
        { opacity: 0, transform: "translate(-50%, 8px)" },
      ],
      { duration: 150, easing: "cubic-bezier(0.23, 1, 0.32, 1)", fill: "forwards" },
    );
    outgoing.onfinish = () => {
      toast.hidden = true;
    };
  }, 2200);
};
```

Notes:
- The toast's base CSS transform is `translateX(-50%)` (line 532) — every
  keyframe must re-state the horizontal centering (`translate(-50%, …)`) or the
  toast jumps sideways mid-animation.
- `getAnimations().cancel()` at the top makes a toast shown during a previous
  exit restart cleanly; a canceled animation's `onfinish` never fires, so it
  cannot hide the new toast.
- The 2200ms dwell time is unchanged.

## Repo conventions to follow

- WAAPI with a `matchMedia("(prefers-reduced-motion: reduce)")` guard is the
  repo's existing pattern for JS-driven motion — see `BackToTop.astro:14` and
  `Works.astro:224`.
- Easing literal `cubic-bezier(0.23, 1, 0.32, 1)` matches plan 010's
  `--ease-out`; component styles in this repo spell curves literally
  (`CommandPalette.astro:264`, `PredirectDemo.astro:224`).

## Steps

1. Add the four keyframes + three animation rules from Target §1 to the
   `<style>` block; merge the backdrop `animation` into the existing
   `.command-palette-backdrop` rule.
2. Add `closeTimer` / `reduceMotion` declarations next to the state vars
   (lines 630–633).
3. Replace `setOpen` (lines 676–693) with Target §2 verbatim.
4. Replace `showToast` (lines 717–724) with Target §3 verbatim.
5. `grep -n "is-closing" src/components/CommandPalette.astro` → hits in both
   the style block and the script.

## Boundaries

- Do NOT touch the command list, filtering, focus-trap (lines 785–798), or
  keyboard handlers (lines 800–820) — they all call `setOpen`, whose signature
  is unchanged.
- Do NOT change the entrance keyframe (`command-palette-enter`) or its 180ms.
- Do NOT change the 2200ms toast dwell.
- Do NOT add dependencies.
- If the cited line numbers don't match the code (drift since 3ed8291), STOP
  and report.

## Verification

- **Mechanical**: `bun run check` → 0 errors; `bun run build` succeeds.
- **Feel check** (`bun run dev`, desktop):
  - open ⌘K → 180ms drop-in; press Esc → dialog fades/rises out over 150ms
    while the backdrop fades; nothing pops;
  - **spam ⌘K ~5× per second**: no stuck palette, no flicker-lock; if open
    lands mid-exit the dialog is simply open (snap-back is acceptable);
  - trigger "Copy email" from the palette: toast slides up 8px + fades in over
    150ms, sits 2200ms, slides down + fades out — the `translateX(-50%)`
    centering never wobbles;
  - DevTools → Animations panel: record an Esc close — exactly one 150ms
    animation on the dialog, easing curve visibly front-loaded;
  - Rendering panel → `prefers-reduced-motion: reduce`: open/close and toast
    show/hide are instant (no timer delay before `hidden` flips);
  - keyboard check: after close, focus returns to the trigger immediately
    (not 150ms later).
- **Done when**: exit and toast animations play as specced, reduce-motion is
  instant, spam test passes, checks are green.
