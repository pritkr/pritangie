# SPEC-017 — agent-kavach v2: vault + immutable audit + policy manifest

## v1 verified (do not regress)
Go daemon (socket 0600, queue, Docker/subprocess exec, kill-switch), MCP 5 tools, TS loop retry×3 + trajectory JSONL, React SSE dashboard, 8 tasks pass@1 1.00, suites: go 19 / py 25 / npm 20.

## v2 goal
Adopt 2026 agent-runtime practice (Docker AI Governance, gVisor/MAGI, agentbox post-CVE-2026-25253): credential vault, tamper-evident audit, declarative policy — the three controls that separate demos from deployable runners.

## Scope (bounded)
1. **Credential vault** — `daemon/vault.go`: `policy.yaml`-declared env allowlist per tool (e.g., web-fetch gets no secrets, eval-run gets none); secrets injected at exec time from process env, NEVER written to trajectory/audit logs — `trace.go` redaction (`[REDACTED]`) with tests proving a fake `SECRET=xxx` never appears in logs.
2. **Hash-chained audit** — each audit JSONL line embeds `prev_hash` + `sha256(line)`; `daemon/verify` subcommand (or `go run ./daemon -verify audit.log`) replays chain, exit 1 on tamper; tests: valid chain passes, edited line detected, truncated tail detected.
3. **Policy manifest** — `policy.yaml` (tools allow/deny, per-tool timeout, network allowlist, workspace root); daemon loads at boot, rejects unknown tools with structured error; MCP server reads same file; tests for deny + timeout override.
4. **Docs** — `docs/` already exists: add `docs/SECURITY.md` (threat model: what kavach stops vs doesn't — prompt injection contained, host escape out of scope without gVisor; roadmap note: runsc backend).

## Non-goals
No gVisor implementation, no real secret store (Vault/KMS), no multi-user RBAC.

## Acceptance
`go test` green (≥25), pytest green, npm green, verify detects tamper, redaction test with canary secret, README security section updated, `policy.yaml` example committed.
