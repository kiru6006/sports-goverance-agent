# Known Gaps & Future Backlog

This document inventories known gaps, out-of-scope capabilities, and items deferred across project phases.

---

| Gap ID | Description | Impact | Target Phase | Status |
| :--- | :--- | :--- | :--- | :--- |
| **GAP-001** | Live NSRS Direct API Integration | Manual export/import used; live NSRS bi-directional sync is read-only deferred | Phase 5 | OPEN (Awaiting API MoU) |
| **GAP-002** | Official Scheme Rule Database Verification | Scheme rules are marked `is_placeholder=true` until approved by State Directorates | Phase 3 | OPEN (Draft schemes seeded) |
| **GAP-003** | Indian Indic Language Transliteration Fuzzy Matching | Basic soundex / trigram match used; multi-script Devnagari-to-Roman transliteration needs specialized model | Phase 5 | BACKLOG |
| **GAP-004** | SMS / IVR Gateway Integration | Notifications use file/log outbox stubs; live telecom DLT gateway integration pending telco registration | Phase 3 | STUBBED |
| **GAP-005** | Production KMS / Hardware Security Module | Local Fernet encryption used for dev/test; requires Cloud KMS integration in production | Phase 6 | PENDING PROD DEPLOY |
