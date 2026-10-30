# Phase 6: Pilot Hardening, ASVS L2 & Resilience Plan

## 1. Objectives & Scope
Per [docs/04-phases.md](file:///Users/apple/projects/sports-network-agent/docs/04-phases.md) and [IDEAS.md](file:///Users/apple/projects/sports-network-agent/IDEAS.md):
- **STRIDE Threat Modeling & ASVS L2 Hardening**: Verify audit log immutability and anti-tamper chains.
- **Tamper-Evident Audit Hash Chaining**: Verify that every `AuditLog` row has `previous_hash` and `record_hash = sha256(prev_hash + user_id + action + resource_type + resource_id + payload_hash)`. Provide verification endpoint `/api/v1/security/audit-chain/verify` returning cryptographic status of the chain.
- **Agent Kill-Switch & Circuit Breakers**: Global & per-state toggle `/api/v1/security/agent-killswitch` allowing security officers to instantly disable generative agent queries or action execution when anomalies are detected.
- **DPDP Act Erasure & Anonymization Workflow**: Right-to-be-forgotten endpoint `/api/v1/security/dpdp/erasure/{athlete_id}` that securely redacts PII (`encrypted_dob`, `encrypted_phone`, `encrypted_guardian_ref`), replaces names with `"REDACTED_DPDP"`, writes an immutable audit record, and updates verification status to `DELETED`.
- **Chaos Recovery Drill & Resilience Verification**: Endpoint `/api/v1/security/chaos-drill` validating database integrity, outbox delivery drains, and cryptographic key rotation readiness.
- **Automated Verification Test Suite**: `backend/tests/test_phase6.py`.
- **Frontend Security & Resilience Dashboard**: Tab or view showing real-time tamper-evident hash verification, agent killswitch controls, DPDP erasure audit, and resilience status.
