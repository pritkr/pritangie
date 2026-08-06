# Plan 001: Clarify career positioning and primary CTA

> **Executor instructions**: Follow this plan step by step. Do not touch the
> workshop section. Update `plans/README.md` when complete.

**Drift check**: `git diff --stat 05c4424..HEAD -- src/components/Hero.astro src/components/CallToAction.astro src/pages/about.astro src/layouts/Layout.astro`

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: LOW
- **Depends on**: none
- **Category**: direction
- **Planned at**: commit `05c4424`, 2026-08-03

## Why this matters

The current headline, “I build tech that feels human,” is memorable but does
not identify the role or opportunities Prit wants. The site contains strong
evidence for a privacy-first open-source product engineer and FOSS educator,
but visitors must infer that from scattered sections. Make that identity clear
within five seconds while retaining the existing playful tone.

## Current state

- `src/components/Hero.astro` contains the main headline at lines 32–44,
  student status at lines 45–59, and only a “See Works” CTA at line 62.
- `src/components/CallToAction.astro` says “Like what you see?” and links only
  to a generic email CTA at lines 7–13.
- `src/pages/about.astro` describes the author as a computer-science student
  and lists many technologies, but does not state a target role or current
  opportunity at lines 25–90.
- `src/layouts/Layout.astro:9-15` contains generic site metadata that should
  remain accurate after copy changes.

## Scope

In scope: `src/components/Hero.astro`, `src/components/CallToAction.astro`,
`src/pages/about.astro`, and any page-specific `Layout` props needed to keep
metadata accurate.

Out of scope: `src/components/WorkshopBooking.astro`, project card structure,
blog implementation, visual redesign, résumé contents, and external profiles.

## Commands

| Purpose | Command | Expected result |
|---|---|---|
| Build | `bun run build` | exit 0; 7 static routes generated |
| Check copy | `rg -n "privacy-first|open-source|educator|Currently looking|Get in touch" src/components src/pages` | new positioning language is present |

## Steps

### Step 1: Establish the primary identity

Update the hero copy to communicate a privacy-first open-source product
engineering identity, with FOSS education/community as the secondary signal.
Keep “human,” “Bihar,” and the playful voice, but replace vague wording with a
specific role and outcomes. Add a short “currently looking for” or equivalent
line only if it can be kept truthful and easy to update.

**Verify**: `bun run build` → exit 0 and `/index.html` contains one clear h1
describing the primary professional identity.

### Step 2: Give visitors two clear next actions

Keep “See Works” as the primary action. Add a secondary action for the résumé
or professional contact, with visible text rather than relying on social icons.
Rewrite the bottom CTA so it names the types of collaboration sought: software,
open-source, privacy, or community work. Do not imply paid availability unless
the current owner confirms it elsewhere in the repository.

**Verify**: `rg -n "See Works|Résumé|CV|open-source|privacy|collaborat" src/components/Hero.astro src/components/CallToAction.astro` → all intended actions are present.

### Step 3: Align the About page

Add a concise opening paragraph that matches the hero identity, then preserve
the more personal material below it. Group the long technology list under a
useful heading such as “What I build with” instead of making the stack the
central identity.

**Verify**: `bun run build` → exit 0; `/about/index.html` contains the same
primary role language as the homepage.

## Done criteria

- [ ] Homepage identifies a concrete primary professional direction.
- [ ] Homepage has visible work and résumé/contact actions.
- [ ] About page reinforces the same direction without removing personality.
- [ ] Workshop files are unchanged.
- [ ] `bun run build` exits 0.

## STOP conditions

- Stop if the owner’s intended career direction cannot be represented truthfully
  by the privacy/open-source product engineer framing.
- Stop if the implementation requires changing workshop copy or files.

## Maintenance notes

Keep the primary identity stable for several months so project and content
updates compound around one professional signal. Revisit only when the résumé,
major project direction, or job search changes.
