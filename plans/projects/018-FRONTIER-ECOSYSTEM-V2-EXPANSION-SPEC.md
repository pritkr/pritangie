# FRONTIER ECOSYSTEM V2.0 ARCHITECTURAL EXPANSION SPECIFICATION
**Document ID**: `018-FRONTIER-ECOSYSTEM-V2-EXPANSION-SPEC`  
**Author**: Antigravity Principal Systems Architect & Google DeepMind Agentic Pair  
**Target Repositories**: 
- `github.com/pritkr/sentinel-mcp`
- `github.com/pritkr/dhvani-eval`
- `github.com/pritkr/pebble-sync`
- `github.com/pritkr/spec-forge`  
**Status**: APPROVED FOR CONCURRENT MULTI-AGENT IMPLEMENTATION

---

## 1. Executive Summary & Design Vision

The Frontier Portfolio establishes an elite technical thesis: **autonomous, resilient, edge-capable, and secure AI infrastructure designed for real-world constraints**.

In Phase 1, we constructed the minimum viable core engines for all 4 systems, verified their base mathematical properties, and integrated them into the Astro showcase and Typst resume.

In **Phase 2 (v2.0 Architectural Expansion)**, we elevate each standalone project from an impressive MVP to a **production-grade engineering marvel** ready to compete with top-tier industrial systems (Envoy, HashiCorp Vault, Whisper/Gram Vaani, Automerge/ElectricSQL, and Semgrep/Stryker).

```
+---------------------------------------------------------------------------------------+
|                                FRONTIER AGENTIC STACK                                 |
+---------------------------------------------------------------------------------------+
|                                                                                       |
|   1. VOICE INGRESS & LOW-RESOURCE TELEPHONY SIMULATION                                |
|   +-------------------------------------------------------------------------------+   |
|   | DHVANI-EVAL v2.0                                                              |   |
|   | - Eastern Nagari & Gurmukhi Normalizers | Indic Phonetic Soundex/Metaphone    |   |
|   | - Telephony Waveform SNR & ITU-T G.712  | Jitter Buffer & Latency Profiling   |   |
|   | - Self-Contained Interactive SVG/HTML Benchmark Dashboard                     |   |
|   +-------------------------------------------------------------------------------+   |
|                                         |                                             |
|                                         v (Spoken Intent)                             |
|   2. CAPABILITY-GATED RUNTIME REVERSE PROXY                                           |
|   +-------------------------------------------------------------------------------+   |
|   | SENTINEL-MCP v2.0                                                             |   |
|   | - Transport Agnosticism: Stdio + Unix Domain Sockets + HTTP/SSE Proxy         |   |
|   | - Ephemeral Leases & Time-To-Live Capability Delegation (HMAC-SHA256)        |   |
|   | - Indirect Prompt Injection & Invisible Unicode Tag Smuggling Guardrails      |   |
|   | - Go Fuzz Testing (testing.F) & High-Concurrency Throughput Benchmarks        |   |
|   +-------------------------------------------------------------------------------+   |
|                                         |                                             |
|                                         v (Agent Tool Execution)                      |
|   3. AUTONOMOUS AST MUTATION & INVARIANT VERIFICATION                                 |
|   +-------------------------------------------------------------------------------+   |
|   | SPEC-FORGE v2.0                                                               |   |
|   | - Advanced AST Operators (Exception Swallowing, Boundary Chaining, Async)     |   |
|   | - Multiprocessing Parallel Worker Pool (ProcessPoolExecutor batching)         |   |
|   | - Hypothesis Property-Based Invariant Synthesizer                             |   |
|   | - Interactive Visual HTML Mutation Audit Report with Side-by-Side Diffs       |   |
|   +-------------------------------------------------------------------------------+   |
|                                         |                                             |
|                                         v (Verified Delta & State)                    |
|   4. OFFLINE-FIRST DISTRIBUTED MERKLE CRDT SYNC                                       |
|   +-------------------------------------------------------------------------------+   |
|   | PEBBLE-SYNC v2.0                                                              |   |
|   | - Stable Causal Compaction & Tombstone Garbage Collection (Causal Horizon)    |   |
|   | - Collaborative Sequence CRDT (Fugue-lite for clinical text editing)         |   |
|   | - WebSocket Real-Time Sync Transport with Heartbeats & Auto-Reconnection      |   |
|   | - Property-Based Semilattice Fuzzing (1,000+ randomized DAG interleavings)   |   |
|   +-------------------------------------------------------------------------------+   |
+---------------------------------------------------------------------------------------+
```

