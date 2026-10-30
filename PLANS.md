# National Sports Intelligence System (NSIS)
## Concept Note for the Ministry of Youth Affairs and Sports, Government of India

**Status:** Draft for discussion. Not reviewed by the ministry, SAI, or counsel.
**Verification legend:** [Certain] established fact or engineering consensus. [Likely] plausible, needs confirmation. [Verify] must be checked against a current primary source before use.

---

## 1. Purpose

NSIS is a decision-support and policy-execution platform. It makes India's sports pipeline visible at athlete, trainer, facility, and scheme level, so that officials can find gaps, allocate existing support, and measure whether it reaches athletes.

NSIS does not select athletes, award funds, or replace federations or existing schemes. Officials make every decision. The system recommends, records, and explains.

**Ask:** Mandate and a named decision owner to run a supervised two-state pilot, plus data-sharing agreements and a governance structure for the pilot.

---

## 2. Problem Statement

The core problem is not a lack of talent or a lack of money alone. It is that the system cannot see its own pipeline. [Likely]

| Symptom | Underlying cause |
|---|---|
| Talent identified in one district is lost by the next stage | No shared athlete identity across school, district, state, and federation records [Likely] |
| Support schemes are underused | Athletes and local officials do not know eligibility, and no system links eligibility to the athlete [Likely] |
| Trainers are unqualified, unpaid, or unrecognised | No verified trainer registry or certification path visible to officials [Likely] |
| Equipment and facilities are idle, missing, or unmatched to demand | No inventory with utilisation data [Likely] |
| Athletes leave sport between school and senior level | No age-band tracking that flags dropout early [Likely] |
| Officials cannot demonstrate impact | Outcome data is not linked to spending or schemes [Likely] |

**Key finding:** Most problems trace back to missing linkage between identification, support, and outcome. Funding and policy changes matter, but they cannot be targeted without this linkage.

---

## 3. Proposed Approach

NSIS follows one loop:

**Sense → Diagnose → Prescribe → Allocate → Measure → feed back into policy.**

| Stage | Output |
|---|---|
| Sense | Verified registry of athletes, trainers, institutions, and facilities |
| Diagnose | Gap view by sport, district, and age band, with explainable flags |
| Prescribe | Ranked policy levers mapped to existing or proposed schemes, each with a source reference |
| Allocate | Eligibility matches, equipment loans, trainer placements, opportunity listings. Officials approve each allocation. |
| Measure | Pipeline conversion, scheme uptake, dropout rate, certification retention |

### Design principles

- **Pipeline metrics, not medal forecasts.** Medal counts are a lagging outcome shaped by many factors. NSIS reports identification, support, and progression rates.
- **Explainable outputs.** Every flag or eligibility result shows its reasons, the rule version, and the source document.
- **Human decisions.** No automated exclusion, selection, or fund release.
- **Minors protected by design.** Verifiable parental consent, restricted visibility, and audit logging on every read of a minor's record.
- **State adapters, not 36 systems.** A shared central schema with state-level configuration for local sports, schemes, and languages.

---

## 4. Architecture Summary

