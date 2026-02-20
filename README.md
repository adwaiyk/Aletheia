# ALETHEIA: Zero-Data-Egress FinCrime Investigations Terminal

[cite_start]**Barclays Hack-O-Hire Solution** [cite: 11]
[cite_start]**Problem Statement:** SAR Narrative Generator with Audit Trail [cite: 12]
[cite_start]**Team:** Better Call SAR [cite: 12]

Aletheia is an advanced, end-to-end Agentic AI compliance workbench designed to eradicate false-positive alert waste and automate the generation of Suspicious Activity Reports (SARs) within a strictly air-gapped, Zero-Data-Egress architecture. 

---

## 1. The Problem Statement: The Compliance Crisis
[cite_start]Global financial institutions face massive bottlenecks in Anti-Money Laundering (AML) operations across four interconnected domains[cite: 18]:

* [cite_start]**Compliance & Risk Management:** Manual drafting results in long turnarounds and inconsistent risk descriptions[cite: 21, 22]. [cite_start]A poor audit trail leads to low defensibility, which impacts the bank through fines, regulatory scrutiny, and credibility loss[cite: 22, 23].
* [cite_start]**Operations & Document Processing:** Overloaded teams face heavy backlogs, and manual handling leads to errors[cite: 31]. [cite_start]The lack of standard templates requires repeated corrections, resulting in missed risks and incomplete reporting[cite: 31, 32].
* [cite_start]**Data & Analytics:** It is highly difficult to detect complex patterns and perform manual transaction linking[cite: 25, 26]. [cite_start]Limited trend insights result in missed risks, incomplete reporting, and inconsistent outputs[cite: 27, 28].
* [cite_start]**Technology & Compliance Systems:** The lack of AI assistance requires high effort, and limited traceability causes issues with regulator queries[cite: 34]. [cite_start]Fragmented workflows impact the institution through low transparency, human errors, and weaker compliance confidence[cite: 34, 35].

---

## 2. Proposed Solution & Innovations
Aletheia transforms AML compliance from a reactive cost center into a proactive, AI-driven powerhouse by addressing these challenges with the following innovations:

1. [cite_start]**End-to-End Agentic Automation:** An autonomous system that ingests, analyzes, generates, validates, and audits SAR narratives[cite: 39].
2. [cite_start]**Contextual Linking:** Early data ingestion that links transactions, entities, and watchlists for deeper contextual intelligence[cite: 38].
3. [cite_start]**Hybrid Detection Engine:** Combines deterministic rules, ML classifiers (Anomaly detection), and dynamic contextual risk scoring[cite: 52].
4. [cite_start]**Grounded Generation:** A Retrieval-Augmented Generation (RAG) pipeline utilizing SAR templates and source trace mapping to completely prevent AI hallucinations[cite: 54].
5. [cite_start]**Audit Transparency:** Full explainability with a time-locked audit trail capturing data sources, reasoning steps, model versions, and human edits[cite: 42].
6. [cite_start]**Human Oversight:** A human-in-the-loop review system enabling analyst edits, overrides, and continuous feedback learning[cite: 40].
7. [cite_start]**Zero-Trust Security:** Built securely by design with Role-Based Access Control (RBAC), Personally Identifiable Information (PII) masking, prompt protection, and strict data isolation across agents[cite: 41].

---

## 3. System & Agentic AI Architecture

[cite_start]Aletheia's architecture utilizes a stateful LangGraph orchestration that directs data through specialized AI agents[cite: 70, 72]. 

### Orchestration Flow & Methodologies
* [cite_start]**Phase 1: Risk Assessment & Knowledge Embedding:** The system converts regulatory documents to vector embeddings and stores them in a ChromaDB Vector Database[cite: 107, 118]. [cite_start]Concurrently, an ML Risk Scoring Model evaluates incoming alerts, utilizing SHAP to extract and explain feature importance[cite: 98, 101, 124].
* [cite_start]**Phase 2: Semantic Retrieval:** When an alert is triggered, LlamaIndex performs a semantic search against the ChromaDB vector database[cite: 99, 104, 109]. [cite_start]This retrieves the exact FinCEN guidelines and historical SAR templates that match the specific financial crime typology[cite: 102, 126].
* [cite_start]**Phase 3: State Orchestration & Narrative Generation:** The LangChain Orchestrator maintains a "State Object" (case file) that travels through the pipeline[cite: 106, 129, 130]. 
    * [cite_start]A **PII Scrubber** anonymizes data and updates the state[cite: 112, 131].
    * [cite_start]A **Narrative Planner Agent** serves as the architect, creating a structured plan[cite: 105, 139].
    * [cite_start]A **Text Generation Agent** utilizes RAG to draft the narrative grounded in legal rules[cite: 110, 115, 140].
    * [cite_start]A **Compliance Validator Agent** ensures the narrative answers the essential 5 W's and meets jurisdiction-specific standards (e.g., FinCEN, FIU-IND)[cite: 120, 143].