---

## 2. Detailed Project Specifications

### 2.1 Sentinel-MCP v2.0 (Go 1.27)
**Role Lead**: Space Bunny Architect (`pro` tier)

#### A. Transport Agnosticism (HTTP/SSE & Unix Domain Socket Proxy)
- **Problem**: MCP specification supports stdio, SSE (Server-Sent Events), and streamable HTTP. Enterprise MCP servers often run as remote microservices (PostgreSQL MCP, Kubernetes MCP) or local Unix daemons.
- **Architecture**:
  - `pkg/transport/transport.go`: Defines `Transport` interface (`ReadMsg()`, `WriteMsg()`, `Close()`).
  - `pkg/transport/unix.go`: Unix Domain Socket listener and forwarder.
  - `pkg/transport/sse.go`: HTTP server exposing `/sse` (for streaming notifications/responses) and `/message` (POST endpoint for client requests). Intercepts JSON-RPC payloads, invokes `guard.Evaluator`, and relays filtered responses.
  - CLI subcommand: `sentinel proxy --transport sse --listen :8080 --upstream http://localhost:9000/sse`.

#### B. Ephemeral Leases & Time-To-Live Capability Delegation
- **Problem**: Modern least-privilege security requires ephemeral privilege elevation. Agents should not have permanent file write or network access.
- **Architecture**:
  - `pkg/lease/lease.go`: Mint and verify capability leases.
  - Structure:
    ```go
    type CapabilityLease struct {
        Token     string    `json:"token"`
        Capability string   `json:"capability"` // e.g. "fs:write:/tmp/scratch"
        ExpiresAt time.Time `json:"expires_at"`
        Signature string    `json:"signature"`  // HMAC-SHA256(secret, capability + expires_at)
    }
    ```
  - Guard integration: If a tool call violates static policy, check if request headers/metadata contain a valid unexpired cryptographic lease token signed by Sentinel's master key.

#### C. Indirect Prompt Injection & Invisible Tag Smuggling Guardrails
- **Problem**: Compromised tools or poisoned web search/file inputs can inject indirect instructions into LLM agent contexts (e.g., hidden Unicode tags `\uE0000-\uE007F`, or `"system: ignore all previous instructions"`).
- **Architecture**:
  - `pkg/guard/injection.go`:
    - `ScanForInjection(text string) (bool, string)`: Detects prompt override heuristics, role hijacking patterns, and zero-width/tag smuggling attacks.
    - Automatic sanitation or blocking when detected.

#### D. Fuzz Testing & Concurrency Benchmarks
- `pkg/proxy/fuzz_test.go`: Uses Go 1.18+ native `f.Fuzz` to test parser robustness against malformed JSON-RPC payloads.
- `pkg/proxy/concurrency_test.go`: Verifies thread safety and sub-millisecond latencies under concurrent goroutine load (1,000+ simulated concurrent agent requests).

---

### 2.2 Dhvani-Eval v2.0 (Python 3.14)
**Role Lead**: Mimo 2.6 Flash Engine (`flash` tier)

#### A. Multi-Script Indic Normalization & Indic Soundex/Metaphone
- **Problem**: Low-resource Indian deployments extend across Eastern Nagari (Bengali/Assamese) and Gurmukhi (Punjabi). Hindi voice systems also suffer from dialectal phonetic substitutions (e.g. dental vs retroflex stops).
- **Architecture**:
  - `dhvani/multiscript.py`:
    - `EasternNagariNormalizer`: handles Bengali/Assamese Unicode range `\u0980-\u09FF`, normalizes Ya-phala, Khanda Ta, Hasanta, and Ishwar.
    - `GurmukhiNormalizer`: handles Gurmukhi range `\u0A00-\u0A7F`, normalizes Tippi, Bindi, Adhak, and Halant.
  - `dhvani/phonetic.py`:
    - `IndicSoundex`: Phonetic classification mapping homophones and aspiration variants into phonetic buckets for dialect-tolerant WER scoring.

