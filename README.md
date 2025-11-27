# 🧬 GeneRosetta

> **From Raw Sequence to Biological Story.**
> *A species-agnostic BioSaaS platform that creates automated, natural-language clinical reports and 3D protein visualizations from raw genomic data.*

---

## 📖 Overview

Bioinformatics is traditionally a field of complex command-line tools, obscure file formats, and output that only experts can decipher (e.g., `p.Trp53Arg` or `c.123A>T`).

**GeneRosetta** bridges the gap between raw genetic data and human understanding. It acts as a **"Universal Translator"** for biology. Users can upload raw DNA sequences (FASTA/VCF) or simple text strings, and the platform automatically:
1.  **Identifies** the organism (Human, Bacteria, or Virus).
2.  **Visualizes** the resulting protein structure in 3D.
3.  **Translates** technical mutations into a plain-English report describing clinical impact or biological function.

## 🚀 Core Features

*   **Frictionless "Guest Mode":** Immediate analysis without requiring user accounts.
*   **Universal Scope:** Optimized for **Human, Bacterial, and Viral** genomes, with a modular architecture designed to scale to other species.
*   **Intelligent "Bio-Router":** Automated detection of the input organism to route analysis to the correct dataset (e.g., ClinVar for humans, UniProt for microbes).
*   **3D Structure Rendering:** Integration with AlphaFold/ESMFold to generate PDB structures on the fly.
*   **Natural Language Engine:** Converts cryptic variant codes into readable sentences explaining stability, charge changes, and disease associations.

## 🏗 Architecture

GeneRosetta is built as an **"Intelligent Assembly Line"** divided into three distinct tiers:

### Tier 1: The Foundation (Data & Ingest)
*   **Input Handling:** Validates FASTA/VCF files and raw strings.
*   **Sanitization:** Enforces file size limits (max ~50KB) to focus on gene-level analysis rather than whole genomes.
*   **Storage:** PostgreSQL database for user history and analysis results.

### Tier 2: The Pipeline (Async Logic)
*   **Task Queue:** Uses **Celery & Redis** to handle time-consuming bio-computations without blocking the web server.
*   **The Scanner:** Uses **Biopython & BLAST** to fingerprint the organism.
*   **The Router:** A modular switchboard that directs data to specific API pipelines based on the detected organism.

### Tier 3: The Synthesis (Presentation)
*   **API Layer:** RESTful endpoints (Django REST Framework) serving JSON results.
*   **Visualization:** Frontend integration for 3D molecule rendering and report display.

## 🛠️ Tech Stack

*   **Language:** Python 3.10+
*   **Framework:** Django & Django REST Framework (DRF)
*   **Async Processing:** Celery + Redis
*   **Database:** PostgreSQL
*   **Bioinformatics:** Biopython, NCBI BLAST
*   **External APIs:** NCBI E-utilities (ClinVar), UniProt, EBI AlphaFold/ESMFold
*   **Authentication:** Google OAuth2 (Social Auth)

## 🗺️ Project Roadmap

This project is being developed over a 5-week intensive sprint.

- [ ] **Week 1: Foundation** - Project setup, DB modeling, and File Ingestion logic.
- [ ] **Week 2: The Logic Layer** - BLAST integration and the "Bio-Router" organism detection.
- [ ] **Week 3: Async Pipeline** - Implementing Celery/Redis for background processing.
- [ ] **Week 4: Synthesis** - Natural Language Generation and 3D Visualization integration.
- [ ] **Week 5: Deployment & Polish** - Edge case handling and cloud deployment.

## 📦 Setup & Installation

*(Instructions will be populated as the project infrastructure is built)*

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/gene-rosetta.git
    cd gene-rosetta
    ```

2.  **Create a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

---

*GeneRosetta is a Project exploring the intersection of Advanced Backend Engineering and Bioinformatics.*