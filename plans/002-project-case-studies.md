# Plan 002: Turn featured projects into evidence-rich case studies

> **Executor instructions**: Follow this plan step by step. Do not touch the
> workshop section. Update `plans/README.md` when complete.

**Drift check**: `git diff --stat 05c4424..HEAD -- src/components/Works.astro src/pages/projects.astro src/pages/posts`

## Status

- **Priority**: P1
- **Effort**: M/L
- **Risk**: MED
- **Depends on**: `plans/001-career-positioning.md`
- **Category**: direction
- **Planned at**: commit `05c4424`, 2026-08-03

## Why this matters

`Works.astro` currently shows four attractive cards, but each card sends the
visitor directly to an external site. A recruiter cannot quickly see Prit’s
role, decisions, contribution, or measurable result. Add a lightweight,
maintainable case-study layer while preserving the existing card design.

## Current state

- `src/components/Works.astro:7-36` stores all portfolio data in one array with
  `name`, `desc`, `cover`, `link`, and `meta`.
- `src/components/Works.astro:52-75` renders each item as one external anchor;
  there is no role, outcome, stack detail, or internal project route.
- `src/pages/projects.astro` only renders `Works`.
- Existing posts in `src/pages/posts/` already provide narrative material for
  Predirect, BEU Connect, and chaind.

## Scope

In scope: `src/components/Works.astro`, `src/pages/projects.astro`, new project
content under `src/pages/projects/` only if consistent with the existing Astro
route structure, and project-specific local assets when required.

Out of scope: workshop files, external repositories, résumé PDF, and a CMS.

## Commands

| Purpose | Command | Expected result |
|---|---|---|
| Build | `bun run build` | exit 0; existing routes plus any project routes generate |
| Inspect routes | `find dist -type f -name index.html | sort` | every declared project route has output |

## Steps

### Step 1: Extend project data with proof fields

Add fields that can be filled truthfully: `role`, `outcome`, `stack`, `status`,
and an optional internal case-study URL. Start with Predirect, BEU Connect,
chaind, and listbrew. Do not invent user counts, revenue, or adoption metrics;
use verified GitHub stars or qualitative outcomes only.

**Verify**: `rg -n "role:|outcome:|stack:|status:" src/components/Works.astro` →
all four projects have the new fields.

### Step 2: Add concise proof to cards

Keep the current visual hierarchy, but add one short role/outcome line and a
clear “View case study” or “View project” affordance. Ensure the whole card is
not the only way to distinguish the internal case study from the external
repository/demo link.

**Verify**: `bun run build` → exit 0; built project cards contain role/outcome
text and accessible link names.

### Step 3: Create one strong Predirect case study first

Create the smallest internal case-study page or equivalent content for
Predirect. Include: problem, Prit’s contribution, technical approach, result,
what changed after release, repository link, and demo/install link. Use the
existing post as source material but do not duplicate the entire article.

**Verify**: `bun run build` → exit 0; a generated Predirect case-study route is
present and contains all six required sections.

## Done criteria

- [ ] All four cards communicate contribution and outcome.
- [ ] Predirect has a dedicated proof-rich case study.
- [ ] No unsupported metrics are added.
- [ ] `bun run build` exits 0.
- [ ] Workshop files are unchanged.

## STOP conditions

- Stop if the owner cannot verify a project’s role or metric rather than
  substituting a marketing claim.
- Stop if adding case-study routes requires a routing architecture change beyond
  the existing static Astro setup.

## Maintenance notes

When adding a new project, require a role, an outcome, and one proof link before
adding it to the homepage. Keep long technical narratives in posts and keep
case studies scannable.
