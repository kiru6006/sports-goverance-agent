# System Assumptions

This document tracks all operational and domain assumptions made during the design and implementation of TrackNet / NSIS.

---

## Assumption 001: Synthetic Data Baseline
- **Status**: ACTIVE
- **Detail**: In development and pilot testing, all athlete names, phone numbers, addresses, and schools are synthetically generated. All seeded records carry `is_synthetic = true`. Real PII will only be ingested following signed MoUs and DPDP legal clearances.

## Assumption 002: Population Baselines for Per-100k Metrics
- **Status**: ACTIVE (Pending Ministry Census Tables)
- **Detail**: Gap analysis per 100k population uses synthetic census estimates per district and age-band until official Census / State Sports Directorate figures are uploaded.

## Assumption 003: Default Gap Threshold
- **Status**: ACTIVE
- **Detail**: A district sport × age cell is flagged as an "Under-Identified Gap" if its identified-per-100k rate is less than 50% (`0.50`) of the state peer median. This multiplier is configurable per state.

## Assumption 004: Encryption at Rest Key Management
- **Status**: ACTIVE
- **Detail**: In development and local test mode, field-level encryption utilizes an environment variable (`ENCRYPTION_SECRET_KEY`) using standard AES-GCM / Fernet. In production, this interfaces with cloud HSM / KMS.

## Assumption 005: Model Deployment & Data Residency
- **Status**: ACTIVE
- **Detail**: Agent evaluation uses locally hosted models (Ollama / vLLM) or MeitY-compliant endpoints adhering to India data residency requirements. Zero PII is included in agent prompts.
