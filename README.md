```markdown
# 🧬 GeneRosetta

[![Live Demo](https://img.shields.io/badge/Live_Demo-generosetta.cloud-blue?style=for-the-badge&logo=google-chrome)](https://generosetta.cloud)
[![Build Status](https://img.shields.io/github/actions/workflow/status/EmediongFrancis/GeneRosetta/deploy.yml?style=for-the-badge)](https://github.com/EmediongFrancis/GeneRosetta/actions)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)

> **From Raw Sequence to Biological Story.**
> *A species-agnostic BioSaaS platform that transforms raw genomic data into interactive 3D protein structures and natural-language clinical reports.*

---

## 📖 The Problem
Bioinformatics is gatekept by complexity. Traditional tools are command-line based, output obscure codes (e.g., `p.Trp53Arg`), and require a PhD to interpret. Generative AI tools (LLMs) can explain data, but they often "hallucinate" scientific facts, making them dangerous for clinical use.

## 💡 The Solution
**GeneRosetta** acts as a deterministic "Universal Translator." It uses a hardcoded **Biophysical Engine**—not an LLM—to calculate precise molecular changes. It orchestrates a suite of global APIs to visualize and explain DNA sequences instantly.

---

## 📸 Screenshots

| **Frictionless Upload** | **Interactive 3D Structure** |
|:---:|:---:|
| *Drag-and-drop FASTA/VCF or paste raw DNA* | *Real-time rendering via ESMFold & 3Dmol.js* |
| ![Upload Screen](screenshots/upload.png) | ![Result Screen](screenshots/result.png) |

*(Note: If screenshots aren't loading, please view the `screenshots/` folder)*

---

## 🏗 System Architecture

GeneRosetta is architected as an **Asynchronous Distributed System** to handle heavy biological computations without blocking the user experience.

```mermaid
graph TD
    User[User / Browser] -->|HTTPS| Nginx[Global Nginx Proxy]
    Nginx -->|Proxy Pass| Gunicorn[Django App Service]
    
    subgraph "Docker Network"
        Gunicorn -->|Save Request| DB[(PostgreSQL)]
        Gunicorn -->|Push Task| Redis[Redis Broker]
        Redis -->|Pop Task| Worker[Celery Worker]
    end
    
    subgraph "The Bio-Engine (Worker)"
        Worker -->|Step 1: Identify| BLAST[NCBI BLAST API]
        Worker -->|Step 2: Route| Router{Bio-Router}
        
        Router -->|Human| ClinVar[NCBI ClinVar API]
        Router -->|Universal| UniProt[UniProt KB API]
        Router -->|Unknown| Physics[Biophysical Engine]
        
        Worker -->|Step 3: Fold| ESM[ESMFold API]
    end
    
    Worker -->|Update Status| DB
    User -->|Poll Status (HTMX)| Gunicorn
```

### Key Technical Differentiators

1.  **Intelligent "Bio-Router" (Strategy Pattern)**
    The system does not assume the input. It first "fingerprints" the organism.
    *   **IF Human:** Routes to the *Clinical Strategy* (Queries ClinVar for disease pathogenicity).
    *   **IF Dog/Bacteria/Virus:** Routes to the *Universal Strategy* (Queries UniProt for biological function).
    *   **IF Unknown:** Routes to the *Fallback Strategy* (Calculates pure physics: Mass/Charge/Hydropathy deltas).

2.  **Deterministic Narrative Engine**
    Instead of using ChatGPT, I built a logic engine based on the **Kyte-Doolittle Scale**. It mathematically calculates if a mutation destabilizes a protein (e.g., "Hydrophobic Core exposed to Water") and generates the text report programmatically. Zero hallucinations.

3.  **Asynchronous Pipeline**
    NCBI BLAST queries can take 30-60 seconds. The app uses **Celery & Redis** to offload this processing. The frontend uses **HTMX** to poll for status updates, ensuring the UI never freezes.

---

## 🚀 Core Features

*   **🧬 Species Agnostic:** Works on Humans, Bacteria, Viruses, and Animals.
*   **🔓 Guest Mode:** Immediate access without login.
*   **🔐 Google SSO:** Seamless authentication to save project history.
*   **⚛️ 3D Visualization:** In-browser rendering of PDB structures using WebGL.
*   **🛡️ Production Security:** Dockerized, SSL-secured (Let's Encrypt), and protected against CSRF/Host-Header attacks.

---

## 🛠️ Tech Stack

### Backend
*   **Framework:** Django 5.0 & Django REST Framework (DRF)
*   **Task Queue:** Celery 5.3 + Redis 7
*   **Database:** PostgreSQL 15
*   **Bioinformatics:** Biopython (SeqIO, BLAST, Entrez)

### Frontend
*   **Template Engine:** Django Templates
*   **Styling:** Tailwind CSS
*   **Interactivity:** HTMX (Polling) & Vanilla JS
*   **Visualization:** 3Dmol.js & Marked.js

### Infrastructure (DevOps)
*   **Containerization:** Docker & Docker Compose
*   **CI/CD:** GitHub Actions (Auto-build & Deploy to VPS)
*   **Server:** Linux VPS (Ubuntu) + Nginx Reverse Proxy

---

## 📦 Local Installation

To run GeneRosetta locally for development:

### Prerequisites
*   Docker & Docker Compose
*   *OR* Python 3.10+ and Redis installed locally

### Option A: Docker (Recommended)
```bash
# 1. Clone the repo
git clone https://github.com/EmediongFrancis/GeneRosetta.git
cd GeneRosetta

# 2. Create .env file
cp .env.example .env
# (Update .env with your credentials)

# 3. Build and Run
docker compose up --build
```
Visit `http://127.0.0.1:8000`

### Option B: Manual Setup
```bash
# 1. Environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Database
# Ensure PostgreSQL is running and credentials are in .env
python manage.py migrate

# 3. Redis
# Ensure Redis is running on port 6379

# 4. Run Services (Needs two terminals)
# Terminal 1:
python manage.py runserver
# Terminal 2:
celery -A config worker --loglevel=info
```

---

## 🔗 APIs Used
*   **NCBI BLAST:** Species Identification.
*   **NCBI E-utilities (ClinVar):** Human clinical variant data.
*   **UniProt KB:** Universal protein function data.
*   **ESMFold (Meta AI):** Protein structure prediction.

---

## 👨‍💻 Author

**Emediong "Bendito" Francis**
*   *Links:* [GitHub](https://github.com/EmediongFrancis) | [LinkedIn](https://linkedin.com/in/emediongfrancis) | [Email](mailto:emediongfrancis@gmail.com)
*   *Project Type:* Advanced Backend Engineering

---
*Built with ❤️ and Python.*
```
