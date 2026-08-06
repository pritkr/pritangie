# Plan 005: Improve accessibility, external asset resilience, and quality gates

> **Executor instructions**: Follow this plan step by step. Do not touch the
> workshop section. Update `plans/README.md` when complete.

**Drift check**: `git diff --stat 05c4424..HEAD -- src/components/Header.astro src/components/Hero.astro src/components/Service.astro src/components/Works.astro package.json`

## Status

- **Priority**: P2
- **Effort**: S/M
- **Risk**: MED
- **Depends on**: plans 001–004
- **Category**: dx
- **Planned at**: commit `05c4424`, 2026-08-03

## Why this matters

The site builds successfully, but several details reduce accessibility and
resilience: decorative images use generic alt text, the mobile menu uses hash
links, and some project/review images depend on third-party URLs. The package
has a build command but no explicit quality gate beyond that build.

## Current state

- `src/components/Header.astro:18-29` uses `alt="svg"` for decoration and
  `src/components/Header.astro:62` uses `href="#"` for the menu trigger.
- `src/components/Hero.astro:30` labels a decorative hero asset as `alt="logo"`.
- `src/components/Service.astro:52-56` uses `alt="svg"` for decoration.
- `src/components/Works.astro:18-34` references YouTube and raw GitHub image
  URLs; `Reviews.astro:19-28` references DiceBear avatars.
- `package.json:5-9` defines `dev`, `build`, `preview`, and `astro`, but no
  lint or accessibility scripts.

## Scope

In scope: `Header.astro`, `Hero.astro`, `Service.astro`, `Works.astro`,
`Reviews.astro`, `package.json`, and small supporting configuration only if a
check can be added without introducing a large dependency migration.

Out of scope: workshop files, full design changes, framework upgrades, and
rewriting all external assets unless a specific broken asset is confirmed.

## Commands

| Purpose | Command | Expected result |
|---|---|---|
| Build | `bun run build` | exit 0; 7 static routes generated |
| Find generic alt text | `rg -n 'alt="svg"|alt="logo"' src/components` | no generic labels remain for decorative/meaningful assets |
| Find hash triggers | `rg -n 'href="#"' src/components` | no interactive menu control depends on a hash link |
| Check scope | `git status --short` | only intended files plus the plan files are changed |

## Steps

### Step 1: Correct image semantics

Use empty alt text for purely decorative stars, arrows, and ornaments. Give
meaningful images specific descriptions, such as the hero portrait or a project
screenshot. Do not describe visual decoration as a logo unless it is actually
the site logo.

**Verify**: `rg -n 'alt="svg"|alt="logo"' src/components` → no matches unless
the remaining usage is demonstrably correct and documented.

### Step 2: Make the mobile menu control semantic

Use a button for opening and closing the mobile menu, with `type="button"`, an
accessible name, and `aria-expanded`/`aria-controls` state that is updated by
the existing script. Preserve the current visual design and close behavior.

**Verify**: `rg -n 'button|aria-expanded|aria-controls|menu-content' src/components/Header.astro` → semantic control and state attributes are present.

### Step 3: Reduce fragile external image dependencies

Prefer local optimized assets for project and testimonial images already in the
repository. For any external image that remains, provide a stable fallback or
document why it must remain external. Do not download or replace assets without
verifying licensing and ownership.

**Verify**: `bun run build` → exit 0; all local asset references resolve in
`dist`.

### Step 4: Add the smallest useful quality gate

Keep `bun run build` as the required baseline. If an existing dependency or
Astro command can provide a no-install type check, add a script only after
verifying it works in this repository. Do not introduce a large linting or
accessibility dependency solely for this plan.

**Verify**: run every script added to `package.json`; each exits 0.

## Done criteria

- [ ] Decorative and meaningful image alt text is intentional.
- [ ] Mobile navigation uses semantic controls and remains functional.
- [ ] Fragile image dependencies are reduced or have a verified fallback.
- [ ] Build and any added quality script pass.
- [ ] Workshop files are unchanged.

## STOP conditions

- Stop if a quality tool requires dependency installation or a framework upgrade
  not already supported by the repository.
- Stop if an external asset’s licensing or ownership is unclear.
- Stop if changing the menu requires rewriting the navigation architecture.

## Maintenance notes

When adding images, decide whether they are content or decoration and set alt
text accordingly. Keep the build command as a deployment gate; add stronger
checks only when they have a clear failure signal and low maintenance cost.