| Layer | Components |
|---|---|
| Frontend | Web application (Angular), role-based dashboards, offline-capable mode for district and village staff |
| Central core | Identity, registry, pipeline analytics, scheme eligibility engine, facility and equipment, opportunity board, notifications |
| Assistant | Tool-based assistant for officials, answering only from approved policy documents with citations, with human approval for any change |
| State adapters | Versioned configuration per state, no changes to core schema or central records |
| Hosting | India-region, MeitY-empanelled cloud [Likely, verify with MeitY and the ministry's IT security team] |
| Observability | Structured logs, metrics, traces, immutable audit log |

**Governance:** Minor records are visible only to the assigned coach, the district officer, and the guardian reference. Scheme rules require maker-checker approval by a second authorised person. Assistant actions are logged and reviewable.

---

## 5. Policy Alignment

NSIS does not create new schemes. It works with existing instruments. The following must be confirmed with the ministry before any mapping is used:

| Area | Existing instrument to confirm | Status |
|---|---|---|
| National sports policy | Current version and its implementation mandates | [Verify] |
| Talent identification and athlete support | Current Khelo India programme components and eligibility | [Verify] |
| Elite athlete support | Current elite athlete support scheme and its criteria | [Verify] |
| Sports quotas | Quota rules in railways, armed forces, PSUs, and state police, per employer | [Verify] |
| Coach certification and licensing | Current certification pathway and bodies | [Verify] |
| Facilities | Existing facility creation and maintenance schemes, and SAI centre network | [Verify] |
| Data protection | DPDP Act 2023 and applicable DPDP Rules, including consent and processor obligations | [Verify current rules status] |

**Rule for the pilot:** No scheme rule enters the system until the ministry supplies the source document, page, and clause. Placeholder rules are clearly labelled and cannot drive eligibility.

---

## 6. Pilot Proposal

### Scope

| Item | Proposal |
|---|---|
| States | 2 pilot states, selected with the ministry for sports participation, existing data quality, and willingness to sign an MoU |
| Districts | 4 to 6 districts across the two states |
| Sports | 5 to 8 sports, chosen with national federations. Include at least one team sport and one individual sport. |
| Population | Athletes aged 10 and above, with specific attention to ages 10 to 19 |
| Users | District sports officers, state officers, selected coaches, NGO and volunteer verifiers |
| Duration | Phase 0 and Phase 1 of the build, then a 6-month supervised run [Likely] |

### Phased timeline

| Phase | Timeline | Exit criterion |
|---|---|---|
| 0. Alignment | 0 to 4 months | Signed MoUs, data-sharing agreements, legal opinion on DPDP compliance, agreed sport taxonomy and ID scheme |
| 1. Registry | 4 to 9 months | Verified sample audit meets an error threshold agreed with the ministry before the audit starts |
| 2. Diagnosis | 9 to 15 months | At least one district uses the gap view for a real allocation decision |
| 3. Support linkage | 12 to 18 months | Measured change in scheme uptake against a pre-agreed baseline |
| 4. Assistant | 15 to 24 months | Assistant used by officials; disagreement rate tracked and reviewed |
| 5. Scale | 24 months onward | Conditional on pilot results and a separate funding decision |

Timelines are planning assumptions. [Likely] They depend on MoU timing and procurement.

### Success metrics (pilot)

- Athletes identified per 100,000 population, per sport, per district
- Identified-to-supported conversion rate
- Scheme uptake among eligible athletes, against baseline
- Trainer certification rate and retention
- Dropout rate by age band
- International medal outcomes, tracked as a lagging indicator only

---

## 7. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Treated as a data project with no policy owner | Name a decision owner in the ministry before Phase 0 begins |
| Federations and states decline data sharing | Start with states that sign MoUs; give each party a visible benefit from the registry |
| Minors' data breach | Consent workflow, encryption, restricted access, audit logs, independent security testing before any real data |
| Gap view misread as district performance ranking | Label the view "pipeline indicator, not a performance score" in the UI and in every export |
| Small-district rates are volatile | Suppress cells below a minimum count; show denominators |
| Officials over-rely on the assistant | Every answer cites a source; officials approve every change; disagreement rate is reviewed |
| Political turnover | Central sponsorship plus state MoUs; state-level configuration is modular |
| Scope creep to "every village" | Pilot-gated expansion with exit criteria per phase |

---

## 8. Governance and Decisions Requested

### Decisions needed from the ministry

1. Nominate a senior officer as decision owner and sponsor for the pilot.
2. Select the two pilot states and the districts within them.
3. Confirm the authority to sign MoUs with states and national federations.
4. Confirm the approval route for scheme rules, including who approves state-level schemes.
5. Confirm the hosting and data-residency requirements for the platform.
6. Agree the go/no-go criteria for the pilot before it starts.

### Decisions needed from counsel

1. DPDP Act 2023 position: consent, processor and fiduciary roles, retention, erasure, and minors.
2. Legal basis for using existing scheme data in an eligibility engine.
3. Terms for any assistant that processes personal data.
4. Device policy for offline use on district devices.

### Pilot steering group (proposed)

- Ministry sponsor (chair)
- Representatives from SAI and two national federations
- Two state sports department nominees
- Counsel
- IT security lead
- Independent technical reviewer

---

## 9. Evidence the Pilot Will Produce

| Evidence | Purpose |
|---|---|
| Verified sample audit results | Data quality before any analysis |
| Pipeline and conversion reports by sport and district | Diagnosis for officials |
| Scheme uptake comparison with baseline | Whether existing support reaches athletes |
| Independent security assessment | Readiness for real personal data |
| Restore and recovery drill results | Operational resilience |
| Accessibility audit | Compliance with government standards for public-facing interfaces [Verify applicable standard] |
| Decision log of officer approvals | Accountability for allocations |

---

## 10. Limitations of This Concept

- The analysis of current sports policy, articles, and government sources has not been completed. It is the first task of Phase 0 and must be done from primary documents.
- Cost estimates are not included. They depend on the chosen hosting model, vendor arrangements, and data-collection approach.
- Achievement of any national medal target is outside NSIS's control. NSIS can improve the information available for decisions.
- Assumptions about data availability in pilot states must be checked during Phase 0.

---

## 11. Next Steps

1. Ministry review of this note and a meeting with the proposed sponsor.
2. Confirmation of pilot states and the sponsor's decision on the governance structure.
3. Counsel review of the data-protection position.
4. Phase 0 kickoff, including the primary-source policy analysis.

---

*Prepared as a discussion document. All [Verify] items must be confirmed against current primary sources before this note is shared outside the proposing team.*