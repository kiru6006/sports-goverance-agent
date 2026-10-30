# Design Decisions Log

This document records ambiguous architecture and domain calls, the reasoning, and the authoritative ruling for TrackNet / NSIS.

---

## Decision 001: Technology Stack Standardization
- **Context**: The concept documents in `IDEAS.md` / `PLANS.md` referenced multiple alternatives (e.g. Next.js vs Angular).
- **Ruling**: Adopt **React 18 + Vite + TypeScript** for the web frontend and **Python 3.11+ / FastAPI** for the core backend API, aligned with user standards and established production patterns (InsureOps).
- **Rationale**: Clean separation between client presentation and domain orchestration; facilitates rapid prototyping, high-performance client state with responsive UI, native integration with Python agent tooling, and support for containerized or static GitHub Pages preview with mock fallback.

---

## Decision 002: Minor Records Concealment (404 vs 403)
- **Context**: Access control attempts for athletes under 18 years old when requested by unauthorized roles (e.g., officers of a different district or state officers without direct custody).
- **Ruling**: Return HTTP `404 Not Found` rather than `403 Forbidden`.
- **Rationale**: An HTTP 403 status code confirms the existence of the minor's record, which constitutes an information leak under the DPDP Act 2023. Returning 404 ensures zero metadata leakage to non-authorized entities.

---

## Decision 003: Small-Cell Suppression for Anonymity
- **Context**: Aggregate reporting across granular district × sport × age band cells when athlete counts are very low.
- **Ruling**: When cell count is $< 5$, emit `suppressed: true` and redact the integer count.
- **Rationale**: In low-density sports or small rural districts, single-digit counts allow re-identification of individual athletes from public or semi-public dashboards.

---

## Decision 004: Deduplication Policy
- **Context**: Athlete onboarding when fuzzy match finds candidate duplicates on normalized name, date of birth, and district.
- **Ruling**: Return candidate matches with match confidence scores. **Never auto-merge.**
- **Rationale**: Automated merging of sports records risks destroying eligibility, state quota rankings, and historical records. Deduplication requires explicit verification by district authorities.

---

## Decision 005: Read-Mostly Agent with ActionProposal Human Gates
- **Context**: The role and autonomy tier of the AI agent layer.
- **Ruling**: The agent may perform read operations (search, gap analysis, policy RAG). Any state modification or scheme rule alteration must create an `ActionProposal` requiring two-factor or distinct human authorization (`approver_id != actor_id`).
- **Rationale**: Government decision-making cannot delegate statutory discretion to autonomous AI agents. The system provides decision support, not autonomous policy execution.
