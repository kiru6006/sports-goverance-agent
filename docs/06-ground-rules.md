# TrackNet — AI SDLC Ground Rules & System Constraints

You are building **TrackNet (Sports Network / Gap Analyser Agent)**, a post-KID athlete tracking, verification, and talent retention intelligence layer for Indian sports (Ministry of Youth Affairs & Sports / Khelo India ecosystem).

## 1. Absolute Constraints (Never, in any phase)
- **NEVER** collect Aadhaar, passport, biometrics, or unverified government ID uploads.
- **NEVER** build a social feed, chat messaging, or unvetted coach-athlete matching.
- **NEVER** build speculative athlete "potential" scoring or speculative medal prediction.
- **NEVER** disburse money or create an automated payment/grant payout channel.
- **NEVER** add gamification, leaderboards, or talent discovery bounties.
- **NEVER** write to NSRS / Khelo India central databases (read-only integration adapters only).
- **NEVER** auto-merge duplicate candidate records. Merges require explicit human review.
- **NEVER** return 403 when probing minor records out of scope. Return **404 Not Found** so minor record existence is never leaked.

## 2. Invariants (Always, in every phase)
- **KID First**: Khelo India ID (KID) is the primary anchor; provisional identifier only if no KID exists.
- **Data Protection & Privacy (DPDP Act 2023)**: Field-encrypt PII at rest (AES-256-GCM / Fernet); audit-log every read/write access.
- **Audit Logging**: Immutable, append-only audit trail logging actor, role, district scope, action, and payload hash. Zero PII in plain logs.
- **Provenance & Explainability**: Every number, gap metric, and eligibility recommendation must state `"as of"` timestamp and source citations down to rule/document version.
- **Multi-Tenant Scoping**: Enforce strict RBAC and geographic stewardship (`steward_org_id`, `state_id`, `district_id`) on all queries and mutations.
- **Human Decision Gates**: The agent layer only prepares `ActionProposal`s. Official approval is mandatory for state changes.

## 3. Engineering & Stack Conventions
- **Backend**: Python 3.11+ / FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, PostgreSQL with PostGIS & pgvector (fallback to SQLite for standalone local demo tests).
- **Frontend**: React 18 + Vite + TypeScript + TailwindCSS with Lucide icons (supporting both full API mode and GitHub Pages / mock client fallback mode).
- **Architecture**: Modular service-repository pattern, deterministic rule engines, agent tool-calling layer.
