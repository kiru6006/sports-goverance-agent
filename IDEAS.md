

---

# PHASE 0: Scaffold and Platform Core
**Deliverables**
- Monorepo, Docker Compose (api, web, postgres+postgis), CI pipeline
- Auth stub with 4 seeded roles: `NATIONAL_ADMIN`, `STATE_OFFICER`, `DISTRICT_OFFICER`, `COACH`
- RBAC dependency for FastAPI with geography scope
- Audit log middleware and table
- Angular shell: login stub, role-based nav, lazy routes, route guards
- Health endpoints, OpenTelemetry wiring, structured logging
- Seed: 2 states, 4 districts, 10 synthetic users

**Acceptance criteria**
- `docker compose up` brings up all services; `/healthz` returns 200
- A `DISTRICT_OFFICER` request for another district returns 403 (tested)
- Every mutating request writes an audit row (tested)
- CI passes on a clean clone

**STOP.** Wait for review before Phase 1.

---

# PHASE 1: Unified Registry
**Entities:** `Athlete`, `Trainer`, `Institution`, `Affiliation`, `Achievement`, `JourneyEvent`, `Sport`, `Facility`

**Backend**
- CRUD with pagination, filtering, sorting (sport, district, age band, status)
- Age band computed from DOB, not stored
- Duplicate detection on submit: fuzzy match on name + DOB + district, returns candidate matches, never auto-merges
- Verification workflow: `SUBMITTED → UNDER_REVIEW → VERIFIED | REJECTED | NEEDS_INFO`. Only DISTRICT_OFFICER or above can verify. Coaches cannot verify their own athletes.
- Journey timeline per athlete (injury, break, transition, competition)

**Frontend**
- Registry list (ag-grid): server-side row model, filters by sport/district/age band/status
- Athlete profile: personal, education, trainers, affiliations, achievements, journey timeline
- Onboarding form with minor-consent step that blocks submit until consent status is set
- Verification queue for district officers

**Acceptance criteria**
- Minor record is invisible to a STATE_OFFICER and to a DISTRICT_OFFICER of another district (tested)
- Duplicate candidates are returned, not merged, on a seeded duplicate (tested)
- Verification transitions are enforced by a state machine; invalid transitions return 409 (tested)
- ag-grid list loads 10k synthetic rows with server-side paging under 300 ms p95 (load test with k6 or Locust)

**STOP.** Wait for review before Phase 2.

---

# PHASE 2: Pipeline Diagnosis
**Entities:** `PipelineSnapshot` (materialized view or aggregated table), `EquipmentItem`, `EquipmentLoan`, `FacilityUtilisation`

**Backend**
- Aggregations: athletes identified per 100k population (population table seeded, marked synthetic), per sport × district × age band
- Conversion funnel: identified → verified → supported → progressed (stage transitions derived from events)
- Gap detection rule: flag cells where identified count is below a configurable threshold relative to district peers. Output `reasons[]`.
- Equipment inventory with lending log and return status
- Refresh strategy for aggregates: scheduled job, with `as_of` timestamp returned on every response

**Frontend**
- Heatmap: sport × district, colour by gap score (ag-charts)
- Funnel chart per state and per sport
- Drill-down: heatmap cell → athlete list (RBAC-scoped)
- Equipment loan UI

**Acceptance criteria**
- Aggregates match a brute-force recomputation on seed data (tested)
- Every gap flag includes `reasons[]` with the threshold used (tested)
- Dashboard shows `as_of` timestamp

**STOP.** Wait for review before Phase 3.

---

# PHASE 3: Support Linkage
**Entities:** `Scheme` (with versioned `SchemeRule`), `EligibilityResult`, `Opportunity`, `OpportunityApplication`, `TrainerCertification`, `Placement`

**Backend**
- Scheme catalogue with versioned rules (JSON schema validated). Only `approved` rules are used for eligibility.
- Eligibility engine: input athlete profile, output `{eligible, reasons[], missing_fields[], rule_version, source_refs[]}`
- Opportunity board: quota rules, open slots, application tracking. No auto-selection.
- Trainer certification tracker: course, status, expiry, placement history
- Notifications: queued via outbox pattern. Channel adapters for email and SMS, stubbed.

**Frontend**
- Scheme admin screen (DRAFT → APPROVED workflow, with approver different from author)
- Athlete "eligible schemes" panel with reasons and missing fields
- Opportunity board with application status
- Trainer certification dashboard

**Acceptance criteria**
- Draft rules never affect eligibility (tested)
- Maker-checker enforced on scheme approval (tested)
- Eligibility output includes `rule_version` and `source_refs` (tested)
- Outbox delivers notifications exactly once under retry (tested)

**STOP.** Wait for review before Phase 4.

---

# PHASE 4: Agent Layer (only after Phases 1–3 are accepted)
**Scope**
- `agent-svc`: tool-calling over existing APIs. Tools: `search_athletes`, `get_pipeline_gaps`, `check_eligibility`, `list_opportunities`, `draft_report`.
- RAG over approved documents only (scheme guidelines, circulars) using pgvector. Chunks store `source_document`, `page`, `clause_id`.
- Every answer returns citations. Answers without a source must say "no source found."
- Human gates: `draft_report` output is a draft. Any action that changes a record or moves money requires an explicit approval endpoint.
- Agent actions logged to `audit_log` with prompt hash, tool calls, and model version.

**Acceptance criteria**
- Agent cannot call write tools without an approval token (tested)
- Agent respects RBAC: a DISTRICT_OFFICER prompt cannot retrieve another district's data (tested with adversarial prompts)
- Citation rate: 100% of policy answers cite a source (evaluated on a 50-question golden set)

**STOP.** Wait for review before Phase 5.

---

