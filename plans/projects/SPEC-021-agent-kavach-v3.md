# SPEC-021 — agent-kavach v3: sandbox hardening + pluggable backends

## Verified baseline (do not regress)
go 45 race-clean, pytest 47, npm 20, pass@1 1.00, vault+redaction (canary test), hash-chained audit + verify, policy.yaml shared by daemon+MCP, docs/SECURITY.md. Known documented limits: no host-escape isolation; wholesale audit rewrite with recomputed hashes passes verify (needs external anchor).

## v3 goal
Make the sandbox claim honest and extensible: seccomp/cgroup/no-new-privs on the local executor, a `runsc` (gVisor) backend stub behind the same interface with auto-detection, and external anchoring for audit integrity.

## Scope (bounded)
1. **Local executor hardening** — `daemon/exec_linux.go`: `SysProcAttr{NoNewPrivs, Setsid, Pdeathsig}`, seccomp filter blocking fork-bomb-ish syscalls (clone3/fork) via `prctl(PR_SET_NO_NEW_PRIVS)` + `SECCOMP_MODE_FILTER` when permitted (graceful fallback with logged warning on non-Linux), optional cgroup v2 memory cap when `/sys/fs/cgroup` writable. Tests ≥6 asserting NoNewPrivs + timeout kill still work, fallback path safe.
2. **Backend interface + gVisor stub** — `daemon/sandbox.go`: `Backend` interface (Run/Stop/Inspect); `dockerBackend`, `localBackend`, `runscBackend` (auto-detects `runsc` binary, else returns structured `ErrBackendUnavailable` — no fake success); `/v1/backends` endpoint; policy.yaml can pin backend. Tests: interface conformance for all three, runsc-absent path returns error not success.
3. **External audit anchor** — `daemon/anchor.go`: periodic HMAC-SHA256 anchor of chain head to `anchors.jsonl` (key from env, never logged); `verify` checks anchors when present, reports unanchored window honestly (no silent pass). Tests: anchor mismatch detected, missing key → warn not pass.
4. **Docs** — README v3 + SECURITY.md update: "what changed", gVisor roadmap now concrete (how to enable runsc), anchor semantics + residual limits (no timestamping authority).

## Non-goals
No actual runsc container runs in tests, no Vault/KMS, no multi-user RBAC.

## Acceptance
go test ≥55 race-clean, pytest + npm unchanged green, `/v1/backends` lists backends with availability, verify still detects tamper + now detects anchor mismatch, README v3 section.
