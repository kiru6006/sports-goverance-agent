# Data Model Specification & Privacy Tiers

## 1. Privacy Tiers & Encryption Matrix

| Entity | Field | Privacy Tier | Encryption at Rest | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `Athlete` | `id` | Identifier | Plaintext / UUID | Public reference key |
| `Athlete` | `kid` | Identifier | Plaintext / Hash | Primary Khelo India ID |
| `Athlete` | `name` | PII | Field Encrypted | Displayed in authorized UI |
| `Athlete` | `dob` | Sensitive PII | Field Encrypted | Age band derived dynamically |
| `Athlete` | `contact_phone` | Sensitive PII | Field Encrypted | Never logged in plain text |
| `Athlete` | `guardian_ref` | Sensitive PII | Field Encrypted | Required for minors |
| `Athlete` | `district_id` | Metadata | Indexed Plaintext | Used for geo-scoping RBAC |
| `Athlete` | `verification_status`| Workflow | Indexed Plaintext | State machine tracked |

## 2. Core Entities

### Sport
- `id`: UUID (PK)
- `code`: String (Unique, e.g. `BOX`, `ATH`, `KAB`)
- `name`: String
- `category`: Enum (`INDIVIDUAL`, `TEAM`)
- `is_olympic`: Boolean
- `is_national_priority`: Boolean

### Athlete
- `id`: UUID (PK)
- `kid`: Optional String (Indexed)
- `encrypted_name`: Binary / String (Encrypted)
- `encrypted_dob`: Binary / String (Encrypted)
- `encrypted_guardian`: Optional Binary / String (Encrypted)
- `gender`: Enum (`MALE`, `FEMALE`, `OTHER`)
- `state_id`: String (FK)
- `district_id`: String (FK, Indexed)
- `primary_sport_id`: UUID (FK)
- `consent_status`: Enum (`GRANTED`, `REVOKED`, `PENDING`)
- `verification_status`: Enum (`SUBMITTED`, `UNDER_REVIEW`, `VERIFIED`, `REJECTED`, `NEEDS_INFO`)
- `is_synthetic`: Boolean (Default: True for test seeds)

### PipelineSnapshot
- `id`: UUID (PK)
- `state_id`: String
- `district_id`: String
- `sport_id`: UUID
- `age_band`: String (`U-14`, `U-17`, `U-19`, `SENIOR`)
- `identified_count`: Integer
- `verified_count`: Integer
- `supported_count`: Integer
- `progressed_count`: Integer
- `is_suppressed`: Boolean (True if count < 5)
- `as_of`: DateTime

### AuditLog
- `id`: UUID (PK)
- `timestamp`: DateTime (UTC)
- `actor_id`: String
- `actor_role`: String
- `actor_district`: Optional String
- `action`: String (e.g. `READ_MINOR_RECORD`, `SUBMIT_VERIFICATION`)
- `target_entity`: String
- `target_id`: String
- `payload_hash`: String (SHA-256)
- `prev_hash`: String (Tamper-evident chain)
