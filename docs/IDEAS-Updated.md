# SYSTEM PROMPT: Build "TrackNet" — Post-KID Athlete Tracking & Verification Layer

## 1. ROLE & MISSION

You are a senior full-stack engineer and product architect. Build a production-quality web application called **TrackNet**.

TrackNet is NOT an athlete social network, NOT a new athlete registration system, and NOT a replacement for India's NSRS / Khelo India / Khel Setu platforms. It is a **thin, independently auditable longitudinal tracking and verification utility** that solves one documented failure: after a child receives a Khelo India ID (KID) via KIRTI, nothing follows. No progression data, no parent visibility, no follow-up. The gap is not talent — it is tracking infrastructure and institutional follow-through.

TrackNet's job:
- Record, every quarter, whether a KID-holding athlete is still training, under whom, at what facility, at what competition level.
- Compute **cohort retention** at district + sport + age-band level.
- Give KIC coaches a logging tool that **writes into their existing workflow**, not a new one.
- Give State Sports Directors a **one-page KISCE/KIC conversion scorecard** to defend allocation decisions.
- Track the **sports-quota vacancy gap** (notified vs advertised vs filled) as a public-interest accountability dataset.
- Support **local data stewards** (NGOs, college PE departments, district associations) as DPDP-compliant data fiduciaries — never a single central vendor holding all athlete data.

## 2. HARD CONSTRAINTS — VIOLATING THESE IS A BUILD FAILURE

1. **No duplicate identity collection.** Use NSRS KID as the primary key where it exists. Otherwise create a `provisional_id`. Never collect Aadhaar, passport, or biometric data. Ever.
2. **No parallel funding channel.** TrackNet never disburses money. It routes to and verifies existing instruments (Khelo India scholarships, KIC grants, state cash awards) and reports whether funds reached the athlete.
3. **No smartphone dependency.** Every athlete-facing touchpoint MUST work via SMS and IVR fallback. Assume 2G, feature phones, and intermittent power.
4. **No replacement of state authority.** Every output is addressed to a named role (State Sports Director, KISCE High Performance Manager, District Sports Officer, KIC Coach) as an *option with cost and target*, never a central directive.
5. **No single data owner.** Data stewardship is federated per cluster (district + sport). Design for `steward_org` scoping from day one. The platform is a processor; the steward is the fiduciary.
6. **Read-only on government systems.** Integrate only via public data or statutorily shareable data. No write-back to NSRS in v1.
7. **Reward retention, not "discovery."** No bounty/points system for surfacing athletes — this creates false positives and worsens the documented age-fraud and merit problem.
8. **Offline-tolerant, mobile-first, low-bandwidth.** Works on a ₹6,000 Android phone at 3G. Hindi + English at minimum; architecture must support regional languages.

## 3. USERS & ROLES (RBAC)

| Role | Scope | Primary Job |
|---|---|---|
| `athlete` / `guardian` | Own record | Confirm quarterly training status via SMS/web |
| `kic_coach` | Assigned athletes | Log training sessions in <30 seconds |
| `steward` (NGO / college PE dept / district assoc.) | Cluster | Own consent records, chase non-responders |
| `district_officer` | District | Review retention gaps, act on alerts |
| `state_director` | State | Read conversion scorecard, reallocate |
| `public_viewer` | Aggregate only | View published retention + vacancy dashboards |
| `admin` | Platform | Manage stewards, audit log, never view raw PII |

## 4. CORE DATA MODEL

Design these entities with migrations. All PII fields are field-encrypted at rest and access-logged.

- **Athlete**: `id`, `kid` (nullable, unique), `provisional_id`, `name`, `dob`, `sex`, `sport`, `district_id`, `block_id`, `school_id`, `guardian_phone_hash`, `created_by_role`, `consent_status`, `consent_ref`, `status` (active/dormant/graduated/lost)
- **Coach**: `id`, `name`, `certification_level` (enum: none, NCAB_L0, NCAB_L1, NCAB_L2, PCA), `kic_id` (nullable), `is_uncertified_local` (bool)
- **Facility**: `id`, `type` (school_ground, KIC, KISCE, private_academy, community), `geo`, `condition`, `access_status`, `verified_at`
- **TrainingLog**: `id`, `athlete_id`, `coach_id`, `facility_id`, `session_date`, `duration_min`, `logged_by_role`, `source` (web/sms/ivr), `synced_at`
- **FollowUp**: `id`, `athlete_id`, `quarter`, `channel` (sms/ivr/web), `response`, `attempted_at`, `responded_at`
- **CompetitionRecord**: `id`, `athlete_id`, `level` (block/district/state/national/international), `event_name`, `date`, `result`, `verified_by`
- **FundingEvent**: `id`, `athlete_id`, `instrument` (Khelo India OPA/KIC grant/state award/NSDF), `amount`, `sanctioned_on`, `received_on`, `delay_days` (computed)
- **QuotaVacancy**: `id`, `state`, `department`, `post_group` (A/B/C), `notified_count`, `advertised_count`, `filled_count`, `as_of_date`, `source_url`
- **StewardOrg**: `id`, `name`, `type`, `district_id`, `sports[]`, `data_fiduciary_ref`, `status`
- **AuditLog**: every read/write of PII, immutable, append-only

## 5. MODULES

**M1 — Athlete Ledger.** Lightweight create/search. KID lookup first. Provisional records upgradeable to KID later. Bulk CSV import from KIC paper/Excel logs.

**M2 — Quarterly Follow-Up Engine.** Scheduled SMS/IVR/web prompts to athlete/guardian + coach. Escalation ladder: Day 0 SMS → Day 7 IVR → Day 14 steward call → Day 30 auto-flag `dormant`. Tracks response rate per cluster — this is a first-class KPI.

**M3 — KIC Coach Quick-Log.** Single-screen, <30s session entry. Works offline (IndexedDB queue, background sync). Deliberately mirrors the coach's existing register format so it augments, not replaces.

**M4 — Retention Analytics.** Cohort survival: of 100 athletes assessed at U-14 in district X, how many still training at U-17, U-19, U-23. Slice by district, sport, sex, coach certification level. Aggregate-only for public viewers.

**M5 — State Conversion Scorecard.** One printable page per KISCE/KIC: athletes enrolled, retention rate, coach certification coverage, funding delay, competition progression. Designed for a State Sports Director to bring into a review meeting.

**M6 — Vacancy Accountability Tracker.** Public dashboard: notified vs advertised vs filled sports-quota posts by state and department, with source citations and staleness flags. Read-only, citation-linked, no PII.

## 6. BUILD PHASES — STOP AND WAIT FOR MY REVIEW AFTER EACH

### PHASE 0 — Foundation & Manual-Mode Scaffold (no athlete PII)
Deliver: repo, Next.js + TypeScript + Tailwind + shadcn/ui, Postgres via Prisma, auth with RBAC, `StewardOrg` scoping, migrations for all entities above, seed script, `/health`, audit-log middleware, `.env.example`, README with local setup.
Also build: **CSV import + retention computation engine** that works on a spreadsheet of 200 mock athletes over 12 months, producing a retention brief PDF/HTML. This exists to validate that retention math and reporting are correct *before* any UI depends on them.
**Acceptance:** `pnpm dev` runs; seed creates 2 districts, 3 sports, 500 mock athletes with realistic dropout curve; retention brief generates and matches hand-calculated expectations; all PII fields encrypted; audit log captures reads.
**STOP.**

### PHASE 1 — Athlete Ledger + Steward Console
Deliver: M1 (KID-first create, provisional upgrade path, bulk import, search), steward dashboard (consent capture, non-responder list), guardian consent flow with DPDP-compliant notice text and withdrawal.
**Acceptance:** Import 500-athlete CSV in <60s; search by KID and name; consent withdrawal deletes PII and retains aggregate counts; zero Aadhaar/passport fields anywhere in schema; RBAC blocks cross-cluster access (test cases included).
**STOP.**

