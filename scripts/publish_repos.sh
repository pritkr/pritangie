#!/usr/bin/env bash
# ==============================================================================
# publish_repos.sh — stage every project as its OWN git repo with a structured
# commit history, then optionally create + push the public GitHub repos.
#
#   ./publish_repos.sh plan              # print the plan, write nothing
#   ./publish_repos.sh build             # stage + commit locally (no network)
#   ./publish_repos.sh push              # gh repo create + push
#   ./publish_repos.sh all               # build, then push
#   ./publish_repos.sh build vachan-eval # one project only
#
# Why not projects/scripts/split.sh? It preserves parent history, but the parent
# never committed these folders, so it falls back to a synthetic snapshot = ONE
# squashed commit. This builds a reviewable history instead: scaffold -> feature
# -> tests -> CI -> docs, so `git log` on a public repo tells the story.
#
# It never commits to your working branch, never modifies projects/ or src/, and
# never touches the network without `push` / `all`.
# ==============================================================================

set -uo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
PROJECTS_DIR="$REPO_ROOT/projects"
STAGE_ROOT="${PUBLISH_STAGE:-$REPO_ROOT/.publish-stage}"

OWNER="${PUBLISH_OWNER:-pritkr}"
AUTHOR_NAME="${PUBLISH_NAME:-Prit Kumar}"
AUTHOR_EMAIL="${PUBLISH_EMAIL:-pritkumarrrr@gmail.com}"

MODE="plan"
SELECTED=""
ALL_PROJECTS="vachan-eval nyaya-guard sahayak-grid agent-kavach dhvani-eval pebble-sync sentinel-mcp spec-forge"

usage() { sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'; }

while [ $# -gt 0 ]; do
  case "$1" in
    plan)         MODE="plan" ;;
    build)        MODE="build" ;;
    push)         MODE="push" ;;
    all)          MODE="all" ;;
    -h|--help)    usage; exit 0 ;;
    --owner)      [ -n "${2:-}" ] || { printf 'publish: --owner needs a value\n' >&2; exit 2; }
                  OWNER="$2"; shift ;;
    --stage)      [ -n "${2:-}" ] || { printf 'publish: --stage needs a path\n' >&2; exit 2; }
                  STAGE_ROOT="$2"; shift ;;
    -*)           printf 'publish: unknown option %s\n' "$1" >&2; exit 2 ;;
    *)            SELECTED="${SELECTED:+$SELECTED }$1" ;;
  esac
  shift
done
[ -n "$SELECTED" ] || SELECTED="$ALL_PROJECTS"
for p in $SELECTED; do
  case " $ALL_PROJECTS " in
    *" $p "*) ;;
    *) printf 'publish: unknown project %s\n' "$p" >&2; exit 2 ;;
  esac
done

# ------------------------------------------------------------------- output
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  B=$'\033[1m'; DIM=$'\033[2m'; R=$'\033[31m'; G=$'\033[32m'; Y=$'\033[33m'; Z=$'\033[0m'
else
  B=""; DIM=""; R=""; G=""; Y=""; Z=""
fi
say()  { printf '%s\n' "$*"; }
info() { say "   ${DIM}$*${Z}"; }
pass() { say "   ${G}OK${Z}    $*"; }
warn() { say "   ${Y}WARN${Z}  $*"; }
fail() { say "   ${R}FAIL${Z}  $*"; }

DESC=""; TOPICS=""; DEST=""; GROUP_N=0

meta() { DESC="$1"; TOPICS="$2"; }

