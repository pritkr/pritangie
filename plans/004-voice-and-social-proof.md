# Plan 004: Replace weak social proof and sharpen personal voice

> **Executor instructions**: Follow this plan step by step. Do not touch the
> workshop section. Update `plans/README.md` when complete.

**Drift check**: `git diff --stat 05c4424..HEAD -- src/components/Reviews.astro src/components/RandomQuote.astro src/components/Service.astro src/pages/about.astro`

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: MED
- **Depends on**: `plans/001-career-positioning.md`
- **Category**: direction
- **Planned at**: commit `05c4424`, 2026-08-03

## Why this matters

The site’s informal voice is a strength, but the current “reviews” section uses
jokes, anonymous identities, and an alleged HOD quote as professional proof.
That can make otherwise strong engineering and community work look less
credible. Preserve humor as clearly labeled personality while adding verified
proof from collaborators, users, workshops, or open-source work.

## Current state

- `src/components/Reviews.astro:4-40` contains roommate, anonymous faculty,
  HOD, and friend comments.
- `src/components/Reviews.astro:45-69` presents those comments under “Here’s
  what people are saying about me,” which frames them as testimonials.
- `src/components/RandomQuote.astro:4-23` chooses a famous quote randomly at
  build time rather than showing Prit’s own perspective.
- `src/components/Service.astro:27-48` mixes site purpose, interests, values,
  and recommendations, including “Effective Accelerationism.”

## Scope

In scope: `Reviews.astro`, `RandomQuote.astro`, `Service.astro`, and the
personal section of `about.astro`.

Out of scope: workshop files, project facts, résumé, and external profiles.

## Commands

| Purpose | Command | Expected result |
|---|---|---|
| Build | `bun run build` | exit 0; 7 static routes generated |
| Search old framing | `rg -n "what people are saying|Anonymous|You know who|Effective Accelerationism" src` | old professional-proof framing is removed or clearly relabeled |

## Steps

### Step 1: Separate humor from credibility

Rename the current section to a clearly personal framing, or replace it with
verified quotes. Do not publish a person’s name, role, or quote unless the owner
has confirmed permission and accuracy. If no verified testimonials are
available, use a “People I build with” or “Unsolicited feedback” section with
only clearly attributable, non-sensitive material.

**Verify**: `bun run build` → exit 0; the section heading does not present
anonymous jokes as professional testimonials.

### Step 2: Add first-person voice

Replace the random famous quote block with a stable, short first-person note:
what Prit believes about privacy, useful software, and learning in public. Keep
the visual treatment, but make the site’s point of view owned by Prit.

**Verify**: `rg -n "I believe|I care|I’m trying|privacy|open source" src/components/RandomQuote.astro` → a first-person statement exists.

### Step 3: Organize personality around the primary identity

Retain interests such as cinema and Linux, but order the section as: work
values, technical interests, personal interests, recommendations. Explain any
politically or technically loaded term in plain language or remove it if it
does not help the intended audience understand Prit.

**Verify**: `bun run build` → exit 0; the About/home pages still contain personal
details while privacy/FOSS/open-source remains the dominant professional theme.

## Done criteria

- [ ] No unverified joke is presented as formal professional proof.
- [ ] The site contains an authored point of view instead of a random quote.
- [ ] Personality remains visible but is organized around the career identity.
- [ ] `bun run build` exits 0.
- [ ] Workshop files are unchanged.

## STOP conditions

- Stop if a quote’s attribution or permission is uncertain.
- Stop if removing a personality item would materially misrepresent the owner’s
  beliefs; label it clearly instead.

## Maintenance notes

Use this rule for future social proof: real name or explicit anonymity, verified
role, permission, and a specific observation about work. Keep jokes in a clearly
personal area.
