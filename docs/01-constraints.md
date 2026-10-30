# Hard System Constraints & Invariants

This document outlines the mandatory legal, technical, and architectural constraints for TrackNet / NSIS.

## 1. Statutory & Legal Constraints (DPDP Act 2023)
1. **Consent Prior to Processing**: Every minor athlete record (`age < 18`) requires verifiable guardian consent before the record can transition beyond draft status.
2. **Concealment of Minors**: Any request for a minor record made by an unauthorized role or an officer outside the athlete's assigned district must return **HTTP 404 Not Found**, never HTTP 403.
3. **No Biometric or Aadhaar Storage**: The platform explicitly disallows ingestion, storage, or indexing of Aadhaar numbers, fingerprints, or raw biometric templates.
4. **Auditability**: Every read and mutation of personal information must generate an append-only audit event capturing user, role, jurisdiction, timestamp, and payload hash. Zero PII values in plain text within logs.

## 2. Decision-Support Boundaries
1. **No Autonomous Fund Disbursement**: TrackNet cannot initiate bank transfers, grant payouts, or quota awards.
2. **No Automated Deduplication Merges**: Duplicate candidates detected through fuzzy trigram similarity must be reviewed and resolved by an authorized district officer.
3. **Explainability Mandate**: Every gap alert, conversion bottleneck, and scheme eligibility recommendation must provide transparent calculation inputs, peer medians, and source document citations.
