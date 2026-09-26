# SPEC-020 — nyaya-guard v3: Postgres+pgvector backend, RLS-tenant ready

## Verified baseline (do not regress)
54 npm tests, eval 1.000s + freshness 4/4, versioned corpus, staleness guard, sampler → proposed.json, /ingest validation.

## v3 goal
Kill the in-memory-only limitation: real Postgres schema (pgvector + pg_trgm + RRF hybrid in SQL) with an in-memory adapter kept as default so CI stays keyless — the pattern 2026 RAG production guides converge on.

## Scope (bounded)
1. **`db/schema.sql`** — chunks(uuid, doc_id, tenant_id, ordinal, content, embedding vector, model, version/freshness cols), HNSW cosine index, GIN trigram index, `ENABLE/FORCE ROW LEVEL SECURITY` + tenant policy using `current_setting('app.tenant_id')`; iterative-scan notes.
2. **`src/store_pg.ts`** — adapter with `SET LOCAL app.tenant_id` per transaction; hybrid retrieval (vector CTE + trgm CTE + RRF) mirroring current `retriever.ts` fusion; feature-flagged (`STORE=memory|pg`).
3. **Tenant tests** — wrong-tenant query returns 0 hits; schema applies cleanly; parity test: memory vs pg return same top-k on the 12-scheme corpus (skipped when no DATABASE_URL, with explicit skip reason).
4. **Docs** — README v3: "why pgvector, why RLS, why we still default to memory in CI" + migration notes (model column for gradual re-embed).

## Non-goals
No docker-compose PG service required in tests (compose service + optional profile yes), no embedding API.

## Acceptance
npm test green (≥60, skips explicit), eval exit 0 in memory mode unchanged, `tsc` clean, README v3 section, compose profile `pg` defined.