# commit_group <subject> <body> <path> [path...]
commit_group() {
  local subject="$1" body="$2"; shift 2
  local existing=() p
  GROUP_N=$((GROUP_N + 1))
  # A group with no paths means the caller forgot the body argument and the
  # intended path fell into it. That silently ships a repo missing its tests or
  # its CI, so it is fatal, not a warning.
  if [ $# -eq 0 ]; then
    fail "group '$subject' has no paths — did the body argument go missing?"
    return 1
  fi
  for p in "$@"; do [ -e "$DEST/$p" ] && existing+=("$p"); done
  if [ ${#existing[@]} -eq 0 ]; then
    fail "group '$subject' matched none of: $*"
    return 1
  fi
  ( cd "$DEST" && git add -- "${existing[@]}" ) || return 1
  if [ -z "$(cd "$DEST" && git diff --cached --name-only)" ]; then
    info "no change — group skipped: $subject"
    return 0
  fi
  ( cd "$DEST" && git commit -q -m "$subject" -m "$body" ) || return 1
  pass "$subject  ${DIM}(${#existing[@]} path(s))${Z}"
}

RSYNC_EXCLUDES=(
  --exclude 'node_modules/' --exclude 'dist/' --exclude '.astro/'
  --exclude '__pycache__/' --exclude '.pytest_cache/' --exclude '*.pyc'
  --exclude '*.egg-info/' --exclude '.venv/' --exclude '.DS_Store'
  --exclude '.git/' --exclude 'coverage/'
)

# Forbidden in a public repo. The .pyc/db/egg-info patterns matter because a
# project's own .gitignore may not cover an artifact a tool created after it.
FORBIDDEN_RE='(^|/)(node_modules|__pycache__|\.pytest_cache|dist|\.astro|coverage)(/|$)|\.pyc$|\.egg-info(/|$)|\.DS_Store$|\.db$|^\.env'

# =========================================================== manifests
# Order per project: scaffold -> feature -> data -> test -> ci -> docs.

manifest_vachan_eval() {
  meta "Eval harness for Indic voice AI: WER/CER, streaming TTFT, semantic cache, eval-gated CI" \
       "voice-ai,evaluation,asr,speech-recognition,fastapi,react,ci-cd"
  commit_group "chore: scaffold project layout, tooling and license" \
    "Pins the toolchain (Makefile, pinned requirements, container build) and the
MIT license so the harness is reproducible from a clean clone." \
    LICENSE .gitignore Makefile requirements.txt Dockerfile docker-compose.yml
  commit_group "feat(core): FastAPI service with pluggable STT adapters and WER/CER scoring" \
    "Mock-first by design: the default adapter needs no API key and no network, so
the whole suite runs in CI. faster-whisper slots in behind the same interface." \
    app/
  commit_group "feat(eval): golden-set runner with per-category gates and a baseline regression check" \
    "Category thresholds beat one global threshold: a dialect regression should
fail on its own category, not get averaged away by easy utterances. Baseline
comparison fails the build on a >0.03 absolute regression." \
    eval/ data/
  commit_group "feat(web): dashboard with WER leaderboard, category breakdown and latency panels" \
    "Pure SVG/CSS, no chart library, so the bundle stays small and the page still
renders with the API offline via a committed mock snapshot." \
    web/
  commit_group "test: cover scoring, input normalization, API surface, cache guard and latency model" \
    "The cache guard tests assert adversarial utterances are never served from
cache - that property is the whole reason the cache is safe to ship." \
    tests/
  commit_group "ci: gate merges on pytest, the eval gate and an image build" \
    "Evaluation runs in CI rather than as a report nobody reads." \
    .github/
  commit_group "docs: problem, architecture, measured results and failure analysis" \
    "Includes the per-language and per-difficulty WER breakdown, and the honest
list of where the harness itself is wrong." \
    README.md
}

manifest_nyaya_guard() {
  meta "Guardrailed civic RAG: deterministic rules decide eligibility, the LLM only rephrases" \
       "rag,llm-safety,guardrails,retrieval,pgvector,row-level-security,typescript,civic-tech"
  commit_group "chore: scaffold package, TypeScript config and license" \
    "Pinned toolchain and MIT license; the service defaults to an in-memory store
so CI needs no database and no API key." \
    LICENSE .gitignore package.json package-lock.json tsconfig.json Dockerfile docker-compose.yml
  commit_group "feat(core): rules-decide retrieval pipeline with citations, guardrails and audit log" \
    "The trust boundary is the point: a deterministic rule layer owns every
eligibility verdict and the model is only allowed to rephrase. PII redaction,
prompt-injection screening and a JSONL audit trail sit on the same path." \
    src/
  commit_group "feat(corpus): versioned scheme documents and the Postgres/pgvector schema" \
    "Scheme documents carry version and validity frontmatter so a superseded
amount can never silently answer as current. The schema enables FORCE row-level
security, because a tenant filter that only the application remembers is not a
boundary." \
    data/ db/
  commit_group "feat(web): chat UI with inline citations, rule trace and confidence" \
    "Shows the deciding rule and its evidence, so a wrong answer is traceable
instead of merely wrong." \
    web/
  commit_group "chore(audit): keep the audit log directory in the tree" \
    "The audit directory ships empty on purpose: an empty dir is not tracked by
git, and a missing logs/ path at first run is a confusing way to find out." \
    logs/
  commit_group "test: cover rule verdicts, guardrail rejections, freshness and tenant isolation" \
    "Includes adversarial queries that must refuse, and a check that the connected
role is not a superuser - otherwise the isolation tests pass vacuously." \
    tests/
  commit_group "feat(eval): refusal and faithfulness suite with a production sampler" \
    "Refusal recall is the metric that matters here: a confident wrong answer costs
a citizen a wasted trip. The sampler mines real audit logs for queries worth
adding to the golden set." \
    eval/
  commit_group "ci: run tests, typecheck and the eval suite on every change" \
    "A RAG system that can silently regress on refusal recall needs the eval suite
in CI, not in a report nobody opens." \
    .github/
  commit_group "docs: trust-boundary design, retrieval rationale and failure analysis" \
    "Explains why pgvector, why RLS, and why CI still defaults to the in-memory
store." \
    README.md
}

manifest_sahayak_grid() {
  meta "Offline-first Hindi civic PWA kit: service worker, sync queue, edge API" \
       "pwa,offline-first,astro,hono,cloudflare-workers,postgres,accessibility,civic-tech"
  commit_group "chore: scaffold the Astro app, TypeScript config and license" \
    "MIT license and pinned toolchain. System fonts and no image payloads keep the
initial JS small enough for a 2G connection." \
    LICENSE .gitignore package.json package-lock.json bun.lock tsconfig.json astro.config.mjs Dockerfile
  commit_group "feat(web): Hindi-first offline UI with checklist, search, TTS and deadline countdowns" \
    "Built for a shared Android phone on patchy 2G: 48px touch targets, Hindi
default, speech synthesis for scheme details, and a service worker that caches the
app shell so the app opens with no connectivity at all." \
    src/ public/
  commit_group "feat(api): Hono edge API with OTP verification and an idempotent sync endpoint" \
    "Sync is keyed on a client-generated UUID so a replayed offline write cannot
double-count - the property that makes offline writes safe to retry." \
    api/
  commit_group "feat(data): Postgres schema and seed data for eight flagship schemes" \
    "Every seeded scheme carries a real deadline and window, staggered so the
tiering logic has something to sort." \
    db/
  commit_group "test: cover eligibility, transliteration-tolerant search, sync idempotency and deadline tiers" \
    "Search tests assert Roman Hindi and Devanagari forms find the same scheme -
the query a real user types is rarely the one in the portal." \
    tests/
  commit_group "ci: build and test on every change" \
    "The build is the test here: an offline-first PWA that fails to build is not
shippable." \
    .github/
  commit_group "docs: offline architecture, airplane-mode demo and deployment targets" \
    "Lighthouse figures are labelled a target, not a measurement." \
    README.md
}

manifest_agent_kavach() {
  meta "Zero-cloud agent sandbox runner: Go daemon, MCP tool gateway, hash-chained audit" \
       "ai-agents,mcp,go,sandbox,seccomp,security,observability,self-hosted"
  commit_group "chore: scaffold the policy manifest, build tooling and license" \
    "policy.yaml is committed as an example so the security posture is readable
before you run anything." \
    LICENSE .gitignore Makefile Dockerfile docker-compose.yml .dockerignore entrypoint.sh policy.yaml
  commit_group "feat(daemon): Go daemon exposing a 0600 unix socket with a sandboxed executor" \
    "Zero open ports by construction - the control socket is a unix socket with
0600 permissions, not a bound TCP port. The executor hardens each child with
no-new-privs, a new session and a parent-death signal, and installs a seccomp
filter that blocks namespace and clone escape routes." \
    daemon/
  commit_group "feat(mcp): tool gateway with schema validation and policy enforcement" \
    "Every tool call is authenticated and authorized at one chokepoint before it
reaches anything external. Policy is read from the same manifest the daemon
loads, so the two cannot drift." \
    mcp/ tools/
  commit_group "feat(runner): plan-tool-observe loop with retry budgets and trajectory logging" \
    "Retries are budgeted and errors are structured, so the loop degrades loudly
instead of spinning. Every step is written to a replayable trajectory log." \
    runner/
  commit_group "feat(web): live dashboard with run stream, cost/latency chart and kill switch" \
    "The kill switch is in the UI on purpose: an operator who cannot stop a run
will not run untrusted code in the first place." \
    web/
  commit_group "feat(eval): task suite and a pass^k reliability scorer over recorded trajectories" \
    "pass^3 on a single lucky trajectory is not reliability. The scorer replays
committed golden trajectories so a regression in the loop shows up as a number." \
    eval/
  commit_group "ci: race-checked Go tests, Python tests, runner tests and image build" \
    "The race detector is not optional here - the executor kills processes from
another goroutine." \
    .github/
  commit_group "docs: threat model, security controls and the gVisor roadmap" \
    "Includes what this does NOT stop. A plain container is not a kernel boundary;
the runsc backend is the documented path to that." \
    README.md docs/
}

manifest_dhvani_eval() {
  meta "Streaming telephony degradation simulator and evaluation suite for Indic voice AI" \
       "voice-ai,evaluation,telephony,indic,streaming,python"
  commit_group "chore: scaffold the Python package, build tooling and license" \
    "Packaging metadata plus a Makefile so the suite runs the same way locally and
in CI." \
    LICENSE .gitignore pyproject.toml setup.py requirements.txt MANIFEST.in Makefile Dockerfile
  commit_group "feat: evaluation core, WER/CER metrics and the telephony degradation simulator" \
    "Models what actually happens on a real call - packet loss, jitter, codec
artifacts - because a model that only scores clean offline audio tells you
nothing about production." \
    dhvani/
  commit_group "test: 98 tests over metrics, normalization and degradation behaviour" \
    "Degradation behaviour is the interesting half: the simulator is only useful
if its packet-loss and jitter models are pinned by tests." \
    tests/
  commit_group "ci: run the suite on every change" \
    "98 tests is the floor, not the goal: the simulator's value depends on the
degradation models staying pinned." \
    .github/
  commit_group "docs: worked example and metric definitions" \
    "A runnable example matters more than prose for a library-shaped tool." \
    examples/ README.md
}

manifest_pebble_sync() {
  meta "Ultra-compact offline-first CRDT sync engine with Merkle clocks and tamper-evident hash chains" \
       "crdt,offline-first,distributed-systems,merkle,typescript,websocket,zero-dependencies"
  commit_group "chore: scaffold the TypeScript package and license" \
    "Zero runtime dependencies is a design constraint, not an accident - the
lockfile and config are committed so the claim is checkable." \
    LICENSE .gitignore package.json tsconfig.json bun.lock
  commit_group "feat: CRDT core - OR-set, document model, Merkle clocks and delta replication" \
    "Delta replication over Merkle clocks means two offline replicas exchange only
what diverged, and a tamper-evident chain makes a peer's history verifiable
rather than merely asserted." \
    src/
  commit_group "test: 53 tests including randomized semilattice property fuzzing" \
    "Property-based runs are what give CRDT convergence claims their teeth;
a handful of example-based tests would not." \
    tests/
  commit_group "ci: typecheck and run the test suite on every change" \
    "Typecheck runs in CI because a zero-dependency library still has to compile
for the next person." \
    .github/
  commit_group "docs: rural-health sync walkthrough and protocol notes" \
    "The example is a real two-replica sync over a lossy link, because CRDT
convergence claims are only meaningful against a network that actually misbehaves." \
    examples/ README.md
}

manifest_sentinel_mcp() {
  meta "Capability-gated security reverse proxy and policy enforcer for the Model Context Protocol" \
       "mcp,security,proxy,policy,go,zero-trust,capability-leases"
  commit_group "chore: scaffold the Go module, release tooling and license" \
    "Includes .goreleaser.yaml so the release pipeline is visible in the repo." \
    LICENSE .gitignore go.mod go.sum Makefile Dockerfile .goreleaser.yaml
  commit_group "feat: proxy core, policy engine, capability leases, audit log and transports" \
    "A capability lease is an HMAC-signed, TTL-bound grant of a specific
permission, so a temporary override is explicit and expires on its own. Unix
socket, SSE and stdio transports share one enforcement path." \
    cmd/ pkg/
  commit_group "ci: vet, build and test the module on every change" \
    "go vet is not optional for a security proxy: the bug class this guards
against is a request that reaches a tool it was never granted." \
    .github/
  commit_group "docs: policy examples and architecture notes" \
    "The example policies are the fastest way to understand what a capability
grant is allowed to look like." \
    examples/ README.md
}

manifest_spec_forge() {
  meta "Agentic code verification and AST-preserving mutation testing engine" \
       "mutation-testing,ast,code-quality,testing,agents,python,llm"
  commit_group "chore: scaffold the Python package and license" \
    "Zero third-party runtime dependencies: the engine runs on the standard
library's ast module, which is also what keeps the mutation operators
trustworthy - no third-party parser between the source and the tree." \
    LICENSE .gitignore pyproject.toml requirements.txt
  commit_group "feat: AST mutator, mutation scoring and test synthesizer" \
    "Coverage tells you a line ran; mutation testing tells you whether your test
would have noticed if the line were wrong. The synthesizer generates regression
tests aimed at mutants that survived." \
    spec_forge/
  commit_group "test: cover mutation operators, scoring and synthesis" \
    "The scoring tests are the ones that matter: a mutation score computed wrong
is worse than no score, because it looks like a result." \
    tests/
  commit_group "ci: run the suite behind a mutation-score gate" \
    "The gate is the point - a test suite that cannot kill mutants is not
protecting anything." \
    .github/
  commit_group "docs: architecture, why mutation testing, and a worked example" \
    "Includes the reasoning for why coverage alone cannot tell you whether a test
would catch a wrong line." \
    examples/ README.md
}

# ============================================================== build phase

build_one() {
  local name="$1"
  DEST="$STAGE_ROOT/$name"
  local manifest="manifest_$(printf '%s' "$name" | tr '-' '_')"
  GROUP_N=0

  say ""
  say "${B}▌ $name${Z}  ${DIM}→ $DEST${Z}"
  [ -d "$PROJECTS_DIR/$name" ] || { fail "no such project: $PROJECTS_DIR/$name"; return 1; }

  rm -rf -- "$DEST"; mkdir -p -- "$DEST" || return 1
  rsync -a "${RSYNC_EXCLUDES[@]}" "$PROJECTS_DIR/$name/" "$DEST/" || return 1

  git -C "$DEST" init -q -b main || return 1
  git -C "$DEST" config user.name "$AUTHOR_NAME"
  git -C "$DEST" config user.email "$AUTHOR_EMAIL"
  git -C "$DEST" config commit.gpgsign false

  "$manifest" || return 1

  # meta() ran first inside the manifest, so DESC/TOPICS now hold this project's.
  # Persist them outside the repo so the push phase never re-runs the manifest.
  mkdir -p "$STAGE_ROOT/.meta"
  printf 'desc=%s\ntopics=%s\n' "$DESC" "$TOPICS" > "$STAGE_ROOT/.meta/$name"

  # Per-project exclusions that are judgement calls, not accidents. Each one is
  # recorded in that project's .gitignore so it is visible in the repo itself.
  case "$name" in
    spec-forge)
      info "scratch.py / run_test.py / update_mutator.py / report.json are gitignored"
      ;;
  esac

  local bad
  bad=$(git -C "$DEST" ls-files | grep -E "$FORBIDDEN_RE" || true)
  if [ -n "$bad" ]; then
    fail "forbidden files tracked:"; printf '%s\n' "$bad" | sed 's/^/         /' >&2; return 1
  fi

  # Completeness: anything still untracked AND not ignored is a file the manifest
  # forgot. This is the check that would have caught the dropped tests/CI above,
  # and it keeps catching them as the projects change.
  local dropped
  dropped=$(git -C "$DEST" status --porcelain --untracked-files=all | grep '^??' | sed 's/^?? //' || true)
  if [ -n "$dropped" ]; then
    fail "manifest dropped these files (present, not ignored, not committed):"
    printf '%s\n' "$dropped" | sed 's/^/         /' >&2
    info "add them to a commit_group in this script, or gitignore them deliberately"
    return 1
  fi

  local files commits
  files=$(git -C "$DEST" ls-files | wc -l | tr -d ' ')
  commits=$(git -C "$DEST" rev-list --count HEAD)
  pass "$commits commits, $files tracked files"
  return 0
}

# =============================================================== push phase

push_one() {
  local name="$1"
  local slug="$OWNER/$name"
  say ""
  say "${B}▌ $slug${Z}"
  if [ ! -d "$STAGE_ROOT/$name/.git" ]; then fail "not built - run: $0 build $name"; return 1; fi

  local metaf="$STAGE_ROOT/.meta/$name"
  local desc topics
  desc=$(sed -n 's/^desc=//p' "$metaf" 2>/dev/null)
  topics=$(sed -n 's/^topics=//p' "$metaf" 2>/dev/null)

  if [ -z "$desc" ]; then
    fail "no description recorded for $name at $metaf - run: $0 build $name"
    return 1
  fi

  # gh repo create has no --add-topic, so metadata is applied with gh repo edit.
  # Split on commas WITHOUT touching IFS: setting IFS also changes how
  # "${arr[@]}" expands, which flattens the array into one comma-joined word.
  local edit_args=(--description "$desc")
  local rest="$topics" t
  while [ -n "$rest" ]; do
    t="${rest%%,*}"
    if [ "$rest" = "$t" ]; then rest=""; else rest="${rest#*,}"; fi
    [ -n "$t" ] && edit_args+=(--add-topic "$t")
  done

  if gh repo view "$slug" >/dev/null 2>&1; then
    warn "$slug already exists - reusing it"
  else
    gh repo create "$slug" --public --source="$STAGE_ROOT/$name" --remote=origin >/dev/null 2>&1 \
      || { fail "gh repo create failed for $slug"; return 1; }
    pass "created $slug"
  fi

  if gh repo edit "$slug" "${edit_args[@]}" >/dev/null 2>&1; then
    pass "description + topics set on $slug"
  else
    warn "could not set description/topics on $slug (push continues)"
  fi

  if git -C "$STAGE_ROOT/$name" push -q -u origin main 2>&1 | tail -2; then
    pass "pushed main → $slug"
  else
    fail "push failed for $slug"
    return 1
  fi
  return 0
}

# =================================================================== driver

say "${B}portfolio repo publisher${Z}"
say "${DIM}source $PROJECTS_DIR${Z}"
say "${DIM}stage  $STAGE_ROOT${Z}"
say "${DIM}owner  $OWNER${Z}"
say "${DIM}mode   $MODE${Z}"

if [ "$MODE" = "plan" ]; then
  for p in $SELECTED; do
    say ""
    say "${B}$p${Z}  ${DIM}→ $OWNER/$p${Z}"
    if [ -d "$PROJECTS_DIR/$p" ]; then
      n=$(find "$PROJECTS_DIR/$p" -type f -not -path '*/node_modules/*' -not -path '*/dist/*' \
            -not -path '*/.astro/*' -not -path '*/__pycache__/*' -not -path '*/.pytest_cache/*' \
            -not -name '*.pyc' 2>/dev/null | wc -l | tr -d ' ')
      say "   ${DIM}$n files · structured history: scaffold, feature, data, test, ci, docs${Z}"
    else
      fail "missing"
    fi
  done
  say ""
  say "${B}plan only — nothing written.${Z} Next: $0 build"
  exit 0
fi

if [ "$MODE" = "build" ] || [ "$MODE" = "all" ]; then
  FAILED=""
  for p in $SELECTED; do build_one "$p" || FAILED="$FAILED $p"; done
  say ""
  if [ -n "$FAILED" ]; then
    fail "build failed for:$FAILED"
    exit 1
  fi
  pass "all staged under $STAGE_ROOT"
  if [ "$MODE" = "build" ]; then
    say ""
    say "${B}built.${Z} Review, then: $0 push"
    exit 0
  fi
fi

if [ "$MODE" = "push" ] || [ "$MODE" = "all" ]; then
  PUSH_FAILED=""
  for p in $SELECTED; do push_one "$p" || PUSH_FAILED="$PUSH_FAILED $p"; done
  say ""
  if [ -n "$PUSH_FAILED" ]; then
    fail "push failed for:$PUSH_FAILED"
    exit 1
  fi
  pass "all pushed to $OWNER"
fi
