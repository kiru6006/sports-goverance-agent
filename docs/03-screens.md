# Screen & Interface Specifications

All views in TrackNet / NSIS share an auditable application shell:
1. **Top Bar**: System title, Role badge (`NATIONAL_ADMIN`, `STATE_OFFICER`, `DISTRICT_OFFICER`, `COACH`), Geography scope indicator, and Language toggle (English / हिंदी).
2. **Bottom Status Strip**: Mandatory provenance bar showing **"Data as of: <timestamp> · Source: State Registry / SAI [Synthetic]"**.

---

## Screen 1: Public Landing & Verification Check
- **Access**: Unauthenticated / Public
- **Objective**: Explain the mandate, present the 5-stage loop, offer role-based sign-in entrypoints, and provide a lookup tool to verify an athlete's certificate / public status (showing only verified status without revealing personal PII).

## Screen 2: Role Sign-In & Scope Auto-Resolution
- **Access**: Public / Auth Gateway
- **Objective**: Authenticate via credential/OTP; session token auto-binds user role, state, and district scope.

## Screen 3: Pipeline Diagnosis & Retention Heatmap
- **Access**: `NATIONAL_ADMIN`, `STATE_OFFICER`, `DISTRICT_OFFICER`
- **Objective**: Sport × District × Age band grid displaying identified-per-100k rates, conversion funnels, and peer-median gap flags. Cells with $< 5$ athletes display `<5 (Suppressed)` to preserve privacy.

## Screen 4: Unified Registry & Verification Queue
- **Access**: `DISTRICT_OFFICER`, `STATE_OFFICER`, `COACH`
- **Objective**: Server-paginated registry list with duplicate-candidate warnings, minor-consent indicators, and state machine transition controls (`VERIFY`, `REQUEST_INFO`, `REJECT`). Minor records outside user district are concealed (404).

## Screen 5: Grounded Policy Agent & Action Proposals
- **Access**: Officials only
- **Objective**: Natural language queries answered strictly with citations from approved ministry guidelines. Read-mostly tools with an `Action Proposals` inbox for two-person human approval.