# PHASE 5: State Adapters and Offline Sync
**Scope**
- State adapter contract: state config (languages, state schemes, state sports list) loaded as versioned config. Adapters cannot alter core schema or delete central records.
- Offline-first PWA for DISTRICT_OFFICER and VILLAGE roles: IndexedDB queue, conflict resolution (server wins on verification fields, last-write-wins on contact fields, conflicts surfaced to user)
- Regional language packs (Hindi, English, plus 2 states' languages)

**Acceptance criteria**
- Adapter cannot delete or modify core-schema records (tested)
- Offline edits sync correctly after reconnect with 50 queued changes (tested)

---

# OUTPUT FORMAT FOR EACH PHASE
1. Plan: tree, data model diff, API contract (OpenAPI excerpt), task list
2. Wait for approval
3. Implementation with tests
4. Summary: what was built, test results, open ASSUMPTIONS, known gaps
5. Stop


# CONTEXT
Phase 0 is accepted. The NSIS monorepo, Docker Compose, CI, auth stub with 4 seeded roles, RBAC dependency, audit middleware, Angular shell, and seed data (2 states, 4 districts, 10 synthetic users) exist. All RULES from the base prompt still apply.

# PHASE 1 GOAL
Build the Unified Registry: athletes, trainers, institutions, affiliations, achievements, journey events, sports, and facilities, with a verification workflow and a duplicate-detection step that never auto-merges.

# STEP 0: CARRY-OVER CHECK (before planning)
1. Run `docker compose up` and the CI pipeline. Report any failures before starting.
2. Confirm the RBAC dependency, audit middleware, and seeded roles still work.
3. List any Phase 0 gaps in `docs/ASSUMPTIONS.md` or as a `KNOWN_GAPS` section. Do not silently fix Phase 0 code without flagging it.

# STEP 1: PLAN ONLY (wait for approval)
Output:
- Folder tree for `modules/registry/`, `modules/identity/` (extended), and `modules/facilities/`
- Data model diff (tables, columns, indexes, constraints, enum values)
- Alembic migration plan
- API contract (OpenAPI excerpt for every endpoint)
- Verification state machine diagram (Mermaid)
- Task list with test plan per task
- Any `# ASSUMPTION:` items

Do not write implementation code until I approve.

# STEP 2: IMPLEMENTATION SCOPE

## Entities
| Entity | Key Fields | Notes |
|---|---|---|
| `Sport` | code, name, federation, is_olympic, is_national | Seeded from a synthetic taxonomy file |
| `Athlete` | id, name, dob, gender, district_id, sports[], guardian_ref, consent_status, verification_status, verification_ref | `age_band` derived from DOB, not stored. `guardian_ref` required when under 18. |
| `Trainer` | id, name, sports[], district_id, certifications[], verification_status | Cannot be an athlete's own verifier |
| `Institution` | id, type (school\|college\|academy\|club), name, district_id, sports_facilities[] | |
| `Affiliation` | athlete_id, trainer_id \| institution_id, role, valid_from, valid_to | Exactly one of trainer_id or institution_id |
| `Achievement` | athlete_id, sport_id, event, level (local\|district\|state\|national\|intl), result, date | |
| `JourneyEvent` | athlete_id, type (injury\|break\|transition\|competition\|training_start), date, notes | Append-only |
| `Facility` | id, name, type, district_id, geo_point (PostGIS), sports[] | Inventory only; utilisation is Phase 2 |

## Backend requirements
- **CRUD with pagination, filtering, sorting** on sport, district, age band, verification status. Use cursor pagination.
- **Age band** is derived at query time from DOB using a configurable band table (for example U-10, U-14, U-17, U-19, Senior, Post-career). Store band definitions as config.
- **Duplicate detection** on create and on submit:
  - Fuzzy match on normalised name, DOB (exact or within 1 year), and district
  - Return `candidates[]` with `score` and `match_fields[]`
  - Never auto-merge. Merging is a separate authorised action, out of scope for this phase.
- **Verification state machine:**
  - States: `SUBMITTED → UNDER_REVIEW → VERIFIED | REJECTED | NEEDS_INFO`
  - `NEEDS_INFO → SUBMITTED` on resubmit
  - Invalid transitions return 409 with the allowed next states
  - Only `DISTRICT_OFFICER` or above can verify, and only within their district scope
  - Coaches cannot verify any athlete they coach
  - Every transition writes to `audit_log` with before/after state
- **Minor-record rules** (enforced in the service layer and API, not only the UI):
  - Records for athletes under 18 are visible only to: the assigned coach, the district officer of that district, and the guardian reference holder
  - `consent_status` must be set before submit. Submit returns 422 if it is missing.
  - Minor records are hidden from STATE_OFFICER and from other-district DISTRICT_OFFICERs. Return 404, not 403, so existence is not leaked.
- **Journey timeline** is append-only. Edits and deletes are not allowed; corrections are new events that reference the original.
- **Audit:** every read of a minor record writes an audit row.
- **Facilities:** geo_point stored as PostGIS geography. Endpoint to list facilities within a radius of a point, RBAC-scoped.
- **Seed data:** generator script producing 10k synthetic athletes, 1k trainers, 500 institutions, and 2k facilities across the 4 seeded districts. Synthetic names only. Mark all seed data `is_synthetic=true`.

## Frontend requirements (Angular standalone, signals)
- **Registry list:** ag-grid with server-side row model. Filters for sport, district, age band, and status. Column state persisted per user.
- **Athlete profile:** tabs for Personal, Education, Trainers, Affiliations, Achievements, Journey timeline. Minor profiles show a "restricted" banner.
- **Onboarding form:** multi-step. The minor-consent step blocks progression until `consent_status` is set. Duplicate-candidate panel appears before final submit, with a "this is a different person" confirmation.
- **Verification queue:** district officers see only their district's `UNDER_REVIEW` items. Actions: verify, reject, request info, each with a required reason field.
- **Route guards** for every new route, matching backend RBAC.

## Non-functional requirements
- Server-side paging: p95 under 300 ms for a 10k-row list at page size 50, measured with k6 or Locust against the Compose stack
- Indexes on `district_id`, `verification_status`, `dob`, and a trigram index on normalised names (pg_trgm)
- All list endpoints return `total` and `next_cursor`

# STEP 3: ACCEPTANCE CRITERIA (must all pass, each with a test)
1. A minor record is not returned to a STATE_OFFICER or to a DISTRICT_OFFICER of another district. Response is 404.
2. Duplicate detection returns `candidates[]` for a seeded duplicate pair and does not merge them.
3. Invalid verification transitions return 409 with `allowed_next[]`.
4. A coach cannot verify their own athlete (negative test).
5. Submitting a minor without `consent_status` returns 422.
6. Every read of a minor record writes an `audit_log` row (tested).
7. Journey events cannot be updated or deleted via the API (tested).
8. Radius query returns only facilities in the caller's scope (tested).
9. Age band is correct at band boundaries, including the day of birthday (parametrised test).
10. Load test: 10k-row list, page size 50, p95 under 300 ms. Attach the k6 or Locust report.
11. Frontend: Playwright test covers onboarding of a minor through to verification.
12. CI passes on a clean clone.

# STEP 4: DELIVERABLES
1. Plan (already approved in Step 1)
2. Implementation with migrations and seed generator
3. Test results: pytest coverage report, Vitest results, Playwright result, load-test report
4. `docs/ASSUMPTIONS.md` updated, with each `# ASSUMPTION:` listed
5. `docs/KNOWN_GAPS.md`: anything not built, with reason
6. Short summary: what was built, what failed, what needs my decision

# STOP
Do not begin Phase 2. Wait for review.

# CONTEXT
Phase 0 and Phase 1 are accepted. The NSIS monorepo, Docker Compose, CI, RBAC, audit middleware, Angular shell, and the Unified Registry (Sport, Athlete, Trainer, Institution, Affiliation, Achievement, JourneyEvent, Facility, verification state machine, duplicate detection, minor-record rules) exist. All RULES from the base prompt still apply.

# PHASE 2 GOAL
Build Pipeline Diagnosis: aggregate registry data into a sport × district × age-band view, derive a conversion funnel, flag gaps with explainable reasons, and track equipment and facility utilisation. Output supports decisions. It does not rank or exclude people.

# STEP 0: CARRY-OVER CHECK (before planning)
1. Run `docker compose up`, the test suite, and CI. Report failures before starting.
2. Confirm Phase 1 minor-record rules still hold (404 for out-of-scope minors, audit on every minor read). Aggregates must not leak minor-level data.
3. Confirm the Phase 1 load test still meets p95 < 300 ms. Record the baseline.
4. List Phase 1 gaps in `docs/KNOWN_GAPS.md`. Do not silently fix Phase 1 code without flagging it.

# STEP 1: PLAN ONLY (wait for approval)
Output:
- Folder tree for `modules/pipeline/`, `modules/equipment/`, and `modules/utilisation/`
- Data model diff: new tables, columns, indexes, enum values
- Aggregation strategy: materialised view vs. aggregate table, with refresh cadence and `as_of` handling
- Funnel stage definitions (see Step 2) with the event or field that triggers each transition
- Gap-detection algorithm, written out in plain language and as pseudocode
- Alembic migration plan
- API contract (OpenAPI excerpt per endpoint)
- Task list with test plan per task
- `# ASSUMPTION:` items, especially the population source and gap thresholds

Do not write implementation code until I approve.

# STEP 2: IMPLEMENTATION SCOPE

## Entities
| Entity | Key Fields | Notes |
|---|---|---|
| `Population` | district_id, age_band, gender, count, source, is_synthetic | Seeded. Real source to be confirmed by ministry. |
| `PipelineSnapshot` | sport_id, district_id, age_band, identified, verified, supported, progressed, as_of | Materialised view or aggregate table. Rebuilt by scheduled job. |
| `SupportRecord` | athlete_id, support_type (equipment\|nutrition\|training_grant\|coaching\|facility_access), status, start, end | Phase 2 provides the table and manual entry only. Phase 3 links it to schemes. |
| `EquipmentItem` | id, facility_id, type, condition, qr_code, status | QR code is a string identifier, not a generated image. |
| `EquipmentLoan` | id, item_id, borrower_type, borrower_id, issued_at, due_at, returned_at, condition_out, condition_in | Append-only. Corrections are new records. |
| `FacilityUtilisation` | facility_id, period (date), sessions, athlete_count, hours_used | Monthly grain. Manual entry in Phase 2. |

## Funnel definitions (must be explicit in the plan)
- **identified:** athlete record exists in the registry, any status
- **verified:** `verification_status = VERIFIED`
- **supported:** at least one `SupportRecord` with status `ACTIVE` or `COMPLETED`
- **progressed:** an `Achievement` at level `district`, `state`, `national`, or `intl` after the first support record
- Stages are cumulative. An athlete counted as progressed is also counted as verified and supported.
- Minor athletes are counted in aggregates, but no minor identifiers appear in any aggregate response.

## Backend requirements
- **Aggregations:** identified, verified, supported, and progressed counts per sport × district × age band. Also per-100k rates using `Population`.
- **Small-cell suppression:** if any cell count is below 5, return `suppressed: true` with no count. Prevents re-identification of individuals in small districts.
- **Gap detection:**
  - For each sport × age band, compare each district's identified-per-100k to the median of its state peers
  - Flag cells below a configurable fraction of that median (default 0.5, stored as config, versioned)
  - Every flag returns `reasons[]` with the threshold, the peer median, the district value, and `as_of`
  - Flags are advisory. They do not trigger any automatic action.
- **Conversion rates:** stage-to-stage conversion per sport and per state, with denominators shown
- **Refresh:** scheduled job rebuilds `PipelineSnapshot`. Every API response includes `as_of`. Expose a `last_refreshed_at` health field.
- **Equipment:**
  - Issue, return, and transfer endpoints. Returns require `condition_in`.
  - Overdue query: items with `due_at < now()` and no `returned_at`
  - Append-only loan log. Edits and deletes return 405.
- **Utilisation:** monthly entry per facility. Utilisation rate = hours_used / (facility open hours from config). Flag facilities below configurable threshold, with reasons.
- **RBAC:** all aggregates are scoped by geography. A DISTRICT_OFFICER gets district-level aggregates only. A STATE_OFFICER gets state and its districts. NATIONAL_ADMIN gets everything.
- **Audit:** every drill-down that reaches athlete-level rows writes an audit entry. Aggregate-only reads are logged at the request level.

## Frontend requirements (Angular standalone, signals)
- **Heatmap:** sport × district grid, colour by gap score, using `ag-charts-angular`. Tooltip shows the count, the per-100k rate, and the peer median. Suppressed cells show "<5" with no value.
- **Funnel:** per-state and per-sport funnel with conversion labels and denominators
- **Drill-down:** heatmap cell → RBAC-scoped athlete list (uses Phase 1 list component). Minor rows show the restricted banner.
- **Equipment:** issue, return, and overdue views. Scan input accepts a QR string.
- **Utilisation:** monthly entry form and a utilisation trend chart per facility
- **As-of banner:** every dashboard shows `as_of` and the data age in days. Show a warning if data is older than 35 days.
- **Route guards** for all new routes, matching backend RBAC

## Non-functional requirements
- Aggregate endpoint p95 < 500 ms for the 4-district seed and for a 10x scaled seed (40 districts). Measure with k6 or Locust.
- Snapshot rebuild completes in under 5 minutes on the 10k-athlete seed
- Indexes: `(sport_id, district_id, age_band)` on `PipelineSnapshot`; `(item_id, returned_at)` on `EquipmentLoan`; `(facility_id, period)` on `FacilityUtilisation`

# STEP 3: ACCEPTANCE CRITERIA (each must have a test)
1. `PipelineSnapshot` matches a brute-force recomputation from raw registry data on the seed (exact match)
2. Cells with count < 5 return `suppressed: true` and no count (tested, including the boundary at 4 and 5)
3. Every gap flag includes `reasons[]` with threshold, peer median, district value, and `as_of` (tested)
4. Funnel stages are cumulative: no athlete is counted as progressed without being supported, verified, and identified (property-based test)
5. A DISTRICT_OFFICER requesting another district's aggregate gets 403. A STATE_OFFICER gets only their state (tested)
6. Minor athletes never appear by identifier in any aggregate or export response (tested)
7. Equipment loan log rejects PUT and DELETE with 405 (tested)
8. Overdue query returns only unreturned loans past due date (tested with fixed clock)
9. Utilisation rate calculation matches a worked example in the test fixtures (tested)
10. Playwright test: open heatmap, drill into a non-suppressed cell, confirm restricted banner on a minor row
11. Load test attached for the 4-district and 40-district seeds
12. CI passes on a clean clone

# STEP 4: DELIVERABLES
1. Approved plan from Step 1
2. Implementation with migrations, the snapshot job, and seed extension (synthetic population table added)
3. Test results: pytest coverage, Vitest, Playwright, load-test reports
4. `docs/ASSUMPTIONS.md` updated, including population source, gap threshold default, and suppression threshold
5. `docs/KNOWN_GAPS.md` updated
6. Short summary: what was built, what failed, what needs my decision

# WARNINGS TO SURFACE IN THE SUMMARY
- Gap heatmaps can be misread as district performance rankings. Add a "not a performance score" label to the UI and the export.
- Per-100k rates in small districts are volatile. The UI must show denominators and suppressed cells.
- Do not add a medal or outcome metric to the heatmap in this phase. Pipeline metrics only.

# STOP
Do not begin Phase 3. Wait for review.

# CONTEXT
Phases 0–2 are accepted. The NSIS monorepo, RBAC, audit middleware, Angular shell, Unified Registry (with minor-record rules and verification workflow), and Pipeline Diagnosis (snapshots, suppression, gap flags, equipment, utilisation) exist. All RULES from the base prompt still apply.

# PHASE 3 GOAL
Build Support Linkage: connect identified athletes to support schemes and opportunities, track trainer certification and placement, and deliver notifications reliably. Every eligibility output is explainable, versioned, and traceable to an approved source. Nothing is auto-approved, auto-excluded, or auto-selected.

# STEP 0: CARRY-OVER CHECK (before planning)
1. Run `docker compose up`, the test suite, and CI. Report failures before starting.
2. Re-run Phase 1 and Phase 2 acceptance tests. Confirm minor-record 404 behaviour, audit on minor reads, and aggregate suppression still hold.
3. Confirm the `SupportRecord` table from Phase 2 is still the single source for support status. Phase 3 links to it. It must not create a parallel support table.
4. Update `docs/KNOWN_GAPS.md` with Phase 2 gaps. Flag any silent fixes.

# STEP 1: PLAN ONLY (wait for approval)
Output:
- Folder tree for `modules/schemes/`, `modules/eligibility/`, `modules/opportunities/`, `modules/certification/`, and `modules/notifications/`
- Data model diff: tables, columns, indexes, enum values
- Scheme rule JSON Schema (full definition)
- Eligibility evaluation algorithm in plain language and pseudocode
- Maker-checker state machine (Mermaid)
- Outbox pattern design: table, relay worker, idempotency key scheme, retry and dead-letter policy
- Alembic migration plan
- API contract (OpenAPI excerpt per endpoint)
- Task list with test plan per task
- `# ASSUMPTION:` items

Do not write implementation code until I approve.

# STEP 2: IMPLEMENTATION SCOPE

## Entities
| Entity | Key Fields | Notes |
|---|---|---|
| `Scheme` | id, code, name, level (central\|state), owner_body, is_placeholder, verify_with_ministry | Name and amounts are placeholders until ministry verifies |
| `SchemeRule` | id, scheme_id, version, rule_json, effective_from, effective_to, source_document, source_page, source_clause, status (draft\|approved\|retired), author_id, approver_id, approved_at | Immutable once approved. New version for changes. |
| `EligibilityResult` | id, athlete_id, scheme_id, rule_version, eligible, reasons[], missing_fields[], source_refs[], evaluated_at, evaluated_by | Append-only. Stored for audit. |
| `Opportunity` | id, type (job\|sponsorship\|quota), employer, eligibility_rule_id, slots, district_scope, state_scope, deadline, status | Quota rules reference an approved `SchemeRule` or a document |
| `OpportunityApplication` | id, opportunity_id, athlete_id, status (submitted\|shortlisted\|rejected\|withdrawn\|offered\|accepted), status_reason, updated_by | Status changes are recorded as events. Applicant selection is done by the employer, not NSIS. |
| `TrainerCertification` | id, trainer_id, course, provider, issued_on, expires_on, status (active\|expired\|revoked) | Expiry computed at query time |
| `Placement` | id, trainer_id, institution_id, role, start, end | |
| `OutboxMessage` | id, channel (email\|sms), recipient_ref, template_id, payload, status, idempotency_key, attempts, next_attempt_at, created_at | Written in the same transaction as the business change |

## Scheme rule JSON Schema (required fields)
- `criteria[]`: each with `field`, `operator` (eq, in, gte, lte, between, exists), `value`, `reason_text`
- `required_fields[]` for the evaluator
- `valid_for`: `{states[], districts[], sports[], age_bands[], gender[]}` (empty list means no restriction)
- `schema_version`
- Rules are validated against the JSON Schema on save. Invalid rules return 422.
- No free-form expressions or code. Operators are a closed set.

## Eligibility engine
- Input: athlete profile fields used by the rule, and the rule version
- Only `status = approved` rules are evaluated. Draft and retired rules are invisible to this path.
- Output: `{eligible, reasons[], missing_fields[], rule_version, source_refs[], evaluated_at}`
- If a required field is missing, return `eligible: null` with `missing_fields[]`. Never return false for missing data.
- Each criterion result is recorded in `reasons[]` with its `reason_text`.
- Results are written to `EligibilityResult` (append-only). The same input and rule version must produce the same output (deterministic, tested).
- Minor athletes: evaluation is allowed only for the assigned coach, the district officer, and the guardian reference holder. Results for minors are never included in aggregate responses.

## Maker-checker for schemes
- States: `DRAFT → SUBMITTED_FOR_APPROVAL → APPROVED | REJECTED → (DRAFT)`
- `approver_id` must differ from `author_id`. Enforced in the service layer and the DB constraint.
- Only NATIONAL_ADMIN or STATE_OFFICER (for state-level schemes) can approve, within their scope.
- `APPROVED` rules are immutable. Changes create a new draft version.
- Retiring a rule sets `status = retired` and `effective_to`. Historical `EligibilityResult` rows keep their `rule_version`.

## Opportunity board
- Lists open opportunities filtered by the athlete's eligibility result (eligible or null, never silently filtered out).
- Applications are recorded. NSIS does not select, rank, or shortlist athletes.
- Status changes require `status_reason`.
- Quota opportunities must reference an approved rule or a source document.

## Trainer certification
- Status and expiry tracking. Expiry alerts at 90, 30, and 7 days.
- Placement history per trainer.
- Revoked certifications block new placements (enforced by service layer, tested).

## Notifications and outbox
- Business write and `OutboxMessage` insert happen in one transaction.
- Relay worker polls pending messages with `SELECT ... FOR UPDATE SKIP LOCKED`.
- Each message carries an `idempotency_key`. Channel adapters must honour it.
- Retry with exponential backoff, max 5 attempts, then `status = dead_letter` and an alert event.
- Email and SMS adapters are stubs that log to a file. No real sending in this phase.
- Notification payloads contain no minor identifiers. Use a reference token that the recipient opens inside the app.

## Frontend requirements (Angular standalone, signals)
- **Scheme admin:** list by status, rule editor with JSON Schema validation shown inline, submit-for-approval, approve/reject with required reason. Approver cannot be the author. Placeholder schemes show a "Placeholder — verify with ministry" badge.
- **Athlete eligibility panel:** per scheme, shows `eligible` / `not determined` / `not eligible`, the reasons list, missing fields with links to edit, rule version, and source reference.
- **Opportunity board:** filters by sport, district, and eligibility. Application status with reason. Restricted banner on minor rows.
- **Trainer certification dashboard:** expiry countdown, placement history, blocked-placement message when revoked.
- **Route guards** for all new routes.

## Non-functional requirements
- Eligibility evaluation p95 < 200 ms per athlete per scheme
- Outbox relay: throughput of 1,000 messages per minute on the Compose stack
- No eligibility or opportunity endpoint returns more than 50 rows per page

# STEP 3: ACCEPTANCE CRITERIA (each must have a test)
1. A draft or retired rule never affects eligibility output (tested)
2. Maker-checker: the author cannot approve their own rule. DB constraint and API both enforce it (tested)
3. Approved rules are immutable. An update attempt returns 409 (tested)
4. Eligibility output includes `rule_version` and `source_refs[]` for every result (tested)
5. Eligibility is deterministic: same inputs and rule version produce identical output across 1,000 randomised runs (property-based test)
6. Missing required field returns `eligible: null` with `missing_fields[]`, never `false` (tested)
7. Invalid rule JSON returns 422 with the failing schema path (tested)
8. Outbox delivers each message exactly once under simulated relay crash and retry (tested with fault injection)
9. Notification payloads contain no minor identifiers (tested)
10. Revoked certification blocks placement creation (tested)
11. Opportunity application changes require `status_reason` (tested)
12. Minor eligibility results are not visible to unauthorised roles (tested, 404 response)
13. Playwright test: scheme approval by a second user, then an athlete eligibility panel showing reasons and rule version
14. CI passes on a clean clone

# STEP 4: DELIVERABLES
1. Approved plan from Step 1
2. Implementation with migrations, JSON Schema, outbox relay worker, and seed placeholder schemes (all marked `verify_with_ministry: true`)
3. Test results: pytest coverage, property-based test report, fault-injection results, Vitest, Playwright
4. `docs/ASSUMPTIONS.md` updated, with every `# ASSUMPTION:` listed and every placeholder scheme identified
5. `docs/KNOWN_GAPS.md` updated
6. Short summary: what was built, what failed, what needs my decision

# WARNINGS TO SURFACE IN THE SUMMARY
- Eligibility rules are a policy artefact. Engineering can implement the engine but cannot decide criteria. Counsel and the scheme owner must approve every rule before it leaves the placeholder state.
- Placeholder scheme names and amounts must not reach any officer-facing or athlete-facing screen as if they were real. The UI badge is required.
- NSIS must not imply that an athlete is selected or excluded from a quota. The opportunity board shows eligibility, not decisions.

# STOP
Do not begin Phase 4. Wait for review.

# CONTEXT
Phases 0–3 are accepted. The NSIS monorepo, RBAC, audit middleware, Angular shell, Unified Registry, Pipeline Diagnosis, and Support Linkage (schemes with maker-checker, eligibility engine, opportunity board, certification, outbox) exist. All RULES from the base prompt still apply.

# PHASE 4 GOAL
Build the Agent Layer: an `agent-svc` that answers official queries using existing APIs as tools, grounds policy answers in approved documents only, and cannot change any record or move any money without an explicit human approval. The agent is a read-mostly assistant with a gated write path. It is not a decision-maker.

# STEP 0: CARRY-OVER CHECK (before planning)
1. Run `docker compose up`, the full test suite, and CI. Report failures before starting.
2. Re-run Phase 1–3 acceptance tests. Confirm minor-record 404s, aggregate suppression, approved-only eligibility, maker-checker, and outbox exactly-once still hold.
3. Confirm the agent will call the same service layer and RBAC dependency as the REST API. It must not query the database directly or bypass the API's authorisation.
4. Confirm the pilot data from Phase 1–2 is real or clearly labelled. Record the data source in `docs/KNOWN_GAPS.md`.
5. Update `docs/KNOWN_GAPS.md` with Phase 3 gaps. Flag any silent fixes.

# STEP 1: PLAN ONLY (wait for approval)
Output:
- Folder tree for `apps/agent-svc/` and `modules/agent/` (tools, retrieval, guardrails, approvals, evals)
- Architecture diagram (Mermaid): user → agent-svc → tool layer → existing services; retrieval → pgvector; approval gate; audit sink
- Tool contract for every tool: name, input schema, output schema, RBAC requirement, read or write, approval required (yes/no)
- Document ingestion pipeline: source intake, parsing, chunking, metadata, embedding, approval status
- RAG retrieval design: chunk schema, top-k, filter-before-rank logic, reranking choice, citation format
- Approval flow (Mermaid sequence diagram): propose action → human review → approval token → execute → audit
- Guardrail design: input checks, output checks, refusal conditions
- Evaluation plan: golden set structure, adversarial set structure, metrics and thresholds
- Model choice and deployment: hosted vs self-hosted, data-residency implications, fallback model
- Alembic migration plan
- API contract (OpenAPI excerpt per endpoint)
- Task list with test plan per task
- `# ASSUMPTION:` items, especially model hosting and data residency

Do not write implementation code until I approve.

# STEP 2: IMPLEMENTATION SCOPE

## Tools (read tools execute directly; write tools only propose)
| Tool | Type | RBAC | Notes |
|---|---|---|---|
| `search_athletes` | read | caller's scope | Minor records follow Phase 1 rules; 404 for out-of-scope |
| `get_pipeline_gaps` | read | caller's scope | Returns Phase 2 gap flags with `reasons[]` and `as_of` |
| `check_eligibility` | read | caller's scope | Calls Phase 3 engine. Returns `reasons[]`, `source_refs[]`, `rule_version` |
| `list_opportunities` | read | caller's scope | Returns eligibility state, never a selection |
| `search_policy` | read | all authenticated roles | RAG over approved documents only |
| `draft_report` | draft | caller's scope | Output is a draft artefact, never auto-sent |
| `propose_record_change` | write | caller's scope | Creates a pending `ActionProposal`. Does not execute. |
| `propose_scheme_change` | write | NATIONAL_ADMIN / STATE_OFFICER | Creates a draft `SchemeRule` only. Approval stays with maker-checker. |

Rules:
- Tools are thin wrappers over the existing service layer. No raw SQL in tools.
- Every tool call is audit-logged: actor, role, tool name, input hash, output hash, model version, timestamp.
- The agent has no tool that approves, excludes, selects, or releases funds.

## Approval gate
- `ActionProposal`: id, actor_id, proposed_by_agent (bool), action_type, payload, scope, status (pending|approved|rejected|expired), approver_id, approved_at, expires_at
- Approval requires a human with the correct role, scope, and `approver_id != actor_id`
- Approval issues a single-use token bound to the proposal ID and payload hash
- Execution re-validates RBAC and payload hash at execution time. A changed payload invalidates the token.
- Proposals expire after 24 hours by default (configurable).

## Retrieval (RAG)
- Corpus: only documents with `status = approved` in the document registry. Unapproved uploads are not indexed for retrieval.
- Chunk schema: `chunk_id, document_id, source_document, page, clause_id, text, embedding, document_version, approved_at`
- Filter before rank: apply jurisdiction and status filters in the SQL query, then vector search. Never rank then filter.
- Top-k default 8, then rerank (cross-encoder or model-based; choice recorded in ADR).
- Answers must cite `source_document`, `page`, and `clause_id` for every factual claim.
- If no chunk clears the similarity threshold, return "no source found" and do not generate a policy answer.
- Retrieval results respect the caller's scope. A state-scoped document may be excluded for other states.

## Guardrails
- Input: reject prompts that request another user's data, bulk export of minor records, or instructions to bypass approval. Log the attempt.
- Output: block outputs containing Aadhaar-format numbers, minor identifiers in unauthorised contexts, or policy claims without citations.
- Prompt injection: retrieved document text is treated as data. Tool calls cannot be triggered by instructions found in retrieved text. Enforce by separating system instructions from retrieved content in the prompt structure and by allow-listing tool calls per request.
- Refusals are explicit, logged, and return a reason code.

## Model deployment
- Default: a hosted model only if the provider and region meet MeitY-empanelled, India-residency requirements. Otherwise use a self-hosted open-weight model. [Verify with counsel before selecting.]
- Model version pinned per deployment. Model version recorded on every audit entry.
- Fallback: if the primary model is unavailable, the agent returns a retrieval-only answer with citations, or a "service unavailable" message. It does not switch to an unapproved model silently.
- Timeouts and token budgets set per request. Tool-call depth capped (default 5).

## Evaluation
- Golden set: 50 policy questions with expected source clauses and expected answers. Citation rate must be 100%.
- Adversarial set: at least 30 prompts covering cross-district access, minor-data extraction, approval bypass, prompt injection through retrieved text, and requests for selection or exclusion decisions.
- Pass criteria: 100% refusal on adversarial write attempts; 0 cross-scope leaks; citation rate 100% on answered policy questions.
- Eval runs in CI on every change to prompts, tools, or retrieval config.

## Frontend requirements (Angular standalone, signals)
- **Agent panel:** chat-style interface with scope indicator (role and geography shown). Each answer shows citations as expandable source cards.
- **Draft report view:** draft badge, edit before export, no direct send.
- **Approval inbox:** pending `ActionProposal`s with diff view, approve/reject with required reason, expiry countdown.
- **No-source state:** clearly labelled "no approved source found."
- **Route guards** for agent routes.

## Non-functional requirements
- p95 first-token latency < 2 s for retrieval-only answers
- p95 full answer < 10 s for answers with up to 3 tool calls
- Tool-call depth ≤ 5; per-request token budget enforced
- Agent audit writes are synchronous with the response

# STEP 3: ACCEPTANCE CRITERIA (each must have a test)
1. Agent cannot call any write tool that executes a change without an approval token (tested)
2. `propose_record_change` creates a pending proposal and returns no executed effect (tested)
3. Approval token is bound to proposal ID and payload hash; a modified payload fails at execution (tested)
4. Approver cannot be the proposer (tested)
5. A DISTRICT_OFFICER prompt cannot retrieve another district's athletes, aggregates, or documents (adversarial suite, 0 leaks)
6. Minor records are not returned in any agent response to an unauthorised caller (tested, 404 path)
7. Retrieval excludes unapproved documents (tested by ingesting an unapproved document and querying for it)
8. Filter-before-rank: a query scoped to state A never returns chunks tagged state B, verified by query plan or test fixture (tested)
9. Every policy answer includes `source_document`, `page`, and `clause_id`. Golden set citation rate = 100% (CI gate)
10. No-source queries return "no source found" and no generated policy claim (tested)
11. Prompt injection in an ingested document does not trigger a tool call or change scope (adversarial test)
12. Every tool call and model response is audit-logged with model version (tested)
13. Fallback never switches to an unapproved model (tested by disabling the primary)
14. Eval suite runs in CI and fails the build below thresholds
15. Playwright test: agent answers a policy question with citations; a write proposal appears in the approval inbox and cannot be executed without approval
16. Latency targets met on the Compose stack; report attached
17. CI passes on a clean clone

# STEP 4: DELIVERABLES
1. Approved plan from Step 1
2. Implementation: agent-svc, tool layer, retrieval pipeline, approval gate, guardrails, eval suite, migrations
3. Test results: pytest coverage, golden-set and adversarial-set reports, Playwright, latency report
4. ADRs in `docs/ADRs/`: model hosting choice, reranker choice, approval token design
5. `docs/ASSUMPTIONS.md` updated, including model version, hosting region, and token budget defaults
6. `docs/KNOWN_GAPS.md` updated
7. Short summary: what was built, eval scores, failures, what needs my decision

# WARNINGS TO SURFACE IN THE SUMMARY
- An LLM agent over government data is a new accountability surface. Record every answer and tool call. Officials must be able to reconstruct why an answer was given.
- Citation accuracy is necessary but not sufficient. Sample answers with a human reviewer each sprint and track disagreement rate.
- Do not expose the agent to athletes or the public in this phase. Officials only, behind the existing auth.
- Counsel must sign off on the model hosting arrangement and the data-processing terms before any real personal data is sent to a model endpoint.

# STOP
Do not begin Phase 5. Wait for review.

# CONTEXT
Phases 0–4 are accepted. The NSIS monorepo, RBAC, audit middleware, Angular shell, Unified Registry, Pipeline Diagnosis, Support Linkage (schemes with maker-checker, eligibility engine, opportunity board, certification, outbox), and the Agent Layer exist. All RULES from the base prompt still apply.

# PHASE 5 GOAL
Add three capabilities: (1) a state adapter layer that lets each state extend config and data feeds without touching the central schema or central records, (2) an offline-first PWA mode for DISTRICT_OFFICER and VILLAGE roles with encrypted local storage and deterministic sync, and (3) regional language packs. Offline mode must not weaken the minor-record rules, the audit trail, or the verification workflow.

# STEP 0: CARRY-OVER CHECK (before planning)
1. Run `docker compose up`, the full test suite, and CI. Report failures before starting.
2. Re-run Phase 1–4 acceptance tests. Confirm minor-record 404s, aggregate suppression, approved-only eligibility, maker-checker, outbox exactly-once, and agent approval gating still hold.
3. Confirm the signed MoU list for each state adapter. Do not build an adapter for a state without a signed MoU. Record the list in `docs/KNOWN_GAPS.md`.
4. Confirm the Phase 4 agent works through the service layer. Adapters must not give the agent new data paths.
5. Update `docs/KNOWN_GAPS.md` with Phase 4 gaps. Flag any silent fixes.

# STEP 1: PLAN ONLY (wait for approval)
Output:
- Folder tree for `modules/adapters/`, `apps/web/src/app/offline/`, `apps/web/src/app/i18n/`, and `packages/adapter-sdk/`
- Adapter contract: a typed interface, its manifest schema, and the list of operations each adapter may and may not perform
- Adapter isolation design: how the runtime enforces the "no core schema or central record change" rule (DB role, schema namespace, or API boundary; pick one and justify it)
- Offline architecture diagram (Mermaid): IndexedDB store → sync engine → outbox queue → API → conflict resolver
- Local encryption design: key derivation, key storage, rotation, and wipe-on-logout
- Sync protocol: change-log format, idempotency keys, ordering, retry, and resumable upload
- Conflict resolution matrix: one row per field class (verification, identity, contact, journey, equipment, consent)
- Language pack strategy: i18n library choice, key naming, fallback chain, and how translation is sourced and reviewed
- Alembic migration plan (if any)
- API contract (OpenAPI excerpt for sync and adapter-config endpoints)
- Task list with test plan per task
- `# ASSUMPTION:` items, especially device policy, language list, and state adapter ownership

Do not write implementation code until I approve.

# STEP 2: IMPLEMENTATION SCOPE

## State adapter layer
- Adapter manifest (versioned JSON): `state_code`, `adapter_version`, `languages[]`, `state_sports[]`, `state_schemes[]` (references to `SchemeRule` drafts only), `data_feeds[]`, `signed_mou_ref`
- Adapters can add: state sports, state scheme rules (draft state only; approval stays with maker-checker), language packs, state-specific extension fields in namespaced extension tables (`ext_<state_code>_*`), and state data-feed mappings
- Adapters cannot: alter core tables, drop or rename core columns, delete or update central records, approve their own rules, or bypass RBAC
- Enforcement is tested at the database level (least-privilege DB role for adapter migrations) and at the API level
- Adapter activation requires `signed_mou_ref` to be present and a NATIONAL_ADMIN action. Deactivation does not delete data.
- Data feeds: pull-based ingestion through `ingestion-svc` with schema validation. Rejected rows go to a quarantine table with reasons. Nothing is written to the registry without validation.

## Offline-first PWA
- Scope: DISTRICT_OFFICER and VILLAGE roles only. COACH, STATE_OFFICER, and NATIONAL_ADMIN are online-only.
- Local store: IndexedDB, with records encrypted at rest using WebCrypto AES-GCM. Key is derived per session and never persisted in plaintext.
- Cached data: only the user's district scope and only what the user's current worklist requires. Minor records are cached only when the user is the assigned coach or district officer, and only for the active session.
- Logout and session expiry: wipe the IndexedDB store and key material. Test this.
- Offline actions allowed: create registry drafts, edit contact fields, add journey events, record equipment loans, and log facility utilisation.
- Offline actions not allowed: verification decisions, consent changes, scheme or eligibility actions, approvals, minor-record deletion. These return a "requires connection" state in the UI.
- Sync engine:
  - Each queued change has a client-generated UUID and an `idempotency_key`
  - Changes are sent in causal order per entity
  - Server applies each change once and returns the new version per entity
  - Failed changes retry with backoff. After 10 attempts, the change moves to a "needs review" queue shown to the user.
- Conflict resolution (from the matrix in Step 1):
  - Verification fields: server wins. Local edits are discarded and the user is shown the server value.
  - Identity fields (name, DOB, duplicate status): conflict is surfaced to the user, no auto-resolution
  - Contact fields: last-write-wins by server timestamp, with the overwritten value kept in audit
  - Journey events: append-only, so both are kept
  - Equipment and utilisation: conflict surfaced if the same item was issued twice offline
- Service worker: cache-first for static assets, network-first for API, with a clear offline banner and data-age indicator.

## Regional language packs
- Languages: Hindi, English, plus two state languages chosen by the first two signed-MoU states
- Angular i18n (`@angular/localize`) or Transloco. Pick one in the plan and record an ADR.
- Keys are semantic (`registry.athlete.verify.button`), never English sentences as keys
- Fallback chain: user language → English. Never show raw keys.
- Translations are marked `reviewed_by` and `reviewed_at`. Unreviewed strings are flagged in build output.
- Names and free text entered in any script are stored as UTF-8 unchanged. Duplicate detection (Phase 1) must handle transliteration variants. Document the gap if not solved.

## Frontend requirements (Angular standalone, signals)
- Offline banner and data-age indicator on every screen
- Sync status panel: pending count, failed count, needs-review queue with resolve actions
- Language switcher with persisted preference
- Route guards for offline-capable routes, matching backend RBAC
- Playwright tests run with the network throttled and then disconnected

## Non-functional requirements
- Sync of 50 queued changes completes in under 30 seconds on a 2G-equivalent throttled connection
- Local store size cap per user (default 200 MB, configurable); oldest non-pending cache evicted first, never pending changes
- Service worker update path tested: a new build does not corrupt the pending queue

# STEP 3: ACCEPTANCE CRITERIA (each must have a test)
1. Adapter cannot delete or modify a core-schema table or a central record (tested at DB role level and API level)
2. Adapter without a `signed_mou_ref` cannot be activated (tested)
3. Adapter deactivation preserves all data it created (tested)
4. Quarantined feed rows never reach the registry (tested with malformed fixtures)
5. Offline-cached minor records are not present for a user outside the assigned coach or district scope (tested)
6. Logout wipes IndexedDB and key material; a post-logout inspection finds no readable records (tested)
7. Encrypted store contains no plaintext PII when inspected directly (tested)
8. Offline verification and consent actions are blocked with the "requires connection" state (tested)
9. 50 queued changes sync exactly once after reconnect, including a simulated connection drop mid-sync (fault-injection test)
10. Conflict matrix: each field class produces the specified resolution (parametrised test, one case per class)
11. Verification conflict resolves to server value and the user is shown that value (tested)
12. Sync failure after 10 attempts moves the change to needs-review, not silent discard (tested)
13. Language fallback: a missing Hindi key renders the English string; no raw keys appear (tested)
14. Service worker update does not drop pending changes (tested)
15. Playwright: offline edit of a registry draft, reconnect, sync, and conflict resolution on a verification field
16. CI passes on a clean clone

# STEP 4: DELIVERABLES
1. Approved plan from Step 1
2. Implementation: adapter SDK, adapter runtime, offline sync engine, encryption module, i18n setup, two state adapter stubs (no real MoU data)
3. Test results: pytest coverage, Vitest, fault-injection report, Playwright (offline and throttled runs)
4. ADRs in `docs/ADRs/`: adapter isolation design, offline encryption design, i18n library choice, conflict matrix
5. `docs/ASSUMPTIONS.md` updated: device policy, cache cap, language list, adapter ownership
6. `docs/KNOWN_GAPS.md` updated: transliteration matching, any state without a signed MoU, any unsupported device class
7. Short summary: what was built, what failed, what needs my decision

# WARNINGS TO SURFACE IN THE SUMMARY
- Offline storage on shared district devices is the main personal-data exposure in this phase. Counsel must approve the device policy (cache scope, session length, wipe behaviour) before rollout.
- Adapters are a governance risk. A state adapter can change how the system behaves for its state. Require a change log and a NATIONAL_ADMIN review for every adapter version.
- Server-wins on verification is deliberate. Do not let offline edits change verification status under any circumstance.
- Translations of legal or eligibility text need review by a qualified translator and by counsel. Machine output is not acceptable for policy text.

# STOP
Phase 5 is the last phase in this plan. Wait for review and a decision on the next scope.

# CONTEXT
Phases 0–5 are accepted. NSIS includes the Unified Registry, Pipeline Diagnosis, Support Linkage, the Agent Layer, state adapters, and offline PWA. All RULES from the base prompt still apply.

# PHASE 6 GOAL
Prepare NSIS for a supervised pilot with real personal data. Add no new features. Close security, privacy, resilience, accessibility, and operability gaps, and produce the evidence a ministry IT security team and counsel will ask for.

# STEP 0: CARRY-OVER CHECK
1. Run `docker compose up`, the full test suite, the eval suite, and CI. Report failures.
2. Re-run acceptance tests for Phases 1–5. Any regression blocks this phase.
3. Consolidate `docs/KNOWN_GAPS.md` into a single prioritised list: blocker, pre-pilot, post-pilot.

# STEP 1: PLAN ONLY (wait for approval)
Output:
- Threat model (STRIDE per module) and trust boundaries diagram (Mermaid)
- Gap-closure plan mapped to each blocker in `KNOWN_GAPS.md`
- Data lifecycle map: collection → verification → use → retention → deletion, per entity
- Backup, restore, and DR design with RPO and RTO targets (`# ASSUMPTION:` for values)
- SLO definitions and alert rules
- Task list with test plan per task

Do not implement until approved.

# STEP 2: SCOPE

## Security
- Threat-model-driven fixes. Each STRIDE finding has an owner and a test.
- OWASP ASVS Level 2 checklist, with pass or fail per item and evidence.
- Secrets: no secrets in the repo or images. Use a secrets manager interface with rotation support.
- Dependency scanning (SCA) and container scanning in CI. Block on critical findings.
- Audit log tamper evidence: hash-chain each `audit_log` row to the previous row. Provide a verification job.
- Rate limiting and lockout on auth and agent endpoints.
- Security headers, CSP, and CORS restricted to the deployed origins.
- Prepare the pen-test scope document. Do not claim the test has passed until a third party has run it.

## Privacy and data lifecycle
- Retention policy as config per entity, with `# ASSUMPTION:` for periods pending counsel review.
- Erasure workflow for athlete data on verified request: removes personal fields, keeps aggregates with suppression intact, and writes an erasure audit record. Minor erasure requires guardian reference and two-person approval.
- Consent withdrawal: stops new processing, triggers the erasure workflow path, and blocks eligibility and notifications for that athlete.
- Export of an individual's data (access request) with RBAC and audit.
- Verify that no PII appears in logs, traces, error messages, or the agent's audit prompts beyond hashed references. Add a test that scans log output for seeded synthetic PII.

## Resilience and operations
- Backups: encrypted, point-in-time recovery for PostgreSQL, and cross-zone copy. Restore drill script that runs in CI against a fresh environment.
- Migration safety: every Alembic migration runs forward and backward on a copy of seed data. Zero-downtime pattern for additive changes.
- Load test at 40-district scale with a 10x registry, plus a soak test of 4 hours. Report p95 and error rate.
- Chaos tests: kill the outbox relay, the snapshot job, and one API replica during load. Confirm no data loss and no duplicate notifications.
- Runbooks in `docs/runbooks/`: deploy, rollback, restore, key rotation, adapter deactivation, agent disable switch, incident response.
- Feature flags for the agent layer and each state adapter, with a kill switch that NATIONAL_ADMIN can use.

## Accessibility and language
- GIGW and WCAG 2.1 AA audit with automated tooling plus a manual keyboard and screen-reader pass. List every failing item.
- Verify every translated string has `reviewed_by`. Build fails if an unreviewed string ships to a production locale.

## Pilot onboarding tooling
- Bulk import tool for pilot data: CSV or XLSX in, schema validation, quarantine report, dry-run mode, idempotent re-import. Imports write through the service layer, so all rules apply.

# STEP 3: ACCEPTANCE CRITERIA (each must have a test or evidence artefact)
1. Every STRIDE finding marked High has a fix and a regression test
2. Audit hash chain detects a modified or deleted row (tested)
3. Erasure removes personal fields and leaves suppressed aggregates intact (tested)
4. Minor erasure requires two distinct approvers (tested)
5. Consent withdrawal blocks eligibility and notifications for that athlete (tested)
6. Log scan finds zero seeded synthetic PII across API, worker, and agent logs (tested)
7. Restore drill recovers the seed database within the stated RTO, with RPO verified (CI job)
8. Each migration passes forward and backward on seed data (CI)
9. Chaos scenarios produce no data loss and no duplicate notifications (report attached)
10. 40-district load test meets the Phase 2 and Phase 3 latency targets; 4-hour soak shows no memory growth beyond 10%
11. Automated WCAG 2.1 AA scan reports zero critical or serious violations on core flows
12. Bulk import dry-run produces a quarantine report with reasons, and re-import creates no duplicates
13. Agent kill switch disables all agent routes within 60 seconds (tested)
14. CI passes on a clean clone

# STEP 4: DELIVERABLES
1. Approved plan from Step 1
2. Implementation and runbooks
3. Evidence pack in `docs/evidence/`: threat model, ASVS checklist, SCA and container scan results, load and soak reports, chaos report, restore drill log, accessibility report
4. Pen-test scope document (no pass claim)
5. `docs/ASSUMPTIONS.md` and `docs/KNOWN_GAPS.md` updated, with remaining blockers listed first
6. Short summary: pilot readiness verdict (Ready / Ready with conditions / Not ready), blockers, and decisions needed from the ministry and counsel

# WARNINGS TO SURFACE IN THE SUMMARY
- Passing tests do not make the system safe for real data. An independent security assessment and a counsel sign-off on retention, erasure, and consent are required before go-live.
- Do not onboard real minors' data until the erasure path has been exercised end-to-end on synthetic data by someone other than the author.
- Treat the agent kill switch as an operational requirement. Test it in the pilot environment before launch.

# STOP
Wait for review and a pilot go or no-go decision.