#### B. Audio Signal Quality Analytics & ITU-T G.712 Compliance
- **Problem**: Speech AI teams need objective signal quality metrics (SNR, clipping, spectral energy) before feeding audio to ASR models.
- **Architecture**:
  - `dhvani/audio_analytics.py`:
    - `compute_snr(signal, noise)`: Computes true signal-to-noise ratio in decibels (dB).
    - `compute_clipping_rate(audio_samples)`: Measures dynamic range saturation.
    - `estimate_speech_energy(audio_samples)`: RMS energy and Zero-Crossing Rate (ZCR).

#### C. Streaming Chunk Jitter Buffer & Latency Profiler
- **Problem**: Voice agents in production (like SuperKalam, Vapi, Cartesia) fail due to streaming jitter and packet drops on 2G networks.
- **Architecture**:
  - `dhvani/streaming.py`:
    - `StreamingVoiceSession`: Simulates chunked 100ms audio feeds with simulated network latency variance, jitter buffer queues, and calculates TTFT (Time to First Token) and EOU (End of Utterance) turnaround.

#### D. Self-Contained Interactive SVG/HTML Benchmark Dashboard
- **Problem**: Text outputs in terminals are hard to present to non-technical stakeholders or in GitHub READMEs.
- **Architecture**:
  - `dhvani/html_report.py`: Generates a zero-dependency, self-contained interactive HTML report featuring embedded SVG charts of WER vs Noise degradation curves and syllable error distributions.

---

### 2.3 Pebble-Sync v2.0 (TypeScript / Bun)
**Role Lead**: Muse Spark 1.3 Systems (`flash` tier)

#### A. Stable Causal Compaction & Tombstone Garbage Collection
- **Problem**: Real-world CRDTs accumulate tombstones (in ORSets and Merkle DAGs) indefinitely, degrading memory and bandwidth over time.
- **Architecture**:
  - `src/merkle/compaction.ts`:
    - `computeCausalHorizon(peerClocks: VectorClock[])`: Finds the minimum vector timestamp known and acknowledged by all active peers.
    - `compactDAG(dag: MerkleDAG, horizon: VectorClock)`: Prunes DAG historical nodes older than the horizon into a compacted base snapshot while preserving cryptographic root hash invariants.

#### B. Collaborative Sequence CRDT (Fugue-lite / Rich Text Editing)
- **Problem**: Rural health and welfare workers don't just edit key-value pairs; they write collaborative clinical notes, patient summaries, and prescriptions concurrently.
- **Architecture**:
  - `src/crdt/sequence.ts`:
    - `SequenceCRDT<T>`: Implements an order-preserving collaborative sequence CRDT using fractional logical positional identifiers `[originId, offset]`.
    - Guarantees deterministic tie-breaking without interleaving anomalies under concurrent offline insertions.

#### C. Real-Time WebSocket Transport & Mesh Signaling
- **Problem**: Pebble-sync needs a real network transport adapter for browser and edge deployments.
- **Architecture**:
  - `src/network/websocket_adapter.ts`:
    - Client and Server WebSocket sync handlers.
    - Implements the 3-step Merkle exchange (`SyncOffer` -> `SyncRequest` -> `SyncResponse`) over binary/text WebSocket frames with automatic exponential reconnect.

#### D. Property-Based Semilattice Fuzzing
- `tests/property_based_fuzz.test.ts`:
  - 1,000+ randomized state-merge fuzzing runs asserting strict Semilattice laws:
    - Commutativity: `merge(A, B) == merge(B, A)`
    - Associativity: `merge(merge(A, B), C) == merge(A, merge(B, C))`
    - Idempotency: `merge(A, A) == A`
    - Monotonicity: `state(t+1) >= state(t)`

---

### 2.4 Spec-Forge v2.0 (Python 3.14)
**Role Lead**: Spec Forge Agent (`pro` tier)

