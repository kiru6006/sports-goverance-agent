# Phase 4 Plan: Grounded Agent Layer & Action Proposals

Following the AI SDLC protocol defined in [IDEAS.md](file:///Users/apple/projects/sports-network-agent/IDEAS.md) and [docs/04-phases.md](file:///Users/apple/projects/sports-network-agent/docs/04-phases.md), Phase 4 establishes the intelligent assistant layer (`agent-svc`) to empower state and district sports officers with grounded policy guidance and decision-support proposals.

---

## 1. Architectural Principles & Non-Negotiables

1. **Strict Read-Only Tool Execution by Default**:
   - The agent can freely query read tools (`search_athletes`, `get_pipeline_gaps`, `check_eligibility`, `list_opportunities`, `query_policy_docs`).
   - The agent **CANNOT** execute state-changing writes (e.g. creating/approving rules, verifying athletes, or disbursing funds) directly.
2. **Action Proposal Workflow with Cryptographic Approval Tokens**:
   - Any suggested write operation emits a structured `ActionProposal` with `status: PENDING_APPROVAL`, exact diff preview, and reason.
   - Execution requires an explicit officer invocation at `/api/v1/agent/proposals/{proposal_id}/execute` accompanied by an approval token.
3. **100% Citation Enforcement (Zero Hallucination Policy)**:
   - Every policy/guideline query retrieves chunks exclusively from verified, approved government documents.
   - If no relevant chunk matches above confidence threshold, the agent must output: `"No source found in approved guidelines."`
4. **Preserved RBAC & Minor Concealment Under Adversarial Prompts**:
   - Agent tool execution inherits the caller's `UserContext` and geo-scope.
   - A `DISTRICT_OFFICER` asking about another district's minors or aggregate records will receive a strict 404/redacted response from the underlying tools.
5. **Tamper-Evident Audit Logging**:
   - All agent queries, prompt hashes, tool calls, model versions, and proposal creations are logged into `audit_logs` with SHA-256 payload chaining.

---

## 2. Component Structure

```text
backend/app/
├── core/
│   ├── agent_service.py       # Grounded Tool Calling & Policy RAG Engine
│   ├── policy_store.py        # Vector/Embedding chunk index with metadata
│   └── seed_phase4.py         # Primary policy documents (MYAS, SAI, State circulars)
├── models/
│   └── entities.py            # Added ActionProposal & PolicyChunk models
├── schemas/
│   └── dto.py                 # AgentQueryRequest, AgentQueryResponse, ActionProposalDTO
└── api/
    └── routes.py              # /agent/chat, /agent/tools, /agent/proposals, /agent/proposals/{id}/execute
```

---

## 3. Data Model Extensions

```python
class PolicyChunk(Base):
    __tablename__ = "policy_chunks"
    id = Column(String, primary_key=True)
    source_document = Column(String, nullable=False)   # e.g., "MYAS Khelo India Operational Guidelines 2024"
    source_page = Column(String, nullable=False)       # e.g., "Page 28"
    source_clause = Column(String, nullable=False)     # e.g., "Clause 4.2"
    text_content = Column(Text, nullable=False)
    embedding_json = Column(Text, nullable=False)      # Dense vector or normalized token weights

class ActionProposal(Base):
    __tablename__ = "action_proposals"
    id = Column(String, primary_key=True)
    action_type = Column(String, nullable=False)       # VERIFY_ATHLETE, ALLOCATE_EQUIPMENT, APPLY_OPPORTUNITY
    target_entity = Column(String, nullable=False)
    target_id = Column(String, nullable=False)
    proposed_payload = Column(Text, nullable=False)
    reasoning = Column(Text, nullable=False)
    citations_json = Column(Text, nullable=False)
    status = Column(String, default="PENDING_APPROVAL") # PENDING_APPROVAL, APPROVED, REJECTED, EXECUTED
    approval_token = Column(String, unique=True, nullable=False)
    created_by_agent = Column(String, default="TrackNet-Assistant-v1")
    approved_by = Column(String, ForeignKey("users.id"), nullable=True)
    executed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
```

---

## 4. API Endpoints Contract

1. `POST /api/v1/agent/chat`
   - Accepts prompt and user context.
   - Evaluates intent, invokes appropriate read tools, searches policy chunks, generates grounded explanation with citations.
2. `POST /api/v1/agent/proposals`
   - Generates a dry-run action proposal without mutating DB state.
3. `POST /api/v1/agent/proposals/{id}/execute`
   - Requires valid `approval_token` and authorized user role. Executes the proposal into real database entities and marks `status: EXECUTED`.
4. `GET /api/v1/agent/proposals`
   - Lists active action proposals pending officer sanction.

---

## 5. Acceptance Test Matrix (`tests/test_phase4.py`)

- **Test 1: Agent Write Isolation**: Agent cannot mutate entities directly without calling `/agent/proposals/{id}/execute` with an approval token.
- **Test 2: RBAC Geo-Scoping Isolation**: Prompt from Pune DSO requesting Nagpur/Sonipat minor records returns zero minor identifiers or 404.
- **Test 3: 100% Policy Citation Rate**: Queries against official guidelines return exact `source_document`, `page`, and `clause`.
- **Test 4: Uncited Query Fallback**: Unknown policy queries strictly return `"No source found in approved guidelines"`.
- **Test 5: Audit Log Integrity**: Prompt hash, model identifier, and tool executions recorded in tamper-evident chain.
- **Test 6: Proposal Approval Token Invalidation**: Used or expired tokens cannot be re-executed (idempotency & replay protection).
