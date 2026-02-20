# ALETHEIA: Zero-Data-Egress FinCrime Investigations Terminal (A Demo)

**Barclays Hack-O-Hire Solution**
**Problem Statement:** SAR Narrative Generator with Audit Trail
**Team:** Better Call SAR

Aletheia is an advanced, end-to-end Agentic AI compliance workbench designed to eradicate false-positive alert waste and automate the generation of Suspicious Activity Reports (SARs) within a strictly air-gapped, zero-data-egress architecture. 

---

## 1. The Problem Statement: The Compliance Crisis
Global financial institutions face severe operational and regulatory bottlenecks in Anti-Money Laundering (AML) operations:

* **Compliance and Risk Management:** Manual drafting of SARs results in prolonged turnaround times and inconsistent risk descriptions. The absence of a robust audit trail leads to low regulatory defensibility, exposing banks to severe fines and credibility loss.
* **Operations and Document Processing:** Overloaded investigation teams face massive backlogs. Manual data handling introduces human error, while the lack of standardized reporting templates necessitates constant corrections.
* **Data and Analytics:** Detecting complex financial crime patterns (such as layering and smurfing) across massive datasets is incredibly difficult manually, leading to missed risks and incomplete regulatory reporting.
* **Technology and Systems:** Financial institutions are unable to utilize powerful cloud-based AI due to strict Data Residency and Privacy laws (PII cannot be sent to external APIs). This leaves legacy systems fragmented, opaque, and highly inefficient.

---

## 2. Proposed Solution and Innovations
Aletheia transforms AML compliance from a reactive cost center into a proactive, AI-driven powerhouse by addressing these challenges with the following core innovations:

* **End-to-End Agentic Automation:** An autonomous system that ingests financial ledgers, analyzes anomalies, generates narratives, and audits the final output.
* **Contextual Alert Triage Engine (The False-Positive Killer):** A semantic AI engine that evaluates transaction memos to dismiss legitimate life events (e.g., house downpayments), drastically reducing wasted investigative hours.
* **Hybrid Detection Engine:** Combines deterministic mathematical rules (to catch exact structuring thresholds) with dynamic contextual risk scoring.
* **Enterprise Multi-Jurisdictional Routing:** Dynamically aligns the AI's legal reasoning with regional frameworks, switching seamlessly between USA (FinCEN), India (FIU-IND), and UK (NCA) regulations.
* **Cryptographic Audit Ledger:** Provides absolute explainability with a time-locked audit trail. The system hashes the exact state of the evidence, human overrides, and final narrative using SHA-256, establishing an immutable chain of custody.
* **Zero-Trust Security:** Built securely by design. By running the Large Language Model entirely locally, the system guarantees that sensitive PII never leaves the bank's internal network.

---

## 3. System and Agentic AI Architecture

Aletheia utilizes a stateful orchestration pipeline that directs data through specialized execution layers.

### Orchestration Flow
1. **Risk Assessment and Knowledge Embedding:** The system converts regulatory documents (like FinCEN guidelines) into vector embeddings. Concurrently, a deterministic rule engine filters thousands of raw transactions to isolate high-risk anomalies.
2. **Semantic Retrieval:** When a suspect account is flagged, the Retrieval-Augmented Generation (RAG) pipeline performs a semantic search to extract the exact historical SAR templates that match the specific financial crime typology.
3. **State Orchestration and Narrative Generation:** A stateful object (the case file) travels through the pipeline:
    * A Data Scrubber isolates necessary transaction context.
    * A Narrative Planner Agent outlines the required SAR structure.
    * A Text Generation Agent utilizes the local LLM to draft a highly formal, citation-backed narrative.
4. **Auditability and Export:** Once reviewed by a human analyst, the system generates a cryptographic hash of the entire session. It then automatically compiles the data into machine-readable XML, JSON, LaTeX, and PDF formats for downstream integration.

---

## 4. Technology Stack

* **Orchestration:** LangGraph and LangChain (Stateful execution graphs and RAG pipelines)
* **LLM Engine:** Ollama running Llama 3 / Mistral 7B (Local execution for zero-data egress)
* **Vector Database:** ChromaDB (Lightweight, open-source regulatory memory)
* **Frontend Interface:** Streamlit (React-based UI for edit-approve workflows and network visualizations)
* **Data Processing:** Pandas, NumPy, and PyVis (Feature engineering, deterministic rule triggering, and fund flow network mapping)
* **Security and Auditing:** Python Hashlib (SHA-256) and local JSON/PostgreSQL (Immutable ledger)

---

## 5. Business Impact
By deploying Aletheia, Tier-1 financial institutions realize immediate operational transformations:
* **Eradicating the 95% False Positive Waste:** Slashes the noise of non-suspicious alerts automatically, saving millions in operational overhead.
* **Massive Operational Cost Reduction:** Frees up thousands of manual investigation hours, allowing human analysts to focus on genuine, high-priority threats.
* **Eliminating Regulatory Backlogs:** Accelerates SAR filing times from weeks to seconds, maintaining total compliance and avoiding regulatory penalties.

---

## 6. Future Scope
Aletheia's architecture is built to scale toward the ultimate goals of global enterprise compliance:

* **Perpetual KYC and OSINT Integration:** Deploying an autonomous background agent to constantly scrape global adverse media, court registries, and dark web forums. This shifts compliance from periodic reviews to real-time, dynamic risk re-scoring.
* **Zero-Knowledge Consortium Data Sharing:** Utilizing Federated Learning to share known money laundering typologies between global institutions (e.g., Barclays and HSBC). This achieves collaborative threat intelligence without ever exposing underlying customer PII.
* **Predictive Threat Hunting:** Upgrading the pipeline with predictive Graph Machine Learning to map complex shell company networks and anticipate the next node in an illicit fund flow before the money is moved.

---

## 7. Local Installation and Demo Setup

Because Aletheia relies on a strict zero-data egress architecture, it must be run locally to interface with your offline LLM.

### Prerequisites
1. Install Python 3.10 or higher.
2. Install Ollama (ollama.ai) and pull the Llama 3 model by running the following command in your terminal:
   ```bash
   ollama run llama3

### Installation Steps
1. Clone the repository:
    ```bash
    git clone [https://github.com/adwaiyk/Aletheia.git](https://github.com/adwaiyk/Aletheia.git)
    cd Aletheia

2. Install dependencies:
    ```bash
    pip install -r requirements.txt

3. Run Data Generator:
    ```bash
    python data_gen.py

4. Run App
    ```bash
    streamlit run app.py