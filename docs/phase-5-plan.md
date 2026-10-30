# Phase 5 Plan: State Adapters & Offline PWA Capabilities

Following the AI SDLC protocol defined in [IDEAS.md](file:///Users/apple/projects/sports-network-agent/IDEAS.md) and [docs/04-phases.md](file:///Users/apple/projects/sports-network-agent/docs/04-phases.md), Phase 5 implements the modular state configuration adapter contract, regional localization (English, Hindi, Marathi), and offline sync protocol with deterministic conflict resolution.

---

## 1. Architectural Principles & Invariants

1. **Sandboxed State Adapter Manifest**:
   - Each state loads a versioned adapter manifest (e.g. `MH` Maharashtra, `HR` Haryana).
   - Manifest defines: state-specific sports priorities, state schemes, local language packs, and custom demographic age limits.
   - **Hard Invariant**: Adapters **cannot** alter core database schema, drop core tables, or delete central records.
2. **Offline-First Sync Protocol**:
   - For `DISTRICT_OFFICER` and field verifiers working in low/no connectivity areas.
   - Client records mutations locally in an IndexedDB queue.
   - When connectivity resumes, client pushes batch sync to `/api/v1/sync/batch`.
3. **Deterministic Conflict Resolution Matrix**:
   - **Verification / Eligibility fields**: *Server wins*. Client cannot unilaterally override officer verification or sanction states during offline sync.
   - **Contact / Profile / Non-critical fields**: *Last-write-wins* based on UTC timestamp.
   - **Conflicts surfaced**: If a conflict occurs, the response flags `conflict_detected: true` with conflicting field details for officer review.
4. **Multilingual Localization**:
   - Bundled dictionary support for `en` (English), `hi` (Hindi), and `mr` (Marathi).

---

## 2. Component Structure

```text
backend/app/
├── core/
│   ├── state_adapter.py      # State manifest loader, schema protection guards
│   ├── sync_protocol.py      # Batch sync resolver with conflict matrix
│   └── seed_phase5.py        # Seed MH and HR state adapter manifests
├── models/
│   └── entities.py           # Added StateAdapterManifest & OfflineSyncRecord models
├── schemas/
│   └── dto.py                # SyncBatchRequest, SyncBatchResponse, StateManifestResponse
└── api/
    └── routes.py             # /adapters/states/{state_id}, /sync/batch, /sync/conflicts

frontend/src/
├── locales/
│   ├── en.json
│   ├── hi.json
│   └── mr.json
└── App.tsx                   # Language switch (EN/HI/MR), Offline simulation bar, Sync Queue
```

---

## 3. Data Model Extensions

```python
class StateAdapterManifest(Base):
    __tablename__ = "state_adapter_manifests"
    id = Column(String, primary_key=True)
    state_id = Column(String, unique=True, index=True, nullable=False)
    state_name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    primary_language = Column(String, default="hi")
    supported_languages_json = Column(Text, nullable=False)
    priority_sports_json = Column(Text, nullable=False)
    state_policies_json = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class OfflineSyncRecord(Base):
    __tablename__ = "offline_sync_records"
    id = Column(String, primary_key=True)
    client_sync_id = Column(String, unique=True, index=True, nullable=False)
    entity_name = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    client_timestamp = Column(DateTime, nullable=False)
    server_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    payload_json = Column(Text, nullable=False)
    status = Column(String, default="APPLIED") # APPLIED, CONFLICT_SERVER_WON, REJECTED
    conflict_notes = Column(Text, nullable=True)
    submitted_by = Column(String, ForeignKey("users.id"), nullable=False)
```

---

## 4. API Endpoints Contract

1. `GET /api/v1/adapters/states/{state_id}`
   - Returns versioned state adapter configuration and localized metadata.
2. `POST /api/v1/sync/batch`
   - Accepts array of offline queue actions. Evaluates conflict resolution matrix, commits non-conflicting mutations, flags conflicts.
3. `GET /api/v1/sync/conflicts`
   - Surfaces unresolved synchronization conflicts for human review.

---

## 5. Acceptance Test Matrix (`tests/test_phase5.py`)

- **Test 1: Schema Protection Invariant**: State adapter configuration cannot inject or modify core database table structures.
- **Test 2: Offline Batch Sync Protocol**: Batch of 50 offline queued updates processes accurately without duplicates.
- **Test 3: Conflict Matrix (Server Wins on Verification)**: Offline attempt to change athlete verification status from `REJECTED` to `VERIFIED` is overridden by server state.
- **Test 4: Conflict Matrix (Last-Write-Wins on Contacts)**: Offline update to guardian contact reference succeeds when timestamp is newer.
- **Test 5: Localization Dictionary Verification**: Ensures critical terms ("Athlete", "Verification", "Consent", "Gaps") are present in English, Hindi, and Marathi dictionaries.