#### A. Advanced AST Mutation Operators
- **Problem**: LLM code generators make subtle errors that basic arithmetic or comparison mutants don't capture (e.g. exception swallowing, broken chained comparisons, missed `await` calls).
- **Architecture**:
  - `spec_forge/mutator.py` additions:
    - `ExceptionSwallowingMutant`: mutates `except SpecificError:` into `except Exception: pass`.
    - `BoundaryChainingMutant`: mutates chained comparisons `a <= b < c` to `a < b <= c`.
    - `TypeCastMutant`: mutates `int(x)` to `float(x)` or `str(x)`.
    - `NoneCheckMutant`: mutates `if x is not None:` into `if x:` (catching truthiness bugs on `0` or `""`).

#### B. Multiprocessing Parallel Worker Pool
- **Problem**: Running 500 mutants sequentially takes minutes. In CI/CD gates, mutation testing must finish in seconds.
- **Architecture**:
  - `spec_forge/parallel_runner.py`:
    - Uses Python `concurrent.futures.ProcessPoolExecutor` with chunked mutant distribution.
    - Automatic core detection, batching, and sub-second timeout enforcement per mutant.

#### C. Property-Based Invariant Synthesizer (Hypothesis Integration)
- **Problem**: Static test case synthesis only catches one boundary value. Property-based tests test thousands of boundary values.
- **Architecture**:
  - `spec_forge/property_synthesizer.py`:
    - Synthesizes Python code decorated with `@given(st.integers(...))` or `@given(st.floats(...))` to mathematically eliminate surviving mutants across arbitrary input spaces.

#### D. Interactive Visual HTML Mutation Audit Report
- **Problem**: Terminal output cannot easily show multi-line side-by-side AST diffs.
- **Architecture**:
  - `spec_forge/html_report.py`:
    - Standalone interactive HTML report with code syntax styling, clickable mutant diffs (original vs mutated AST), survivor taxonomy, and synthesized test cases.

---

### 2.5 Unified End-to-End Frontier Ecosystem Demonstration
- `projects/ecosystem-demo/`:
  - `run_frontier_pipeline.py`: Pure, zero-dependency end-to-end integration demo connecting:
    1. Telephony audio degradation and Indic phonetic evaluation (`dhvani-eval`).
    2. Zero-overhead capability proxying & injection scanning (`sentinel-mcp`).
    3. AST mutation testing & regression defense (`spec-forge`).
    4. Offline-first Merkle CRDT synchronization across edge nodes (`pebble-sync`).

---

## 3. Subagent Allocation Matrix

| Subagent Role | Model Tier | Target Project | Mission Scope |
| :--- | :--- | :--- | :--- |
| **Space Bunny Architect** | `pro` | `projects/sentinel-mcp` | SSE & Unix Domain Socket proxy, Ephemeral Leases (HMAC-SHA256), Indirect Injection & Tag Smuggling Guard, Go Fuzz & Concurrency Tests. |
| **Mimo 2.6 Flash Engine** | `flash` | `projects/dhvani-eval` | Multi-script normalizer (Eastern Nagari & Gurmukhi), Indic Soundex/Metaphone, Telephony SNR & Audio Analytics, Streaming Jitter Buffer, HTML/SVG Dashboard. |
| **Muse Spark 1.3 Systems** | `flash` | `projects/pebble-sync` | Stable Causal Compaction & GC, Sequence CRDT (Fugue-lite), WebSocket Transport Adapter, Property-Based Semilattice Fuzzing. |
| **Spec Forge Agent** | `pro` | `projects/spec-forge` | Advanced AST Operators, Parallel Multiprocessing Runner, Hypothesis Property Synthesizer, Interactive HTML Mutation Audit Report. |

---

## 4. Verification Protocol
Each subagent must:
1. Implement the specified modules with clean, idiomatic code and zero unnecessary dependencies.
2. Write comprehensive unit and integration tests.
3. Verify test passes cleanly (`go test ./...`, `python3 -m unittest discover tests`, `bun test`).
4. Update standalone `README.md` documentation with architecture diagrams and instructions.
5. Report completion with exact performance and test metrics.
