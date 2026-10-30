# NSIS / TrackNet Technical Specifications & Architecture Blueprint

This document unifies the core system constraints, data models, screen catalog, and architectural phase roadmaps into a single reference.

---

## 1. Statutory Constraints & Non-Negotiable Invariants

1. **Statutory Consent & Minors (DPDP Act 2023)**:
   - Every athlete under 18 years of age requires verified guardian consent.
   - Any access request for a minor record made by an unauthorized role or outside the athlete's assigned district returns **HTTP 404 Not Found**, never HTTP 403.
   - No biometric data, Aadhaar numbers, or raw identity documents are ever ingested or stored.
   - Append-only cryptographic audit logging for every read or mutation touching sensitive fields. Zero PII in log text.

2. **Decision-Support Boundaries**:
   - The platform provides recommendations and calculations; it does **not** autonomously disburse funds, exclude athletes, or alter verified records without human officer sign-off.
   - Duplicate candidates detected by phonetics (Soundex) or trigram string distance are flagged as candidates for human review; **no automated merges**.
   - Every gap flag, conversion metric, and scheme eligibility recommendation includes transparent calculation inputs and statutory citations.

---

## 2. Core Entities & Privacy Tiers

| Entity | Key Attributes | Privacy Tier | Encryption at Rest |
|:---|:---|:---|:---|
| **Athlete** | `id`, `kid`, `gender`, `state_id`, `district_id`, `primary_sport_id`, `age_band`, `consent_status`, `verification_status` | Public Identifiers / Workflow | Plaintext / Indexed |
| **Athlete (PII)** | `name`, `dob`, `contact_phone`, `contact_email`, `guardian_ref` | Sensitive PII | AES-GCM / Field-level Encrypted |
| **PipelineSnapshot** | `id`, `state_id`, `district_id`, `sport_id`, `age_band`, `identified_count`, `verified_count`, `supported_count`, `progressed_count`, `is_suppressed` | Aggregated Analytics | Plaintext (suppressed if `< 5`) |
| **AuditLog** | `id`, `timestamp`, `actor_id`, `actor_role`, `action`, `target_entity`, `target_id`, `payload_hash`, `prev_hash`, `record_hash` | Security / Audit | Cryptographic SHA-256 Chain |
| **StateAdapterManifest** | `id`, `state_id`, `state_name`, `version`, `supported_languages_json`, `priority_sports_json`, `state_policies_json`, `is_active` | System Configuration | Versioned / Sandboxed |
| **OfflineSyncRecord** | `id`, `client_mutation_id`, `actor_id`, `entity_type`, `field_name`, `conflict_status`, `server_timestamp` | Synchronization | Audit Logged |

---

## 3. Screen & Functional Catalog

- **S-00 to S-04 (Platform Core)**: Identity provider, geographic scope auto-resolution, tamper-evident audit viewer, and chaos drill monitor.
- **S-10 to S-19 (Unified Registry & Network)**: Paginated athlete grid, comprehensive profile views, onboarding wizard, verification queue with state machine controls, and append-only journey event logging.
- **S-20 to S-25 (Source Intelligence & Rejection Audits)**: Policy RAG source library, claim extraction, and candidate rejection audit reports (who rejected, why, and formal audit report).
- **S-30 to S-35 (Diagnosis & Gap Engine)**: Multi-dimensional pipeline gap heatmap, 6-dimension conversion funnels, EvidenceCards with non-causal ranked hypotheses, and travel/facility matrices.
- **S-40 to S-45 (Intervention & Outcome)**: Case management, multi-option comparison tables, maker-checker approval gates (`approver_id != author_id`), and 3/6/12-month outcome tracking.
- **S-50 to S-58 (Support Linkage & Opportunities)**: Scheme catalog with placeholder flags, deterministic eligibility evaluator, coarse needs flags, quota opportunity board, and zero-minor-PII notification outbox.
- **S-60 to S-65 (Autonomous AI Agent & Policy RAG)**: Policy RAG assistant with 100% clause citations, proposal approval tokens, prompt hash logging, and an instant emergency kill-switch.
- **S-70 to S-75 (State Adapters & Offline PWA)**: Sandboxed state adapter manifests, localized UI (EN/HI/MR), offline mutation queue, and deterministic conflict resolution matrix (server wins on status; last-write-wins on contacts).
- **S-80 to S-84 (Security, Privacy & Hardening)**: DPDP Act cryptographic erasure, consent revocation workflows, and go/no-go readiness audits.
- **Go Copilot**: Real-time natural language query assistant linking directly to player profiles, locations, and institutions.

---

## 4. Phase Roadmaps & Verification Status

| Phase | Milestone | Deliverables | Verification Status |
|:---|:---|:---|:---|
| **Phase 0** | Core Platform & RBAC | FastAPI backend, React 18 frontend shell, geo-scoping, immutable audit middleware | ✅ Passed (Tests 1–3) |
| **Phase 1** | Registry & Deduplication | Athlete/Facility/Trainer models, Soundex/Trigram duplicate detection, minor concealment | ✅ Passed (Tests 4–16) |
| **Phase 2** | Pipeline Diagnosis & Gaps | 6-dimension heatmap, conversion funnels, small-cell suppression (`< 5`), equipment loans | ✅ Passed (Tests 17–21) |
| **Phase 3** | Support Linkages & Schemes | Versioned scheme rules, deterministic eligibility engine, maker-checker, outbox pattern | ✅ Passed (Tests 22–28) |
| **Phase 4** | Grounded AI Agent | Policy RAG with 100% citations, read-mostly tools, action proposal human gates | ✅ Passed (Tests 29–33) |
| **Phase 5** | State Adapters & Offline PWA | State manifests (MH, HR), multilingual dictionary, offline sync with conflict matrix | ✅ Passed (Tests 34–37) |
| **Phase 6** | ASVS L2 Hardening & Security | Cryptographic audit hash chain, emergency kill-switch, DPDP erasure, chaos drill | ✅ Passed (Tests 38–41) |
| **Phase 7** | Rejection Audit & Direct Chat | Formal rejection reports, coach/player mapping, support demands & direct chat | ✅ Passed (Tests 42–44) |

---

## 5. System Assumptions & Backlog

- **Assumption 001**: Synthetic data baseline (`is_synthetic = true`) used throughout development and pilot trials prior to state MoU execution.
- **Assumption 002**: Standard per-100k gap threshold set to `< 0.50` of state peer median, configurable per state adapter.
- **Assumption 003**: Field-level encryption uses AES-GCM / Fernet in development; interfaces with Cloud KMS / HSM in production environments.
- **Backlog**: Live NSRS bi-directional API synchronization (pending government API MoU) and CERT-In empanelled third-party penetration testing.