* [cite_start]**Phase 4: Auditability:** Every single time the state updates and flows across an edge, LangGraph automatically saves a Checkpoint of the entire state to a PostgreSQL database[cite: 103, 127]. [cite_start]This allows auditors to replay the exact flow of data, step-by-step, proving the AI's chain of thought[cite: 128].

---

## 4. Tech Stack

| Technology | Architectural Purpose |
| :--- | :--- |
| **LangGraph** | [cite_start]Orchestration/Agent: Enables stateful, directed execution graphs with controlled routing, loops, and audit-aware state memory[cite: 145]. |
| **LangChain** | [cite_start]Orchestration/Agent: Prevents hallucinated narratives by utilizing RAG with ChromaDB grounding to map templates and source traces[cite: 145]. |
| **Llama 3 / Mistral 7B** | [cite_start]LLM Layer: Local models running via Ollama ensuring template-based, regulation-backed generation with zero-data egress[cite: 145]. |
| **PostgreSQL** | [cite_start]Database: Stores the immutable fact and audit log, acting as structured state memory[cite: 145]. |
| **ChromaDB** | [cite_start]VectorDB: A lightweight, open-source database for regulatory memory and context retrieval[cite: 145]. |
| **FastAPI** | [cite_start]Backend API Layer: Enforces zero-trust boundaries via role-based privacy controls and PII tokenization before LLM calls[cite: 145]. |
| **Frontend UI (React/Streamlit)** | [cite_start]User Interface: Supports edit-approve workflows, explainability views, and human overrides tied to the audit log[cite: 145]. |
| **Python (Scikit-learn/SHAP)** | [cite_start]Feature Engineering: Manages explainable risk scoring, producing interpretable risk factors before narrative drafting[cite: 145]. |
| **LlamaIndex** | [cite_start]Retrieval: Provides contextual regulatory grounding per alert over ChromaDB[cite: 145]. |
| **Docker** | [cite_start]Deployment: Dockerized microservices and FastAPI async endpoints enabling horizontal scaling[cite: 145]. |

---

## 5. Business Impact
By deploying Aletheia, Tier-1 financial institutions realize immediate operational transformations:
1. [cite_start]**Eradicating the 95% False Positive Waste** [cite: 229]
2. [cite_start]**Massive Operational Cost Reduction** [cite: 231, 232]
3. [cite_start]**Eliminating Regulatory Backlogs** [cite: 233]

---

## 6. Future Scope
Aletheia's architecture is built to scale toward the ultimate goals of global compliance:

* [cite_start]**"Always-On" Perpetual KYC & OSINT Integration:** An autonomous system that scans global media, court records, and dark web sources in real time[cite: 236, 240]. [cite_start]Risk scores update instantly before major transactions clear, flagging threats as soon as a client's public profile shifts[cite: 241].
* [cite_start]**Zero-Knowledge Consortium Data Sharing:** Allows banks (e.g., Barclays and HSBC) to share fraud typologies between institutions through federated learning without exposing customer data[cite: 237, 242]. [cite_start]Cryptographic checks confirm matches across institutions while maintaining data privacy and residency compliance[cite: 243].
* [cite_start]**Predictive Threat Detection & Network Mapping:** AI-driven graph models to identify shell company networks and anticipate illicit fund flows[cite: 238, 239, 244]. [cite_start]Synthetic, privacy-safe data trains models to detect emerging money laundering risks before they surface[cite: 245].

---

## 7. Local Installation & Demo Guide

Because Aletheia relies on a **Zero-Data Egress** architecture, it must be run locally to interface with your offline LLM.

### Prerequisites
1. Install Python 3.10+
2. Install Ollama and pull the Llama 3 model:
   ```bash
   ollama run llama3