### PHASE 2 — Follow-Up Engine + Coach Quick-Log
Deliver: M2 (SMS/IVR adapter with pluggable provider interface + mock adapter; escalation ladder as a scheduled job; response-rate dashboard) and M3 (offline-first single-screen log, IndexedDB queue, conflict resolution, sync status indicator).
**Acceptance:** Simulated quarter run on 500 athletes produces correct escalation transitions; mock SMS adapter logs all outbound; coach can log 10 sessions offline and sync without data loss; log entry takes ≤3 taps from open.
**STOP.**

### PHASE 3 — Retention Analytics + State Scorecard
Deliver: M4 (cohort survival charts, all slices, aggregate-only public view with k-anonymity ≥10) and M5 (printable one-page scorecard, PDF export, "addressed to" role header, per-KISCE/KIC).
**Acceptance:** Retention numbers reconcile with Phase 0 engine exactly; public view suppresses any slice under 10 athletes; scorecard prints on one A4 page; every number has a tooltip stating its source and as-of date.
**STOP.**

### PHASE 4 — Vacancy Tracker + Verification Module
Deliver: M6 (public dashboard, citation-linked, staleness flags, CSV ingest of manually compiled vacancy data) and the **verification module**: generate a signed, verifiable athlete record summary (competition history, training continuity, coach certification) exportable as PDF with a verifiable hash — for use in sports-quota applications. No eligibility adjudication.
**Acceptance:** Vacancy dashboard renders 3 states of mock data with source links and staleness banners; verification PDF hash is reproducible from stored data; module clearly labelled "record summary — not an eligibility certificate."
**STOP.**

## 7. TECH STACK & CONVENTIONS

- **Frontend:** Next.js (App Router), TypeScript strict, Tailwind, shadcn/ui, Recharts for charts
- **Backend:** Next.js route handlers + Prisma; background jobs via a `jobs/` module with a cron-compatible runner (Vercel Cron or a `node-cron` dev runner)
- **DB:** Postgres. All migrations versioned. No raw SQL string interpolation.
- **Auth:** NextAuth (or equivalent) with role + `steward_org_id` in session
- **i18n:** `next-intl`; ship `en` + `hi`; all strings externalised from day one
- **Testing:** Vitest for units, Playwright for the 3 critical flows (import → retention; coach offline log → sync; consent withdrawal)
- **Observability:** structured JSON logs; no PII in logs
- **Deploy:** Vercel-ready; document a self-host path (states may require it)

## 8. UX PRINCIPLES

- Mobile-first. Design for 360px width and 3G.
- Every screen states **what decision it supports** and **who owns that decision**.
- Every number shows its **source and as-of date**.
- No dark patterns on consent. Withdrawal is as easy as granting.
- Coach logging must be faster than the paper register. If it isn't, it will be abandoned — this is the documented failure mode of prior systems.

## 9. NON-GOALS — DO NOT BUILD

- Athlete social feed, messaging, or networking
- Coach/athlete matching marketplace
- AI talent prediction or "next medal prospect" scoring
- New athlete registration replacing NSRS
- Payments, scholarships, or disbursement of any kind
- Gamification, leaderboards, discovery bounties
- Any Aadhaar, biometric, or government ID upload

If a request seems to need any of these, implement the tracking/verification alternative and note the tradeoff in the README.

## 10. HOW TO WORK

- Build **one phase at a time**. At the end of each phase: summarise what was built, list acceptance criteria with pass/fail evidence, list deviations and why, then **stop and wait for my approval**.
- Prefer boring, auditable implementations over clever ones.
- Every module ships with: migration, seed data, tests, and a short `docs/<module>.md` explaining the real-world failure it addresses.
- If a requirement is ambiguous, choose the interpretation that makes the system *easier to audit and harder to misuse*, and flag the choice.
- Never stub security. RBAC, encryption, and audit logging are not phase-2 items.

## 11. DEFINITION OF DONE (per phase)

1. All acceptance criteria demonstrably pass (show commands + output)
2. Tests written and green
3. Docs updated
4. No PII in logs; audit log verified
5. Works at 360px width and with network throttled to Slow 3G in Playwright
6. A 5-line summary a State Sports Director could understand

Begin with **Phase 0 only**. Confirm your understanding of the constraints in §2, propose the file/folder structure, then build.


Here is the screen-by-screen skeleton. Every screen inherits the same **app shell**: top bar (app name · role badge · data scope e.g. "Dist. Pune · Kabaddi" · language toggle EN/हि · help), left nav (role-dependent, 4–6 items max), and a footer strip showing **"Data as of: <date> · Source: <systems>"** — because every number in this product must be traceable.

---

## PHASE 0 — Foundation

**1. Public Landing** — anyone
Blocks: hero with one-line problem statement → "How it works" 3 steps (KID exists → quarterly check-in → retention data) → role entry cards (Athlete/Guardian, Coach, Steward, District Officer, State Director) → footer with data-sources note and DPDP notice link.
No login wall. No athlete data visible.

**2. Sign-In** — all
Blocks: phone/email + OTP or password → role + org scope auto-resolved → redirect to role home. Failed/expired OTP state.

**3. Retention Brief (Phase-0 validation screen)** — internal
Blocks: filter bar (state/district/sport/age band) → headline cohort survival numbers → dropout curve chart → table of district × sport × retention → **Print / Export PDF**.
This is the go/no-go artifact. Works on mock data first.

**4. Health / Status (internal)** — admin
Single block: service status, DB connectivity, last job run, build version.

---

## PHASE 1 — Athlete Ledger + Steward Console

**5. Steward Dashboard (home)** — steward
Blocks: consent pending count (red if >10) → non-responder list (top 10, "chase" action) → cluster summary (athletes tracked, % with KID, % responded this quarter) → quick links to Import, Athlete List, Consent Queue.

**6. Athlete List & Search** — steward, district officer
Blocks: search bar (by KID / name / phone-hash) → filters (sport, age band, status: active/dormant/graduated/lost, KID yes/no) → results table (ID, name, age, sport, KID?, coach, last log, status) → row → Athlete Profile.
Bulk select for export.

**7. Athlete Create (KID-first wizard)** — steward, coach
Block 1: **KID lookup first** — "Do you have a Khelo India ID?" → if yes, fetch and prefill.
Block 2: provisional details (name, DOB, sex, sport, district/block, school, guardian phone) — **no Aadhaar, no ID upload**.
Block 3: consent → creates record with `provisional_id`, flags "upgradeable to KID."

**8. Athlete Profile** — steward, coach, district officer (role-scoped)
Blocks: header (name, age, sport, status chip, KID/provisional badge) → tabs:
· **Training** — session log table + continuity sparkline
· **Competition** — level reached per year
· **Funding** — instrument, sanctioned, received, delay days
· **Consent** — status, ref, granted/withdrawn date
· **Audit** — who viewed/edited
Actions per role: log session, edit, withdraw consent, export record summary.

**9. Bulk CSV Import** — steward
Blocks: upload → column mapper (required: name, dob, sport, district; optional: KID, coach) → validation report (rows OK / errors / duplicates by KID) → confirm → import summary.
Shows a downloadable error file.

