# SPEC-019 — vachan-eval v3: latency lab + realtime path

## Verified baseline (do not regress)
44 pytest, eval gate+basis PASS (mean WER 0.1617, p95 ~594ms), 30 utts, category gates, history deltas, mock STT.

## v3 goal
Make it a **latency** showcase (VoiceAgentRAG arXiv 2026: retrieval round-trip eats the whole budget; dual-fast/slow design is the differentiator) — the single strongest signal for SuperKalam / Wadhwani / Micron-style voice agent roles.

## Scope (bounded)
1. **`eval/latency.py` + streaming STT adapter** — `ASR_ADAPTER=stream` simulates chunked audio (1s chunks): emit first-token latency (TTFT), inter-chunk p50/p95, end-to-end p95. Report TTFT separately (voice UX metric). Tests ≥8 with deterministic fake clocks.
2. **Semantic cache** — `app/cache.py`: doc-embedding-indexed cache (deterministic hash embeddings, no API key) over near-duplicate utterances; measure hit rate + speedup on the 30-utt set, and show cache-correctness guard (cache only when normalized transcript-equivalent expected text matches; never serve cache on `adversarial` category). Report hit rate/speedup in eval output.
3. **Latency budget in CI** — `eval/run.py` gains `--budget` check: TTFT p95 ≤ 400ms in stream mode, e2e p95 ≤ 1200ms; failing prints which layer breached.
4. **Web** — latency page section: TTFT vs e2e bars per category + cache hit-rate line (pure SVG).

## Non-goals
No real faster-whisper download, no websocket server, no GPU.

## Acceptance
≥52 pytest, `eval/run.py --stream` exit 0 printing TTFT + cache stats, web build ok, README v3 section with measured TTFT/hit-rate numbers and the dual-path explanation.
