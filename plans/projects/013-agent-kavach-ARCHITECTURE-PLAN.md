# 013 — agent-kavach: Zero-cloud self-hosted agent sandbox runner

> Future repo: `pritkr/agent-kavach` (GPL-3.0 to match chaind-cli/Predirect identity, or MIT — pick MIT for hiring). Slot: Agentic AI + DevOps + Privacy infra.
> Targets: UpMentor-X ₹30-60k, Hulchul ₹15-45k, MATRIX/Ages Art/Xiarch/Techvruk agentic, Hobnobly/Skillzenloop DevOps, Ente/Brave infra.

## 1. Architecture

```
web (React SSE dashboard: stream, cost/lat chart, KILL) ──▶ runner/ (TS loop:
  plan→tool→observe, retry×3 backoff, structured errors, trajectory JSONL)
        │ tools via mcp/ (Python http): shell-sandboxed, file-read scoped,
        │ web-fetch allowlist, scheme-lookup, eval-run; arg validation
        ▼
daemon/ (Go: :0 open ports — Unix socket 0600 token, job queue, executor:
  Docker sandbox preferred → fallback subprocess timeout+rlimit, kill-switch,
  /metrics Prometheus, cost/latency ledger, audit.log)
```

- **Security model (sell this in interviews):** zero open ports, 0600 socket + token file, workspace-scoped FS, domain allowlist, 30s tool timeout, kill-switch broadcasts SIGKILL + marks trajectory `killed`.
- **Reliability:** retry budgets, trajectory eval `pass^k` script, replay from JSONL.
- **Observability:** OTel-style trace JSON + `/metrics` (runs_total, p95, cost_total).

## 2. Repo tree

```
agent-kavach/
  daemon/{main.go, queue.go, exec.go, metrics.go, go.mod} (stdlib-first)
  mcp/{server.py, tools.json}  runner/{loop.ts, tools.ts, replay.ts, package.json}
  web/{Vite React}  eval/{tasks.json (8 real tasks), passk.py}
  tests: go test ≥8, pytest ≥8, npm test ≥6
  Dockerfile (multi-stage), docker-compose.yml, Makefile, .github/workflows/ci.yml
  README, LICENSE
```

## 3. Build plan by aspect

- **Aspect A — backend/systems (Go+Python):** daemon socket+queue+exec+kill, MCP tools + validation, all tests green.
- **Aspect B — runner+frontend:** TS loop + replay + SSE dashboard + kill button + SVG charts.
- **Aspect C — evals/infra:** 8 tasks (file edit, fetch+parse, scheme lookup, multi-tool), pass^k scorer, CI (go test + pytest + npm test), Docker multi-stage, README security + numbers.
- **Gates:** `go test ./...` + `pytest -q` + `npm test` all green; `docker build` ok.

## 4. Resume bullets

- Built zero-cloud agent runner (Go Unix-socket daemon, Docker sandbox, kill-switch) with MCP tools + plan-act-observe loop; trajectory eval + Prometheus metrics.