**10. Consent Capture & Notice** — steward (with guardian present)
Blocks: plain-language notice (what's collected, why, who sees it, withdrawal right, retention period) → language toggle → guardian phone OTP verify → consent record created → printable receipt.
Withdrawal path is equally prominent.

**11. Consent Withdrawal (public, no login)** — guardian/athlete
Blocks: enter phone → OTP → list of records under that phone → "Withdraw all / Withdraw selected" → confirmation showing **what is deleted (PII) and what is retained (aggregate counts only)**.

**12. Non-Responder Worklist** — steward, district officer
Blocks: filter (quarter, block, sport) → table (athlete, last response, attempts, last channel) → per-row "call/chase" with a scripted prompt → bulk assign to steward.

---

## PHASE 2 — Follow-Up Engine + Coach Quick-Log

**13. Coach Home (mobile)** — KIC coach
Blocks: today's session count → "Log a session" big button → my athletes (last logged, sync status dot) → offline banner when no network.
Designed for 360px, one-handed.

**14. Quick-Log Session (single screen)** — coach
Blocks, all on one screen, ≤3 taps: athlete picker (recent-first) → facility (default = last used) → duration chips (30/45/60/90) → **Save**.
Offline: saves to IndexedDB, shows "queued" badge. No optional fields on the primary path.

**15. Sync Status / Offline Queue** — coach
Blocks: queued items list (athlete, time, state) → retry / discard → last successful sync timestamp → conflict notice if a server record changed.

**16. Follow-Up Campaign Dashboard** — district officer
Blocks: quarter selector → funnel (sent → delivered → responded → escalated → dormant) → response rate by block/sport → **"Run quarter"** action (confirmation modal showing recipients) → per-channel breakdown (SMS/IVR/Web).

**17. Escalation Ladder Config / Run Detail** — district officer, admin
Blocks: ladder visual (Day 0 SMS → Day 7 IVR → Day 14 steward call → Day 30 dormant) → edit timing/thresholds → per-run detail table (athlete, current rung, next action date) → job run history with logs.

---

## PHASE 3 — Retention Analytics + State Scorecard

**18. Retention Analytics** — district officer, state director
Blocks: filter bar (state/district/sport/sex/age band/coach certification) → KPI row (tracked, retained %, dormant %, graduated %) → cohort survival chart (U-14→U-17→U-19→U-23) → dropout heatmap (district × sport) → export.

**19. Cohort Drilldown** — district officer, state director
Blocks: cohort header ("U-14 Kabaddi, Pune, 2024 intake: 240") → survival waterfall (240 → 160 → 95 → 60) with counts at each transition → table of athletes in the cohort (scoped) → **"why they left"** tag summary (no coach / no facility / no competition / moved / unknown).

**20. Public Aggregate Retention View** — public, no login
Blocks: state/district selector → aggregate charts only → **k-anonymity rule: any slice with <10 athletes is suppressed with "insufficient data"** → methodology note → data-as-of stamp.

**21. State Conversion Scorecard (printable)** — state director
One A4 page per KISCE/KIC:
Blocks: institution header + "Addressed to: <role>" → 5 numbers (enrolled, retention %, coach certification coverage, funding delay days, competition progression count) → one-line interpretation per number → "Suggested action" box → QR/hash footer for authenticity.
Print CSS is a first-class deliverable.

---

## PHASE 4 — Vacancy Tracker + Verification

**22. Vacancy Tracker (public dashboard)** — public
Blocks: filter (state, department, post group A/B/C) → **notified vs advertised vs filled** bar comparison per state → gap table with **source URL + as-of date + staleness flag** per row → export CSV.
Every row cites its source. No athlete data anywhere on this screen.

**23. Vacancy Data Ingest** — admin
Blocks: CSV upload (state, department, group, notified, advertised, filled, source URL, as-of date) → validation (source URL required, date required) → preview diff vs current → publish.
Records who published and when.

**24. Verification Record Summary** — athlete/steward generates, third party verifies
Blocks: athlete header → competition history table → training continuity summary → coach certification at each stage → funding received summary → **"Record summary — not an eligibility certificate"** banner → Export PDF with embedded hash.
No adjudication, no eligibility verdict.

**25. Verification Hash Check (public)** — third party
Single block: enter or scan hash → shows matching record summary metadata (name masked, sport, district, issue date) → "matches / does not match" result.

---

## CROSS-CUTTING / ADMIN

**26. Audit Log Viewer** — admin
Blocks: filter (actor, role, entity type, action, date) → immutable table → no PII values shown, only field names and record IDs → export.

**27. Steward Org & User Management** — admin
Blocks: org list (name, type, district, sports, status) → add/edit org → assign users to org + role → deactivate.

**28. Settings** — all roles (scoped)
Blocks: language preference → notification channel preference (SMS/IVR/web) → phone number → session/security info.

---

### Notes before you proceed

- Screens **5, 13, 14, and 21** carry the whole product. If those four are wrong, nothing else matters. Review them first after each phase ships.
- Screens **20 and 22** are the only public-facing ones and therefore the only ones that can create political pressure — treat their data-suppression and citation rules as non-negotiable.
- Screen **3** is your Phase-0 gate: if the retention brief doesn't hold up in a conversation with a real District Sports Officer, stop before Phase 1.



# TrackNet — Text View Look & Feel

## 0. Visual language (applies to every screen)

```
PALETTE
  bg          #F7F8FA   page
  surface     #FFFFFF   cards, 1px #E3E6EB border, 8px radius
  ink         #12151A   primary text
  ink-2       #5A6270   secondary
  ink-3       #8A929E   captions, "as of" stamps
  navy        #1F3A5F   brand, nav active
  saffron     #E07B24   primary action (Log, Run, Export)
  green       #2E7D5B   positive / active
  amber       #B26A00   warning / dormant
  red         #B3261E   alert / lost
  grey        #6B7280   graduated / archived

TYPE  Inter · tabular numerals for all counts
  H1  24/32 600    page title
  H2  18/24 600    card title
  BODY 14/20 400
  CAP 12/16 500    captions, chips, "as of"

SPACING 4-base · card padding 20 · gutter 24 · max content width 1280

CHIPS  rounded-full, 6px v-pad, 10px h-pad, 12px 600, tinted bg + solid text
  ● active   green      ● dormant  amber     ● lost  red
  ● graduated grey      ● provisional  outline-only, dashed border
  ● KID       navy tint

EVERY SCREEN ENDS WITH:
  ── Data as of 31 Mar 2026 · Source: NSRS, KIRTI, KIC logs ──  (caption, ink-3)
```

---

## App shell

```
┌────────────────────────────────────────────────────────────────────────────┐
│  TRACKNET      ● Steward · Dist. Pune · Kabaddi            EN | हि   ⓘ  ◐  │
├──────────────┬─────────────────────────────────────────────────────────────┤
│  ▸ Dashboard │                                                             │
│    Athletes  │                     (screen content)                        │
│    Import    │                                                             │
│    Consent   │                                                             │
│    Worklist  │                                                             │
│              │                                                             │
│  ──────────  │                                                             │
│  Help        │                                                             │
│  Sign out    │                                                             │
└──────────────┴─────────────────────────────────────────────────────────────┘
```
Nav = 220px fixed, white, active item navy 3px left bar. Top bar 56px, white, 1px bottom border. Collapses to a bottom tab bar (5 icons) under 768px.

---

## PHASE 0

### 1. Public Landing — no login

```
┌────────────────────────────────────────────────────────────────────────────┐
│  TRACKNET                                            EN | हि     Sign in → │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│    After a child gets a Khelo India ID, nothing follows.                   │
│    TrackNet is the follow-up.                                              │
│                                                                            │
│    ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐          │
│    │ 1  KID exists    │ │ 2  Quarterly     │ │ 3  Retention     │          │
│    │                  │ │    check-in      │ │    data          │          │
│    │    NSRS / KIRTI  │ │    SMS · IVR ·   │ │    district ×    │          │
│    │    issues it     │ │    web, 30 sec   │ │    sport × age   │          │
│    └──────────────────┘ └──────────────────┘ └──────────────────┘          │
│                                                                            │
│    I am a —                                                                │
│    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                  │
│    │Athlete │ │ Coach  │ │Steward │ │District│ │ State  │                  │
│    │Guardian│ │        │ │  NGO   │ │Officer │ │Director│                  │
│    └────────┘ └────────┘ └────────┘ └────────┘ └────────┘                  │
│                                                                            │
│    Public dashboards:  Retention →    Vacancy tracker →                    │
│  ── We do not collect Aadhaar. Consent notice · Withdraw consent ──        │
└────────────────────────────────────────────────────────────────────────────┘
```
Hero on `bg`, headline navy 32/40. Three step cards flat, no shadow. Role cards = outlined buttons, hover navy border.

### 2. Sign-In

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              TRACKNET                                      │
│                                                                            │
│                    ┌────────────────────────────────┐                      │
│                    │  Sign in                       │                      │
│                    │                                │                      │
│                    │  Phone number                  │                      │
│                    │  ┌──────────────────────────┐  │                      │
│                    │  │ +91  ______________      │  │                      │
│                    │  └──────────────────────────┘  │                      │
│                    │  [ Send OTP ]  saffron          │                      │
│                    │                                │                      │
│                    │  OTP                           │                      │
│                    │  ┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐      │                      │
│                    │  └──┘└──┘└──┘└──┘└──┘└──┘      │                      │
│                    │  Resend in 0:24                │                      │
│                    └────────────────────────────────┘                      │
│  ── Your role and district are resolved from your account ──               │
└────────────────────────────────────────────────────────────────────────────┘
```
Centred 400px card on `bg`. OTP boxes 44px, focus = navy 2px ring. Error state: red text under field, card border red.

### 3. Retention Brief — Phase-0 gate

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Retention Brief                              [ Print / Export PDF ] saffron│
├────────────────────────────────────────────────────────────────────────────┤
│ State ▾ Maharashtra   District ▾ Pune   Sport ▾ Kabaddi   Age ▾ U-14  [Go] │
├────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐               │
│  │ TRACKED    │ │ RETAINED   │ │ DORMANT    │ │ LOST       │               │
│  │   1,240    │ │    58%     │ │    27%     │ │    15%     │               │
│  │            │ │  green     │ │  amber     │ │  red       │               │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘               │
├────────────────────────────────────────────────────────────────────────────┤
│  Cohort survival                                                           │
│  100% ┤■■■■■■■■■■■■■■■■■■                                                  │
│   75% ┤■■■■■■■■■■■■■■■■■■■■■■■■■■                                          │
│   50% ┤■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■                                   │
│   25% ┤■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■                               │
│    0% └─────────────────────────────────────────────────────               │
│        U-14        U-17        U-19        U-23                            │
├────────────────────────────────────────────────────────────────────────────┤
│  District × Sport        Intake   Retained   Rate    Worst transition      │
│  Pune · Kabaddi           240       139      58%     U-17 → U-19           │
│  Pune · Athletics         410       205      50%     U-14 → U-17  ◀ alert   │
│  Satara · Kabaddi         190       131      69%     —                      │
│  Satara · Athletics       400       188      47%     U-19 → U-23  ◀ alert   │
├────────────────────────────────────────────────────────────────────────────┤
│ ── Data as of 31 Mar 2026 · Source: NSRS, KIRTI · Mock data in Phase 0 ──  │
└────────────────────────────────────────────────────────────────────────────┘
```
KPI cards: 4-up, number 28/36 600, label caption above in ink-3. Bars navy, fading to lighter navy per step. `◀ alert` = red caption inline. Table zebra `#FBFCFD`, row hover `#F3F6FA`.

### 4. Health / Status — admin

```
┌────────────────────────────────────────────────────────────────────────────┐
│ System status                                     ● All operational green  │
├────────────────────────────────────────────────────────────────────────────┤
│  Service          API            ● up      p95 180ms                       │
│  Database         Postgres       ● up      14 conns                        │
│  Jobs             follow-up       ● idle   last run 02:00, 0 failed        │
│  Build            1.0.0-phase0   ·  deployed 31 Mar 2026 09:12             │
│  ── Internal screen · no athlete data ──                                   │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 1

### 5. Steward Dashboard — home

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Good morning, Meera                                  ● Dist. Pune · Kabaddi│
├────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐         │
│  │ CONSENT PENDING   │ │ NON-RESPONDERS    │ │ RESPONSE THIS QTR │         │
│  │       7  amber    │ │      23  red      │ │      71%  green   │         │
│  │  → Consent queue  │ │  → Worklist       │ │   target 70% ✓    │         │
│  └───────────────────┘ └───────────────────┘ └───────────────────┘         │
├────────────────────────────────────────────────────────────────────────────┤
│  My cluster                                                                │
│  Athletes tracked       1,240      With KID        982  (79%)              │
│  Training logged (30d)    844      Provisional     258  (21%)              │
│  Facilities verified       31      Coaches          46  (12 uncertified)   │
├────────────────────────────────────────────────────────────────────────────┤
│  Chase these first (longest silent)                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Rohan P.   · 14 · Kabaddi · KID 4821 · last log 96d  [ Call ] [SMS]  │  │
│  │ Sneha K.   · 13 · Kabaddi · KID 5107 · last log 88d  [ Call ] [SMS]  │  │
│  │ Imran S.   · 15 · Kabaddi · prov.   · last log 74d   [ Call ] [SMS]  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────────────────────┤
│  Quick:  [ Import CSV ]  [ Athlete list ]  [ Consent queue ]              │
│ ── Data as of 31 Mar 2026 · Source: NSRS, KIC logs ──                      │
└────────────────────────────────────────────────────────────────────────────┘
```
KPI cards with coloured left 3px bar. Red card only if threshold breached — otherwise grey. Chase rows are tappable rows, action buttons ghost-style.

### 6. Athlete List & Search

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Athletes (1,240)                                    [ + Add athlete ] saff │
├────────────────────────────────────────────────────────────────────────────┤
│ 🔍 KID, name or phone-hash                                                 │
│ Sport ▾  Age ▾  Status ▾  KID ▾                        [ Export CSV ]       │
├────────────────────────────────────────────────────────────────────────────┤
│ ☐  NAME          AGE  SPORT     KID      COACH        LAST LOG   STATUS     │
│ ─────────────────────────────────────────────────────────────────────────  │
│ ☐  Rohan Patil    14  Kabaddi   4821     S. Deshmukh   96d  ●  ● active    │
│ ☐  Sneha Kulkarni 13  Kabaddi   5107     S. Deshmukh   88d  ●  ● dormant   │
│ ☐  Imran Shaikh   15  Kabaddi   ┈prov┈   uncertified   74d  ●  ● dormant   │
│ ☐  Anjali More    12  Kabaddi   5240     P. Jadhav     3d   ●  ● active    │
│ ☐  Vikram Rao     19  Kabaddi   3301     —            210d  ●  ● lost      │
│                                                                            │
│                                          1–25 of 1,240   ‹ 1 2 3 … ›       │
├────────────────────────────────────────────────────────────────────────────┤
│ 2 selected:  [ Export ]  [ Assign to steward ]                             │
│ ── Data as of 31 Mar 2026 · Source: NSRS, KIC logs ──                      │
└────────────────────────────────────────────────────────────────────────────┘
```
Sticky header row, 12px caps labels ink-3. `┈prov┈` dashed outline chip = provisional. Last-log cell turns amber >60d, red >120d. Bulk bar slides up from bottom when ≥1 selected.

### 7. Athlete Create — KID-first wizard

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Add athlete                          ① KID lookup ─ ② Details ─ ③ Consent │
├────────────────────────────────────────────────────────────────────────────┤
│  STEP 1 · Do they already have a Khelo India ID?                           │
│                                                                            │
│    ┌──────────────────────────────────┐   ┌──────────────────────────┐     │
│    │  KID  4 8 2 1                    │   │  [ Look up ]  navy       │     │
│    └──────────────────────────────────┘   └──────────────────────────┘     │
│                                                                            │
│    ● Found — Rohan Patil, 14, Kabaddi, Pune   (prefilled on next step)     │
│      ── or ──                                                              │
│    ○ No KID yet → create a provisional record (upgradeable later)          │
│                                                                            │
│                                   [ Continue → ]                           │
│  ── We never collect Aadhaar, passport or biometric data ──                │
└────────────────────────────────────────────────────────────────────────────┘
```
Stepper as thin 3-segment bar, current navy, done green with ✓. Found-state line green with a filled dot; provisional path amber.

```
│  STEP 2 · Details                                    (KID 4821 · locked)    │
│                                                                            │
│  Name *            ┌──────────────────────────────┐                        │
│                    │ Rohan Patil                  │  read-only if KID      │
│  Date of birth *   ┌────┐┌────┐┌────────┐          │                        │
│                    │ 12 ││ 05 ││ 2011   │          │                        │
│  Sex *             ( ) Female   (•) Male   ( ) Other                       │
│  Sport *           ┌──────────────────────────────┐                        │
│                    │ Kabaddi                    ▾ │                        │
│  District *  Pune ▾   Block * Haveli ▾   School  ▾                         │
│  Guardian phone *  ┌──────────────────────────────┐  [ Send verify OTP ]    │
│                    │ +91 98765 43210              │                        │
│                                   [ Continue → ]                           │
```
Required fields marked `*` red. Locked fields grey background with a small 🔒 and caption "from NSRS".

### 8. Athlete Profile

```
┌────────────────────────────────────────────────────────────────────────────┐
│ ← Athletes                                                                 │
│  Rohan Patil   · 14 · Kabaddi        ● active    KID 4821                  │
│  Dist. Pune · Haveli · ZP School Wadgaon      [ Log session ] [ ⋯ ]        │
├────────────────────────────────────────────────────────────────────────────┤
│  Training │ Competition │ Funding │ Consent │ Audit                        │
│  ━━━━━━━━                                                                  │
├────────────────────────────────────────────────────────────────────────────┤
│  TRAINING CONTINUITY                                    avg 3.1 / week     │
│                                                                            │
│  6 ┤        ▁▂▃▂▄▃▂▁▃▄▅▄▃▂▁▂▃▄▃▂▁▃▂▄▃▂▁▂▃▄▃▂▁                              │
│  0 └──────────────────────────────────────────────────────                  │
│     Apr        Jul        Oct        Jan        Mar                        │
├────────────────────────────────────────────────────────────────────────────┤
│  Recent sessions                                                           │
│  28 Mar  · 60 min · KIC Haveli        · S. Deshmukh  · L0   · web          │
│  26 Mar  · 45 min · ZP School ground  · uncertified  · ⚠     · sms          │
│  24 Mar  · 90 min · KIC Haveli        · S. Deshmukh  · L0   · web          │
│  ── Data as of 31 Mar 2026 · Source: KIC logs ──                           │
└────────────────────────────────────────────────────────────────────────────┘
```
Header card 1px border, name H1. Tabs = underline style, navy 2px. Uncertified coach row gets amber ⚠ chip. Sparkline navy; gaps render as breaks, not zeros.

Funding tab: `Khelo India OPA · ₹10,000/mo · sanctioned 12 Jan · received 26 Feb · delay 45d ⚠`
Consent tab: green `Granted 12 Jan 2026 · ref C-8821` + prominent `Withdraw consent` red-outline button.
Audit tab: table of `who · role · action · field · when`, no values shown.

### 9. Bulk CSV Import

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Import athletes                              Step 2 of 4 · Map columns     │
├────────────────────────────────────────────────────────────────────────────┤
│  Your column          →   TrackNet field         Sample                     │
│  ┌──────────────────┐     ┌──────────────────┐   ┌────────────────────┐     │
│  │ Child Name       │  →  │ Name *          ▾│   │ Rohan Patil        │     │
│  │ DOB              │  →  │ Date of birth * ▾│   │ 12/05/2011         │     │
│  │ Game             │  →  │ Sport *         ▾│   │ Kabaddi            │     │
│  │ Khelo ID         │  →  │ KID (optional)  ▾│   │ 4821               │     │
│  │ — not mapped —   │  →  │ (ignore)        ▾│   │                    │     │
│  └──────────────────┘     └──────────────────┘   └────────────────────┘     │
├────────────────────────────────────────────────────────────────────────────┤
│  Validation                                                                │
│  ● 486 rows valid                                                          │
│  ●  11 rows missing date of birth        [ Download error file ]           │
│  ●   3 rows duplicate KID (4821, 5107, 5240)                               │
│                                            [ Back ]   [ Import 486 rows ]  │
└────────────────────────────────────────────────────────────────────────────┘
```
Validation rows: green dot = pass, amber = warn (importable), red = blocked. Import button disabled if any red-blocking category unchecked.

### 10. Consent Capture & Notice

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Consent                                        Guardian present? ● Yes     │
├────────────────────────────────────────────────────────────────────────────┤
│  हिंदी में पढ़ें  ←→  Read in English                                       │
│                                                                            │
│  WHAT WE COLLECT        name, age, sport, school, guardian phone           │
│  WHAT WE DO NOT         Aadhaar, passport, photos, biometrics, bank        │
│  WHY                    to track training every quarter and report         │
│                         district retention to the sports department        │
│  WHO SEES IT            your cluster steward, your KIC coach, the          │
│                         district officer. Not the public.                  │
│  HOW LONG               3 years after last activity, then deleted          │
│  YOUR RIGHTS            see it, correct it, withdraw any time — no reason  │
│                         needed, and withdrawal is as easy as this         │
├────────────────────────────────────────────────────────────────────────────┤
│  Verify guardian phone   +91 98765 43210    [ Send OTP ]                   │
│  OTP  ┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐        ☐ Guardian has read the notice      │
│                                          [ Record consent ] saffron        │
│  ── A printed receipt will be generated · ref C-8821 ──                    │
└────────────────────────────────────────────────────────────────────────────┘
```
Notice block is the visual centre — plain 15/24 body, label column 180px bold caps. No pre-ticked boxes. Withdraw link appears at bottom in equal weight.

### 11. Consent Withdrawal — public

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Withdraw consent                                        no login needed     │
├────────────────────────────────────────────────────────────────────────────┤
│  Guardian phone  +91 ______________      [ Send OTP ]                      │
│  OTP             ┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐      [ Verify ]                  │
├────────────────────────────────────────────────────────────────────────────┤
│  Records under this phone                                                  │
│  ☑  Rohan Patil   · 14 · Kabaddi · KID 4821                                │
│  ☐  Sneha Patil   · 11 · Kabaddi · provisional                             │
│                                            [ Withdraw selected ] red       │
├────────────────────────────────────────────────────────────────────────────┤
│  ⚠ What happens next                                                       │
│    Deleted        name, DOB, phone, school, coach links, session detail    │
│    Kept           anonymous counts only — "1 athlete, Pune, Kabaddi, U-14" │
│    Time            immediate, irreversible, receipt sent by SMS            │
└────────────────────────────────────────────────────────────────────────────┘
```
Red 3px top border on the warning card. Destructive button is outline-red, not filled.

### 12. Non-Responder Worklist

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Non-responders (23)                    Quarter ▾ Q4 · Block ▾ · Sport ▾    │
├────────────────────────────────────────────────────────────────────────────┤
│ ATHLETE            BLOCK    LAST RESPONSE  ATTEMPTS  LAST CH   ACTION      │
│ Rohan Patil        Haveli   96d            4         SMS       [Call][SMS]  │
│ Sneha Kulkarni     Haveli   88d            3         IVR       [Call][SMS]  │
│ Imran Shaikh       Mulshi   74d            2         SMS       [Call][SMS]  │
├────────────────────────────────────────────────────────────────────────────┤
│ Call script  ───────────────────────────────────────────────────────────── │
│  "Namaste, main TrackNet se. Rohan abhi Kabaddi practice kar rahe hain?    │
│   Kaun coach ke paas? Kaunsi jagah?"                                       │
│  Log outcome:  ( ) Training  ( ) Stopped  ( ) Moved  ( ) Unknown           │
└────────────────────────────────────────────────────────────────────────────┘
```
Script card is a fixed side panel (360px) on desktop, bottom sheet on mobile. Outcome radios required before the row can be closed.

---

## PHASE 2

### 13. Coach Home — mobile, 360px

```
┌──────────────────────────────┐
│ ☰  TrackNet      ● S. Deshmukh│
│    KIC Haveli · Kabaddi      │
├──────────────────────────────┤
│  TODAY                       │
│  ┌────────────────────────┐  │
│  │    + LOG A SESSION     │  │
│  │        saffron         │  │
│  └────────────────────────┘  │
│                              │
│  My athletes (28)            │
│  ● Rohan Patil     2d   ✓syn │
│  ● Sneha Kulkarni  9d   ⏳q  │
│  ● Anjali More     3d   ✓syn │
│  ● Imran Shaikh    —    ✓syn │
│  …                           │
├──────────────────────────────┤
│  ⚠ Offline — 2 sessions      │
│    queued, will sync later   │
├──────────────────────────────┤
│  ⌂Home  👥Athletes  ⟳Sync  ⚙ │
└──────────────────────────────┘
```
Log button 56px tall, full width, saffron, 16/600. Sync dot: green ✓syn, amber ⏳ queued, red ! failed. Offline banner amber, sticky above tab bar.

### 14. Quick-Log Session — single screen, ≤3 taps

```
┌──────────────────────────────┐
│ ←  Log session          ✕    │
├──────────────────────────────┤
│ 1  WHO                       │
│  ┌────────┐┌────────┐┌──────┐│
│  │ Rohan  ││ Sneha  ││Anjali││
│  └────────┘└────────┘└──────┘│
│  recent first · search 🔍     │
├──────────────────────────────┤
│ 2  WHERE            (default)│
│  KIC Haveli            ▾     │
├──────────────────────────────┤
│ 3  HOW LONG                  │
│  ┌────┐┌────┐┌────┐┌────┐    │
│  │30m ││45m ││60m ││90m │    │
│  └────┘└────┘└────┘└────┘    │
├──────────────────────────────┤
│  ┌────────────────────────┐  │
│  │        SAVE            │  │
│  └────────────────────────┘  │
└──────────────────────────────┘
```
Selected chip = navy fill, white text. Athlete chips scroll horizontally, 44px min height. No optional fields on this path. Save immediately returns to home with a 2s green toast "Saved · Rohan, 60m".

### 15. Sync Status / Offline Queue

```
┌──────────────────────────────┐
│ ←  Sync                      │
├──────────────────────────────┤
│ Last successful sync         │
│ 31 Mar 2026, 09:41  green    │
├──────────────────────────────┤
│ Queued (2)                   │
│ ┌──────────────────────────┐ │
│ │ Rohan · 60m · 10:12      │ │
│ │ ⏳ waiting    [ Retry ]  │ │
│ ├──────────────────────────┤ │
│ │ Anjali · 45m · 10:40     │ │
│ │ ⚠ conflict — server has  │ │
│ │   a newer entry          │ │
│ │ [ Keep both ] [ Replace ]│ │
│ └──────────────────────────┘ │
├──────────────────────────────┤
│        [ Sync all now ]      │
└──────────────────────────────┘
```
Conflict card amber left bar, both resolutions spelled out in plain words.

### 16. Follow-Up Campaign Dashboard

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Follow-up · Q4 2026                  [ Run quarter ] saffron   Quarter ▾   │
├────────────────────────────────────────────────────────────────────────────┤
│  FUNNEL                                                                    │
│   Sent         ████████████████████████████████████████  1,240            │
│   Delivered    ███████████████████████████████████       1,178  95%       │
│   Responded    ███████████████████████████               884   71% green   │
│   Escalated    ███████████                               341   27% amber   │
│   Dormant      ██████                                    194   15% red     │
├────────────────────────────────────────────────────────────────────────────┤
│  By block        Response %      By channel      Share                     │
│  Haveli            76%  ●         SMS             62%                      │
│  Mulshi            68%  ●         IVR             31%                      │
│  Shirur            54%  ● alert   Web              7%                      │
├────────────────────────────────────────────────────────────────────────────┤
│ ── Data as of 31 Mar 2026 · Source: TrackNet follow-up engine ──           │
└────────────────────────────────────────────────────────────────────────────┘
```
Funnel bars navy, colour shifts only on the outcome rows. `● alert` red caption when below 60%.

### 17. Escalation Ladder Config / Run Detail

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Escalation ladder                          Edit timings  [ Save ] disabled│
├────────────────────────────────────────────────────────────────────────────┤
│   ●──────────●──────────●──────────●──────────●                            │
│  Day 0      Day 7      Day 14     Day 21     Day 30                        │
│  SMS        IVR        Steward    2nd call   → dormant                     │
│                        call                                                │
├────────────────────────────────────────────────────────────────────────────┤
│  Current run · 1,240 athletes                                              │
│  ATHLETE          RUNG      NEXT ACTION      WHEN                          │
│  Rohan Patil      Day 14    steward call     2 Apr                         │
│  Sneha Kulkarni   Day 30    mark dormant     1 Apr  ◀ due today            │
│  Imran Shaikh     Day 7     IVR              4 Apr                         │
├────────────────────────────────────────────────────────────────────────────┤
│  Job history                                                               │
│  31 Mar 02:00  ✓ 1,240 processed · 0 failed · 4m12s                        │
│  30 Mar 02:00  ✓ 1,240 processed · 2 failed · 4m40s   [ view log ]         │
└────────────────────────────────────────────────────────────────────────────┘
```
Ladder is a horizontal stepper; editable nodes open an inline number input. "Due today" rows highlighted `#FFF8EC`.

---

## PHASE 3

### 18. Retention Analytics

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Retention analytics                    State ▾ Dist ▾ Sport ▾ Sex ▾ Age ▾  │
├────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                       │
│  │ TRACKED  │ │ RETAINED │ │ DORMANT  │ │GRADUATED │                       │
│  │  12,480  │ │   58%    │ │   27%    │ │    4%    │                       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘                       │
├────────────────────────────────────────────────────────────────────────────┤
│  COHORT SURVIVAL                                                           │
│   ████████████████████████████████  U-14  12,480                           │
│   █████████████████████             U-17   6,240   50% drop               │
│   ████████████                      U-19   3,120   50% drop               │
│   ██████                            U-23   1,180   62% drop               │
├────────────────────────────────────────────────────────────────────────────┤
│  DROPOUT HEATMAP · district × sport          low ░░ ▒▒ ▓▓ ██ high        │
│              Kabaddi  Athletics  Wrestling  Hockey                         │
│  Pune          ▒▒        ██         ░░        ▓▓                          │
│  Satara        ░░        ██         ▒▒        ▓▓                          │
│  Kolhapur      ▓▓        ▒▒         ░░        ██                          │
├────────────────────────────────────────────────────────────────────────────┤
│ ── Data as of 31 Mar 2026 · Source: NSRS, KIC logs, competition records ── │
└────────────────────────────────────────────────────────────────────────────┘
```
Heatmap cells 64×40, rounded 4px, value caption on hover. Bars use one navy ramp — never rainbow.

### 19. Cohort Drilldown

```
┌────────────────────────────────────────────────────────────────────────────┐
│ ← Analytics                                                                │
│  U-14 Kabaddi · Pune · 2024 intake                  240 athletes           │
├────────────────────────────────────────────────────────────────────────────┤
│  SURVIVAL WATERFALL                                                        │
│   U-14  ████████████████████████████████████  240                          │
│   U-17  ███████████████████████                160   −80  ▓ no coach 41    │
│   U-19  ██████████████                          95   −65  ▓ no comp  33    │
│   U-23  █████████                                60  −35  ▓ moved    22    │
├────────────────────────────────────────────────────────────────────────────┤
│  Why they left (tagged at follow-up)                                       │
│   No coach nearby          41   34%                                        │
│   No competition pipeline  33   27%                                        │
│   Family moved             22   18%                                        │
│   No facility              14   12%                                        │
│   Unknown / no response    11    9%                                        │
├────────────────────────────────────────────────────────────────────────────┤
│  Cohort athletes (60 still active)              [ Export ]                │
│  Rohan Patil · active · S. Deshmukh · L0                                   │
│  …                                                                         │
└────────────────────────────────────────────────────────────────────────────┘
```
Tag bars horizontal, one colour, percentage right-aligned tabular.

### 20. Public Aggregate Retention View

```
┌────────────────────────────────────────────────────────────────────────────┐
│  TRACKNET · Public data                          EN | हि    Method →       │
├────────────────────────────────────────────────────────────────────────────┤
│  State ▾ Maharashtra     District ▾ Pune     Sport ▾ All                   │
├────────────────────────────────────────────────────────────────────────────┤
│  Retention by sport                          (aggregate only)              │
│   Kabaddi    ████████████████████        58%                               │
│   Athletics  █████████████████           50%                               │
│   Wrestling  ████████████████            47%                               │
│   Hockey     ░░░░░░░░░░░░░░░░░░░░░░░     insufficient data                 │
├────────────────────────────────────────────────────────────────────────────┤
│  ⓘ Any group smaller than 10 athletes is hidden to protect identity.       │
│    No individual athlete is identifiable on this page.                     │
│ ── Data as of 31 Mar 2026 · Source: NSRS, KIC logs · Methodology → ──      │
└────────────────────────────────────────────────────────────────────────────┘
```
Suppressed bars render as a dashed grey track with caption. This screen uses a wider 960px column, generous whitespace — it is the only screen designed for a journalist to screenshot.

### 21. State Conversion Scorecard — printable A4

```
┌────────────────────────────────────────────────────────────────────────────┐
│  KHELO INDIA CENTRE · HAVELI, PUNE                        Q4 2026          │
│  Addressed to: District Sports Officer, Pune                               │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│   120          58%          42%          45 days        11                 │
│   ENROLLED     RETENTION    COACH        FUNDING        COMPETITION        │
│                            CERTIFIED     DELAY          PROGRESSIONS       │
│                                                                            │
│  ─────────────────────────────────────────────────────────────────────     │
│  RETENTION 58%    Above district average (52%). No action indicated.       │
│  COACH CERT  42%  Below 60% threshold. 6 of 14 coaches uncertified.        │
│  FUNDING 45d ⚠    Above 30-day norm. 9 athletes awaiting OPA.              │
│  PROGRESS 11      Low for 120 athletes. No U-17 entrants this quarter.     │
│  ─────────────────────────────────────────────────────────────────────     │
│  SUGGESTED ACTION                                                          │
│   1. Route 6 uncertified coaches to NCAB Level 0 (funded under KIC grant). │
│   2. Escalate 9 pending OPA sanctions to State Sports Directorate.         │
│   3. Schedule one U-17 selection trial before 30 Jun.                      │
│                                                                            │
│  ── Generated 31 Mar 2026 · verify at tracknet.in/v/8f3a2c ──   [QR]       │
└────────────────────────────────────────────────────────────────────────────┘
```
Print CSS: A4 portrait, 20mm margins, black text on white, all colour stripped except amber ⚠. The five numbers are 32/40 600 — this is the only screen where numbers are the hero. Every number carries a one-line plain-language interpretation beneath.

---

## PHASE 4

### 22. Vacancy Tracker — public

```
┌────────────────────────────────────────────────────────────────────────────┐
│  TRACKNET · Sports quota vacancies               EN | हि    Method →       │
├────────────────────────────────────────────────────────────────────────────┤
│  State ▾ All     Department ▾ All     Group ▾ A B C                        │
├────────────────────────────────────────────────────────────────────────────┤
│  NOTIFIED vs ADVERTISED vs FILLED                                          │
│                                                                            │
│  Haryana      N ████████████████ 1,057                                    │
│               A ██████             447                                    │
│               F █████              447   ▓ gap 610 unadvertised            │
│                                                                            │
│  Punjab       N ████████████       358                                     │
│               A ░░░░░░░░░░░░         0   ▓ 0 advertised since 2017         │
│               F ░░░░░░░░░░░░         0                                     │
│                                                                            │
│  Karnataka    N █████████          212                                     │
│               A ███                 61                                     │
│               F ██                  44                                     │
├────────────────────────────────────────────────────────────────────────────┤
│  Rows · all figures sourced and dated                                      │
│  STATE      DEPT      GRP  NOTIF  ADV  FILLED  AS OF      SOURCE    AGE    │
│  Haryana    Police     C   1,057   447    447  31 Mar 26  ↗ link    9d ⚠   │
│  Punjab     Police     C     358     0      0  31 Mar 26  ↗ link   22d ⚠   │
│  Karnataka  PSU        C     212    61     44  28 Feb 26  ↗ link   31d ⚠   │
│  ── Public data · no athlete information on this page ──                   │
└────────────────────────────────────────────────────────────────────────────┘
```
Notified = navy, advertised = mid navy, filled = dark navy. `░` dashed = zero. Staleness: ⚠ amber >30 days, red >90. This screen is deliberately plain — it must survive being printed and quoted.

### 23. Vacancy Data Ingest — admin

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Publish vacancy data                     Step 2 of 3 · Preview diff        │
├────────────────────────────────────────────────────────────────────────────┤
│  Uploaded  vacancy_q4_2026.csv · 34 rows                                    │
│                                                                            │
│  VALIDATION                                                                │
│  ● 31 rows valid                                                           │
│  ●  2 rows missing source URL       [ blocked ]                            │
│  ●  1 row missing as-of date        [ blocked ]                            │
├────────────────────────────────────────────────────────────────────────────┤
│  CHANGES vs current                                                        │
│  Haryana · Police · C    447 → 447   no change                             │
│  Punjab  · Police · C      0 →   0   no change                             │
│  Karnataka · PSU  · C     44 →  61   +17  filled ▲                         │
│  Bihar · Police · C        — →  88   new row                               │
├────────────────────────────────────────────────────────────────────────────┤
│  Publishing as: A. Sharma (admin) · 31 Mar 2026 11:02                      │
│                              [ Back ]   [ Publish 31 rows ]                │
└────────────────────────────────────────────────────────────────────────────┘
```

### 24. Verification Record Summary

```
┌────────────────────────────────────────────────────────────────────────────┐
│  ATHLETE RECORD SUMMARY                         ⚠ Not an eligibility cert. │
├────────────────────────────────────────────────────────────────────────────┤
│  Rohan Patil · 14 · Kabaddi · Dist. Pune · KID 4821                        │
│  Record covers 14 Jan 2024 – 31 Mar 2026                                   │
├────────────────────────────────────────────────────────────────────────────┤
│  COMPETITION HISTORY                                                       │
│   2026  District  Pune Kabaddi Championship   2nd                          │
│   2025  Block     Haveli Kabaddi League       1st                          │
│   2024  Block     Haveli Kabaddi League       participated                 │
├────────────────────────────────────────────────────────────────────────────┤
│  TRAINING CONTINUITY          avg 3.1 sessions/week · 84% quarters logged  │
│  COACHING                     S. Deshmukh (NCAB L0) 2024–26                │
│                               local coach, uncertified, 2024 (4 months)    │
│  FUNDING RECEIVED             Khelo India OPA · ₹10,000/mo · 14 months     │
├────────────────────────────────────────────────────────────────────────────┤
│  This summary states recorded facts only. It does not certify eligibility  │
│  for any quota, scheme or selection.                                       │
│                    [ Export PDF ]      hash 8f3a2c…                        │
└────────────────────────────────────────────────────────────────────────────┘
```
The disclaimer is inside the header band and repeated in the footer — deliberately redundant.

### 25. Verification Hash Check — public

```
┌────────────────────────────────────────────────────────────────────────────┐
│  Verify a record summary                                                   │
│  ┌──────────────────────────────────────────┐  ┌────────────────────┐      │
│  │ 8f3a2c                                   │  │  Verify  navy      │      │
│  └──────────────────────────────────────────┘  └────────────────────┘      │
├────────────────────────────────────────────────────────────────────────────┤
│  ● Match                                                                   │
│  R. P. · 14 · Kabaddi · Dist. Pune · issued 31 Mar 2026                    │
│  Issued by TrackNet · 3 competition records · 2 seasons of training        │
│  Name masked. Full record available only to the holder and authorised      │
│  officers.                                                                 │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Cross-cutting

### 26. Audit Log Viewer — admin

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Audit log (immutable)      Actor ▾ Role ▾ Entity ▾ Action ▾ Date ▾         │
├────────────────────────────────────────────────────────────────────────────┤
│ WHEN              ACTOR     ROLE      ENTITY       ACTION    FIELDS        │
│ 31 Mar 11:02      A.Sharma  admin     vacancy#88   publish   —             │
│ 31 Mar 10:41      M.Nair    steward   athlete#4821 view      name, dob     │
│ 31 Mar 09:12      S.Deshmukh coach    log#9912     create    —             │
├────────────────────────────────────────────────────────────────────────────┤
│ ⓘ Field names only. Values are never shown here.                           │
└────────────────────────────────────────────────────────────────────────────┘
```

### 27. Steward Org & User Management — admin

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Organisations                                       [ + Add org ] saffron  │
├────────────────────────────────────────────────────────────────────────────┤
│ ORG                          TYPE        DISTRICT   SPORTS       STATUS    │
│ Pune Sports Trust            NGO         Pune       Kabaddi     ● active   │
│ SP College PE Dept           College     Pune       All         ● active   │
│ Satara Dist. Kabaddi Assoc.  Association Satara     Kabaddi     ● paused   │
├────────────────────────────────────────────────────────────────────────────┤
│  Selected: Pune Sports Trust                                               │
│  USERS                                                                     │
│  Meera Nair     steward     ● active     [ Change role ] [ Deactivate ]    │
│  Kiran Joshi    kic_coach   ● active     [ Change role ] [ Deactivate ]    │
└────────────────────────────────────────────────────────────────────────────┘
```

### 28. Settings — all roles, scoped

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Settings                                                                   │
├────────────────────────────────────────────────────────────────────────────┤
│  Language             (•) English   ( ) हिंदी                              │
│  Notify me by         ☑ SMS   ☑ IVR   ☐ Web only                          │
│  Phone                +91 98765 43210      [ Change ]                      │
│  My scope             Dist. Pune · Kabaddi  (set by admin)                 │
│  Session              signed in 09:41 · expires 17:41   [ Sign out ]       │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Notes on consistency

- Every screen opens with a **page title + scope chip** on the right. If a screen cannot state its scope, it should not exist.
- Every card carries an **"as of" stamp**, and every page repeats the source strip at the bottom. This is the visual expression of the auditability requirement — it is not decoration.
- Colour is reserved for **status and action only**. If a screen looks colourful, it's a bug.
- The two public screens (20, 22) are visually plainer than everything else — wider margins, fewer borders, no chips. They are for quoting, not for operating.
- Screens 3, 13, 14 and 21 are the ones to review first after each phase ships.


# Phase 0 — Foundation & Manual-Mode Scaffold

Before writing code, read:
- @docs/01-constraints.md
- @docs/02-data-model.md  (all entities)
- @docs/04-phases.md  § Phase 0
- @docs/03-screens.md  § Screens 1, 2, 3, 4

Deliver:
1. Next.js 14 App Router + TypeScript strict + Tailwind + shadcn/ui
2. Postgres via Prisma; migrations for every entity in @docs/02-data-model.md
3. Auth with RBAC; session carries role + steward_org_id
4. Seed script: 2 districts, 3 sports, 500 mock athletes with a realistic
   12-month dropout curve (reproducible, seeded random)
5. Audit-log middleware (append-only, no PII values)
6. Screens 1, 2, 4 from @docs/03-screens.md
7. Screen 3 — Retention Brief — backed by a real computation engine
   that produces the same numbers as the seed data
8. `.env.example`, README with local setup, `pnpm dev` runs clean

Acceptance (show commands + output for each):
- `pnpm dev` starts; landing page loads at 360px width
- Seed runs idempotently; 500 athletes; dropout curve matches hand-calc
- Retention brief PDF exports and reconciles with engine output
- Every PII field is encrypted at rest (grep for plaintext in DB)
- Audit log captures athlete reads
- Playwright: sign-in flow + retention brief export pass on Slow 3G

Do NOT:
- Build any athlete CRUD UI (that is Phase 1)
- Build the follow-up engine (Phase 2)
- Add screens 5–28

When done: update PROGRESS.md, list acceptance criteria pass/fail with
evidence, list deviations and why, then STOP and wait for approval.

tracknet/
├── CLAUDE.md                    ← auto-loaded by Antigravity every session
├── README.md                    ← 20-line project pitch
├── PROGRESS.md                  ← updated after each phase (see below)
├── DECISIONS.md                 ← log of ambiguous calls + your ruling
│
├── docs/
│   ├── 00-mission.md            ← "after KID, nothing follows" problem
│   ├── 01-constraints.md        ← the 8 hard constraints from §2
│   ├── 02-data-model.md         ← entities, fields, encryption rules
│   ├── 03-screens.md            ← the text-view look & feel you just reviewed
│   ├── 04-phases.md             ← 5 phases with acceptance criteria
│   └── 05-non-goals.md          ← the do-not-build list
│
├── prompts/
│   ├── phase-0.md               ← ~35 lines, feed to Antigravity
│   ├── phase-1.md
│   ├── phase-2.md
│   ├── phase-3.md
│   └── phase-4.md
│
└── (app code lands here as phases ship)

# TrackNet — always-on rules

You are building TrackNet, a post-KID athlete tracking and verification
layer for Indian sports. Read @docs/00-mission.md and @docs/01-constraints.md
before writing any code.

NEVER, in any phase:
- Collect Aadhaar, passport, biometrics, or ID uploads
- Build a social feed, messaging, or coach/athlete matching
- Build athlete "potential" scoring or medal prediction
- Disburse money or create a payment channel
- Add gamification, leaderboards, or discovery bounties
- Write to NSRS/Khelo India systems (read-only)

ALWAYS:
- KID first; provisional_id only if no KID exists
- Field-encrypt PII; audit-log every read/write of PII
- Show "as of" date and data source on every number
- SMS/IVR fallback for every athlete-facing touchpoint
- RBAC scoped by steward_org_id from session

Working rules:
- One phase at a time. Stop at the end of each phase and wait.
- Commit at the end of each phase with tag `phase-N-done`.
- If a request conflicts with the rules above, do not comply — quote
  the conflicting rule from @docs/01-constraints.md and ask.
- Log every ambiguous design call to DECISIONS.md.
