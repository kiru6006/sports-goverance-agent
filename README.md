# TRACKNET / NSIS
## National Sports Intelligence System & Athlete Retention Agent

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-cyan.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2+-blue.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0+-purple.svg)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4+-38bdf8.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-Proprietary_Gov_Pilot-red.svg)](#)

> **TrackNet (NSIS)** is an intelligence and policy-execution operating layer for Indian Sports (Ministry of Youth Affairs and Sports / Khelo India ecosystem). It provides continuous visibility into the athlete pipeline across identification, support, and progression, bridging the critical gap between grassroots talent identification (KID) and long-term sports retention.

---

## 🏛 Core Purpose & Operating Loop

The system operates on an auditable policy-execution cycle:

$$\text{Sense} \longrightarrow \text{Diagnose} \longrightarrow \text{Prescribe} \longrightarrow \text{Allocate} \longrightarrow \text{Measure}$$

- **Sense**: Verified registry of athletes, trainers, institutions, and facilities with strict minor consent & DPDP protections.
- **Diagnose**: District × Sport × Age-band gap diagnosis with small-cell privacy suppression ($< 5$ counts suppressed).
- **Prescribe**: Explainable policy levers mapped to versioned scheme rules with clause-level citations.
- **Allocate**: Eligibility matching, equipment loans, and opportunity listings—with strict human-in-the-loop approvals.
- **Measure**: Multi-year pipeline conversion, dropout curves, and scheme uptake metrics.

---

## 🔒 Non-Negotiable System Invariants

1. **Decision Support, NOT Automated Selection**: NSIS never autonomously selects athletes, awards quotas, or disburses money. Officials approve every mutation.
2. **Protection of Minors by Design**:
   - Mandatory guardian consent step prior to submission.
   - Unauthorized attempts to view minor profiles return **HTTP 404 Not Found** (never 403) to prevent existence probing.
   - Immutable audit logging on every read or query touching a minor record.
3. **Field-Level Encryption**: All sensitive identifying data (DOB, contact details, guardian references) is encrypted at rest.
4. **No Biometrics / Aadhaar**: Never collect Aadhaar numbers, biometric data, or identity document scans.
5. **Read-Mostly Agent with ActionProposal Gating**: The AI agent assists by querying approved documents and proposing actions (`approver_id != actor_id`).

---

## 🏗 Architecture Overview

```mermaid
flowchart TB
    subgraph UI ["Frontend (React 18 + TypeScript + TailwindCSS)"]
        Landing["Public Landing & Verification Status"]
        Dashboard["Pipeline Diagnosis & Retention Heatmaps"]
        Registry["Unified Registry (Athletes, Coaches, Facilities)"]
        SchemesUI["Scheme Rules & Eligibility Checker"]
        AgentUI["Agent Assistant & Policy RAG Console"]
        ApprovalsUI["Human Action Proposals Inbox"]
    end

    subgraph API ["FastAPI Core Backend (Python 3.11+)"]
        AuthRouter["/api/v1/auth (RBAC + Geo-Scope)"]
        RegistryRouter["/api/v1/registry"]
        PipelineRouter["/api/v1/pipeline (Aggregates & Gaps)"]
        SchemesRouter["/api/v1/schemes (Eligibility Engine)"]
        AgentRouter["/api/v1/agent (Tool Calls & RAG)"]
        AuditRouter["/api/v1/audit (Immutable Event Trail)"]
    end

    subgraph CoreEngine ["Domain Engines & Workflow Logic"]
        DedupEngine["Fuzzy Trigram Deduplication"]
        StateMachines["Verification & Approval State Machines"]
        EligibilityEngine["Deterministic Scheme Rule Evaluator"]
        GapAnalyzer["Peer Median Pipeline Gap Analyzer"]
        OutboxRelay["Idempotent Outbox Notification Worker"]
    end

    subgraph Persistence ["Data Layer (PostgreSQL / SQLite)"]
        DB[(Core Database + PostGIS)]
        VectorIndex[(pgvector / Approved Policy Chunks)]
        AuditLog[(Tamper-Resistant Audit Trail)]
    end

    UI --> API
    API --> CoreEngine
    CoreEngine --> Persistence
```

---

## 📂 Repository Layout

```text
sports-network-agent/
├── CLAUDE.md                    # Core ground rules & invariants (auto-loaded)
├── README.md                    # System pitch, architecture, and run instructions
│
├── docs/                        # Structured System Documentation & Specifications
│   ├── 01-plans.md              # Ministry concept note & policy alignment
│   ├── 02-specifications.md     # Constraints, data models, screen catalog & architecture
│   ├── 03-ideas.md              # Implementation blueprint & acceptance criteria
│   ├── 04-decisions.md          # Architecture Decision Records (ADRs)
│   ├── 05-progress.md           # Milestone status & phase gate tracker
│   └── 06-ground-rules.md       # Hard security, privacy & legal invariants
│
├── backend/                     # Python 3.11+ FastAPI Backend
│   ├── requirements.txt         # Core dependencies
│   ├── app/
│   │   ├── main.py              # Application entrypoint & middleware
│   │   ├── core/                # Config, DB connection, crypto & RBAC
│   │   ├── models/              # SQLAlchemy 2.0 ORM models
│   │   ├── schemas/             # Pydantic v2 schemas
│   │   ├── services/            # Domain logic (Registry, Pipeline, Schemes, Agent)
│   │   └── api/routes/          # REST API endpoints
│   └── tests/                   # Pytest test suite
│
└── frontend/                    # React 18 + Vite + TypeScript Frontend
    ├── package.json             # Node dependencies
    ├── vite.config.ts           # Vite bundler configuration
    ├── tailwind.config.js       # Tailwind CSS configuration
    └── src/
        ├── main.tsx             # React entrypoint
        ├── App.tsx              # Router & layout
        ├── components/          # Reusable UI components
        ├── pages/               # Views (Landing, Diagnosis, Registry, Agent, Approvals)
        └── data/                # Seed mock fixtures for offline preview
```

---

## 📚 Documentation Index

All primary system documentation is maintained under the [`docs/`](docs/) directory:

1. [**01-plans.md**](docs/01-plans.md) — Concept Note for the Ministry of Youth Affairs and Sports, problem statement, operating loop, and policy levers.
2. [**02-specifications.md**](docs/02-specifications.md) — Unified constraints, entity privacy tiers, screen catalog (S-00 to S-84), and architecture roadmaps.
3. [**03-ideas.md**](docs/03-ideas.md) — Exhaustive domain blueprint, functional requirements, and acceptance criteria.
4. [**04-decisions.md**](docs/04-decisions.md) — Architecture Decision Records (ADRs: stack standardization, minor 404, small-cell suppression, maker-checker).
5. [**05-progress.md**](docs/05-progress.md) — Milestone status, test suites, and phase verification gates (Phases 0–7).
6. [**06-ground-rules.md**](docs/06-ground-rules.md) — Absolute constraints, DPDP Act 2023 compliance, and engineering conventions.

---

## 👥 Seed Roles & Access Scopes

| Role | Typical Actor | Geographical Scope | Permissions |
| :--- | :--- | :--- | :--- |
| `NATIONAL_ADMIN` | Ministry / SAI Directorate | All States & Districts | Full policy view, scheme rule approvals, agent config |
| `STATE_OFFICER` | State Directorate Officer | Assigned State | State gap view, district comparisons, state scheme authoring |
| `DISTRICT_OFFICER` | District Sports Officer (DSO) | Assigned District | Registry verification, equipment loans, athlete support |
| `COACH` | Certified Coach / Trainer | Assigned Athletes / Club | Athlete onboarding, journey updates, training logs |

---

## 🚀 Local Quickstart

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or 20
- PostgreSQL with PostGIS (optional for dev; SQLite fallback supported)

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env

# Initialize DB & Seed Data
python -c "from app.core.db import init_db; init_db()"

# Start FastAPI Server (Runs on port 8001)
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```
API Documentation will be live at: `http://localhost:8001/docs`

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🌐 Public Live Demo & Deployment

- **GitHub Pages**: [https://kiru6006.github.io/sports-goverance-agent/](https://kiru6006.github.io/sports-goverance-agent/)
- **Automated CI/CD**: Automatic GitHub Actions build & deployment to GitHub Pages on every push to `main` ([.github/workflows/deploy.yml](.github/workflows/deploy.yml)). (Ensure GitHub Repo **Settings** $\to$ **Pages** $\to$ **Build and deployment** is set to **GitHub Actions**).

---

## 📋 Comprehensive Feature Implementation Status

All mandatory government sports intelligence and governance capabilities have been verified and implemented:

| Capability Area | Core Feature | Status | Specification File |
| :--- | :--- | :--- | :--- |
| **Talent & Registry** | Fuzzy Trigram Deduplication | ✅ Implemented | [`docs/02-specifications.md#4-phase-roadmaps`](docs/02-specifications.md#4-phase-roadmaps--verification-status) |
| | Minor Concealment (DPDP Act HTTP 404) | ✅ Implemented | [`docs/02-specifications.md#1-statutory-constraints`](docs/02-specifications.md#1-statutory-constraints--non-negotiable-invariants) |
| | Verification State Machine (`SUBMITTED` $\to$ `UNDER_REVIEW` $\to$ `VERIFIED` / `REJECTED`) | ✅ Implemented | [`docs/02-specifications.md#2-core-entities`](docs/02-specifications.md#2-core-entities--privacy-tiers) |
| | Candidate Rejection Audit & Reason Reports | ✅ Implemented | [`docs/05-progress.md#phase-7`](docs/05-progress.md#ai-sdlc-phase-gate-status) |
| | Derived Age-Band Classification (`U-14`, `U-17`, `U-19`, `SENIOR`) | ✅ Implemented | [`docs/02-specifications.md#2-core-entities`](docs/02-specifications.md#2-core-entities--privacy-tiers) |
| **Pipeline & Analytics** | District $\times$ Sport $\times$ Age Band Gap Diagnosis | ✅ Implemented | [`docs/02-specifications.md#4-phase-roadmaps`](docs/02-specifications.md#4-phase-roadmaps--verification-status) |
| | Small-Cell Privacy Suppression ($<5$ counts redacted) | ✅ Implemented | [`docs/02-specifications.md#1-statutory-constraints`](docs/02-specifications.md#1-statutory-constraints--non-negotiable-invariants) |
| | Cumulative Athlete Conversion Funnel (Identified $\ge$ Verified $\ge$ Supported $\ge$ Progressed) | ✅ Implemented | [`docs/02-specifications.md#4-phase-roadmaps`](docs/02-specifications.md#4-phase-roadmaps--verification-status) |
| | Peer Median Bottleneck Detection | ✅ Implemented | [`docs/02-specifications.md#3-screen-catalog`](docs/02-specifications.md#3-screen--functional-catalog) |
| **Infrastructure & Assets**| Equipment Inventory & Custody Tracking | ✅ Implemented | [`docs/02-specifications.md#4-phase-roadmaps`](docs/02-specifications.md#4-phase-roadmaps--verification-status) |
| | Overdue Equipment Loan Flagging & Fines | ✅ Implemented | [`docs/02-specifications.md#4-phase-roadmaps`](docs/02-specifications.md#4-phase-roadmaps--verification-status) |
| | Training Facilities & Venue Capacity Ledger | ✅ Implemented | [`docs/02-specifications.md#2-core-entities`](docs/02-specifications.md#2-core-entities--privacy-tiers) |
| **Schemes & Opportunities**| Deterministic Scheme Rule Evaluator with Citations | ✅ Implemented | [`docs/02-specifications.md#4-phase-roadmaps`](docs/02-specifications.md#4-phase-roadmaps--verification-status) |
| | Maker-Checker Rule Authorization (`approver_id != author_id`) | ✅ Implemented | [`docs/02-specifications.md#4-phase-roadmaps`](docs/02-specifications.md#4-phase-roadmaps--verification-status) |
| | Transactional Outbox with Zero-PII Tokens | ✅ Implemented | [`docs/02-specifications.md#4-phase-roadmaps`](docs/02-specifications.md#4-phase-roadmaps--verification-status) |
| | Support Demands & Services Needed / Offered Matrix | ✅ Implemented | [`docs/05-progress.md#phase-7`](docs/05-progress.md#ai-sdlc-phase-gate-status) |
| **Communication & Network**| Cross-Profile Contact Mapping (Player, Coach, Specialist) | ✅ Implemented | [`docs/05-progress.md#phase-7`](docs/05-progress.md#ai-sdlc-phase-gate-status) |
| | Direct Peer-to-Peer Messaging Drawer | ✅ Implemented | [`docs/05-progress.md#phase-7`](docs/05-progress.md#ai-sdlc-phase-gate-status) |
| **AI Ecosystem & Policy** | Read-Only Grounded Policy RAG Agent | ✅ Implemented | [`docs/02-specifications.md#4-phase-roadmaps`](docs/02-specifications.md#4-phase-roadmaps--verification-status) |
| | Two-Person `ActionProposal` Approval Queue | ✅ Implemented | [`docs/04-decisions.md#decision-005`](docs/04-decisions.md#decision-005-read-mostly-agent-with-actionproposal-human-gates) |
| | Anti-Hallucination 100% Policy Citation Enforcement | ✅ Implemented | [`docs/02-specifications.md#4-phase-roadmaps`](docs/02-specifications.md#4-phase-roadmaps--verification-status) |
| **Field Resilience & Sync** | State Adapters & Offline PWA Sync Protocol | ✅ Implemented | [`docs/02-specifications.md#4-phase-roadmaps`](docs/02-specifications.md#4-phase-roadmaps--verification-status) |
| | Multi-Lingual Interface (English, Hindi, Marathi) | ✅ Implemented | [`docs/02-specifications.md#3-screen-catalog`](docs/02-specifications.md#3-screen--functional-catalog) |
| | Deterministic Conflict Resolution Matrix | ✅ Implemented | [`docs/02-specifications.md#4-phase-roadmaps`](docs/02-specifications.md#4-phase-roadmaps--verification-status) |
| **Security & ASVS L2** | SHA-256 Tamper-Evident Audit Hash Chain | ✅ Implemented | [`docs/02-specifications.md#4-phase-roadmaps`](docs/02-specifications.md#4-phase-roadmaps--verification-status) |
| | Emergency AI Agent Kill-Switch | ✅ Implemented | [`docs/02-specifications.md#4-phase-roadmaps`](docs/02-specifications.md#4-phase-roadmaps--verification-status) |
| | Right-to-Erasure (DPDP Act) Anonymization Workflow | ✅ Implemented | [`docs/02-specifications.md#4-phase-roadmaps`](docs/02-specifications.md#4-phase-roadmaps--verification-status) |
| | Automated Chaos Drill & Recovery Engine | ✅ Implemented | [`docs/02-specifications.md#4-phase-roadmaps`](docs/02-specifications.md#4-phase-roadmaps--verification-status) |
| **Modern UX Design** | Responsive Collapsible Left-Side Navigation Bar | ✅ Implemented | [`frontend/src/App.tsx`](frontend/src/App.tsx) |
| | Accessible High-Contrast Theme with Inter Typography | ✅ Implemented | [`frontend/tailwind.config.js`](frontend/tailwind.config.js) |

---

## 🧪 Testing & Verification

Run backend unit & security tests (All 44 tests pass):
```bash
cd backend
PYTHONPATH=. pytest tests/ -v
```

Run frontend production bundle build:
```bash
cd frontend
npm run build
```
