# AI SDLC Phase Progression & Acceptance Gates

This document defines the 7 distinct phases of TrackNet / NSIS development. Progression to subsequent phases requires meeting each phase's acceptance gate.

---

### Phase 0: Scaffolding, RBAC & Security Foundation
- **Deliverables**: FastAPI backend, React 18 + Vite frontend shell, PostgreSQL/SQLite ORM, RBAC geo-scoping, field encryption, immutable audit middleware, synthetic data generators.
- **Acceptance Gate**: Clean build, `/healthz` 200, negative cross-district 403 checks, minor 404 test passing, zero plain PII in database logs.

### Phase 1: Unified Registry & Deduplication Engine
- **Deliverables**: Athlete, Trainer, Facility, Institution models. Verification state machine (`SUBMITTED → UNDER_REVIEW → VERIFIED`). Trigram duplicate detection.
- **Acceptance Gate**: Duplicates returned as candidates (no auto-merge); invalid status transitions return 409; minor consent status enforced.

### Phase 2: Pipeline Diagnosis & Privacy-Preserving Heatmaps
- **Deliverables**: Sport × District × Age band aggregations, small-cell suppression ($< 5$), conversion funnel calculation, peer median gap detection.
- **Acceptance Gate**: Aggregates match brute-force calculations; small cells suppressed; gap alerts include reasons and peer baseline.

### Phase 3: Support Linkage, Scheme Catalog & Maker-Checker
- **Deliverables**: Versioned `SchemeRule` JSON schema, deterministic eligibility evaluator, maker-checker rule approval (`approver_id != author_id`), transactional outbox notifications.
- **Acceptance Gate**: Property-based test passes across 1,000 permutations; draft rules never affect eligibility; idempotent outbox delivery.

### Phase 4: Grounded Agent Layer & Action Proposals
- **Deliverables**: `agent-svc` tool-calling, pgvector retrieval over approved guidelines only, prompt-injection isolation, `ActionProposal` review queue.
- **Acceptance Gate**: 100% citation rate on 50-item golden set; zero adversarial data leaks; write actions require approval tokens.

### Phase 5: State Adapters & Offline PWA
- **Deliverables**: Sandboxed state adapter manifests, IndexedDB WebCrypto store, sync protocol with conflict resolution matrix, Hindi/English localization.
- **Acceptance Gate**: Adapters cannot alter core schema; logout wipes local key material; offline sync tested under network throttling.

### Phase 6: Pilot Hardening, ASVS L2 & Resilience
- **Deliverables**: STRIDE threat model verification, tamper-evident audit hash chaining, DPDP erasure workflow, chaos recovery drill, agent kill-switch.
- **Acceptance Gate**: Recovery drill passes in CI; log scanner finds 0 synthetic PII; automated WCAG 2.1 AA scan passes on all core flows.
