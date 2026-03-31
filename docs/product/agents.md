# The 6 ARCHON Architect Agents

ARCHON deploys 6 specialist AI architects in parallel, each with deep domain expertise, live web research, and access to your codebase. All 6 are orchestrated by a **team-architecture** supervisor that coordinates their work and merges their findings.

---

## How Each Agent Works

Every agent follows the same 4-phase loop:

```
Phase 1 — INGEST (RAG)
  Read your codebase via semantic + keyword search
  Identify relevant files, configs, and patterns

Phase 2 — RESEARCH (Perplexity-style)
  Search the live web for domain-specific knowledge
  Extract and rank sources by relevance + credibility
  Build an evidence base with citations

Phase 3 — REASON (Chain of Thought)
  Map findings to your codebase reality
  Identify gaps, risks, and opportunities
  Generate alternatives with trade-off analysis

Phase 4 — PRODUCE
  Architecture findings with severity scores
  Domain-specific ADRs and IaC
  Diagrams and risk register entries
  Cited recommendations
```

---

## Software Architect

**Domain:** Application architecture, patterns, NFRs, tech debt, ADRs

**What they review:**
- Application structure: layering, module boundaries, dependency direction
- Architectural patterns: hexagonal, clean, DDD, CQRS, event-driven
- Non-functional requirements: scalability, maintainability, testability
- Technical debt: identification, prioritisation, migration paths
- Code structure standards and anti-patterns

**Key questions answered:**
- "Is our application structure set up to scale with a growing team?"
- "Are our bounded contexts well-defined?"
- "What is our technical debt load and what should we fix first?"
- "Which architectural patterns should we adopt for our next service?"

**Outputs:** ADRs for key structural decisions, refactoring plan, NFR specification

---

## Cloud Architect

**Domain:** AWS / GCP / Azure infrastructure, IaC, cost optimisation, DR

**What they review:**
- Cloud service selection and configuration
- Networking: VPCs, subnets, security groups, peering
- Compute strategy: containers, serverless, VMs
- Storage and database architecture
- Cost model: rightsizing, reserved capacity, spot usage
- Disaster recovery: RPO/RTO, multi-region, backup strategy
- Infrastructure as Code: Terraform/Pulumi quality and coverage

**Key questions answered:**
- "How much are we overspending on cloud? Where?"
- "Are we prepared for a regional outage?"
- "Is our Terraform production-ready?"
- "What's our scaling strategy as we grow 10x?"

**Outputs:** Cost model at 3 tiers (startup/growth/scale), IaC skeleton, DR runbook, ADRs for infrastructure decisions

---

## Security Architect

**Domain:** Zero-trust, IAM, encryption, compliance (SOC2, HIPAA, GDPR, PCI-DSS)

**What they review:**
- Authentication and authorisation design
- IAM: roles, permissions, service accounts, least privilege
- Encryption: at rest, in transit, key management
- Zero-trust posture: network segmentation, service-to-service auth
- Compliance gaps: SOC 2 / HIPAA / GDPR / PCI-DSS readiness
- Secrets management: how credentials are stored and rotated
- CVE scanning: known vulnerabilities in dependencies and infrastructure

**Key questions answered:**
- "What are our critical security gaps before our SOC 2 audit?"
- "Are we handling PII in a GDPR-compliant way?"
- "Is our authentication design zero-trust ready?"
- "What CVEs apply to our current stack?"

**Outputs:** Threat model, compliance gap analysis, zero-trust design, encryption architecture

---

## Data Architect

**Domain:** Data strategy, governance, data models, pipelines, storage

**What they review:**
- Data model: schema design, entity relationships, normalisation
- Data governance: ownership, quality, lineage, classification
- Storage strategy: databases, data lakes, warehouses, caching
- Data pipelines: ETL/ELT patterns, streaming vs batch
- Data contracts between services
- PII handling and data retention policies

**Key questions answered:**
- "Is our database schema going to hold up at 100x data volume?"
- "Do we have a data governance strategy?"
- "Should we be using a data warehouse?"
- "How do we handle GDPR right-to-erasure requests?"

**Outputs:** Data model review, data governance framework, storage strategy recommendation, data contract templates

---

## Integration Architect

**Domain:** Service communication, event-driven design, API gateway, service mesh

**What they review:**
- Service communication patterns: REST, gRPC, messaging, events
- API design: contracts, versioning, backwards compatibility
- Event-driven architecture: event schema, broker topology, consumer design
- API gateway: routing, rate limiting, auth, aggregation
- Service mesh: mTLS, traffic management, observability
- Saga patterns and distributed transaction handling
- Integration testing strategy

**Key questions answered:**
- "Are our microservices tightly coupled in ways that will cause problems?"
- "Should we be using event-driven architecture?"
- "Is our API design backwards-compatible and well-versioned?"
- "How do we handle distributed transactions across services?"

**Outputs:** Integration architecture diagram, event design document, API contract review, service decomposition plan

---

## AI Architect

**Domain:** ML/AI systems, RAG pipelines, model serving, agentic architectures

**What they review:**
- AI/ML system design: training, serving, monitoring
- LLM integration: prompt design, RAG architecture, fine-tuning strategy
- Vector database selection and RAG pipeline quality
- Model serving infrastructure: latency, throughput, cost
- MLOps: training pipelines, experiment tracking, model versioning
- AI safety: guardrails, input/output validation, human oversight
- Agentic system design: orchestration, tool use, memory patterns

**Key questions answered:**
- "Is our RAG pipeline designed correctly?"
- "Are we spending too much on LLM API calls?"
- "How do we prevent prompt injection in our AI features?"
- "What's the right model serving strategy for our latency requirements?"

**Outputs:** AI system architecture, RAG pipeline review, MLOps recommendations, cost optimisation plan

---

## Team Architecture (Supervisor)

The **team-architecture** agent orchestrates all 6 specialists:

1. Fans out to all 6 agents simultaneously
2. Monitors progress and handles checkpoint coordination
3. Cross-references findings across domains (e.g., security + cloud agree on the same risk)
4. Deduplicates overlapping findings
5. Produces the executive summary
6. Assembles the final Architecture Review Package

The supervisor does not produce domain-specific findings — it synthesises the work of the 6 specialists into a coherent whole.
