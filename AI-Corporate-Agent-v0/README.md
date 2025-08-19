## ADGM Corporate Agent – Document Intelligence (RAG)

An AI-powered legal assistant to review ADGM incorporation/compliance documents. It accepts `.docx` uploads, identifies document types, checks completeness against ADGM checklists, detects red flags with RAG-backed citations, inserts inline notes in the `.docx`, and outputs a structured report.

### Features
- Accept multiple `.docx` uploads via a simple web UI (Streamlit)
- Auto-detect process (focus: Company Incorporation) and compare against required checklist
- Classify uploaded docs (AoA, MoA/MoU, Board/Shareholder Resolutions, etc.)
- Detect red flags (jurisdiction issues, ambiguous language, missing signatures, template non-compliance)
- Enforce “official ADGM format” with warning and high-severity issue if not met
- Insert inline highlighted notes in reviewed `.docx` files
- Generate a structured JSON report and a downloadable ZIP (reviewed docs + report)
- Retrieval-Augmented Generation over provided ADGM reference materials
- Pluggable model support: OpenAI or local Ollama

### Project Structure
```
AI-Corporate-Agent-v0/
├─ app/
│  ├─ ui_streamlit.py        # Web UI (Streamlit)
│  ├─ analyzer.py            # Core analysis: classify, RAG, issues, report
│  ├─ classifier.py          # Heuristic document-type classifier
│  ├─ checklists.py          # Required docs per process (Company Incorporation)
│  ├─ text_extractor.py      # Extract text from .docx/.pdf
│  ├─ ingest.py              # Lightweight vector store (OpenAI/Ollama embeddings)
│  ├─ retrieval.py           # Similarity search + RAG prompt builder
│  ├─ docx_utils.py          # Inline notes/highlights in .docx
│  ├─ official_check.py      # Heuristic “official ADGM format” checker
│  ├─ llm.py                 # LLM abstraction (OpenAI → fallback Ollama)
│  └─ config.py              # Env/config management
├─ data/
│  ├─ reference/             # ADGM reference docs (RAG source)
│  └─ vector.*               # Persisted local embeddings (created at runtime)
├─ outputs/                  # Reviewed .docx and report.zip
├─ .tmp_uploads/             # Temp area for uploaded files (runtime)
├─ .venv/                    # Python venv (local)
└─ README.md                 # This guide
```

### Quick Start

#### 1) Prerequisites
- Windows with PowerShell
- Python 3.10+ installed
- Optional (choose one for models):
  - OpenAI API key for best embeddings/reasoning
  - Ollama running locally (offline), with models pulled (e.g., `llama3.1`, `nomic-embed-text`)

#### 2) Download the project
- Download ZIP and extract to a folder, e.g. `D:\AI-Corporate-Agent-v0`
  - or clone from your Git repository if applicable

#### 3) Setup environment
```powershell
cd D:\AI-Corporate-Agent-v0
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r app\requirements.txt
```

#### 4) Choose model (one-time)
- OpenAI (cloud):
  ```powershell
  setx OPENAI_API_KEY "sk-..."
  setx OPENAI_MODEL "gpt-4o-mini"
  setx EMBEDDING_MODEL "text-embedding-3-small"
  ```
  Open a new PowerShell window after `setx`.

- Ollama (local, no cloud):
  - Install from the Ollama site, then:
    ```powershell
    ollama pull llama3.1
    ollama pull nomic-embed-text
    setx OLLAMA_MODEL "llama3.1"
    setx EMBEDDING_MODEL "ollama:nomic-embed-text"
    setx OPENAI_API_KEY ""
    ```
  Open a new PowerShell window after `setx`.

#### 5) Run the app
```powershell
.\.venv\Scripts\streamlit run app\ui_streamlit.py
```
Open the browser: `http://localhost:8501`

#### 6) Build knowledge base (first time)
- In the app, open “Build/Refresh Knowledge Base (RAG)” → click “Build/Refresh Index”
- Ensure your ADGM references reside under `data/reference/` (the project includes starter files)

#### 7) Review documents
- Upload one or more `.docx` files (your incorporation pack)
- Click “Run ADGM Review”
- Download “Reviewed Docs + Report (ZIP)”; reviewed files are also saved to `outputs/`

### Supported Document Types
- Uploads: `.docx` (Word) only
- Recognized formation categories (examples):
  - Articles of Association (AoA)
  - Memorandum of Association (MoA/MoU)
  - Board Resolution
  - Shareholder Resolution
  - Incorporation Application Form
  - UBO Declaration Form
  - Register of Members and Directors
  - Change of Registered Address Notice
- References for RAG: `.pdf`, `.docx`, `.md`, `.txt` placed under `data/reference/`

### Using the Web Interface
- Build/Refresh Index: prepares the RAG knowledge base from `data/reference/`
- Upload area: choose one or more `.docx` files
- Warning banner appears if any upload doesn’t look like an official ADGM template
- Run ADGM Review: performs classification, checklist verification, RAG issues, and saves reviewed outputs

### Output Format
- Reviewed `.docx`: inline notes/highlights summarizing issues and suggestions
- Structured JSON report (included in ZIP and visible in UI), e.g.:
```json
{
  "process": "Company Incorporation",
  "documents_uploaded": 4,
  "required_documents": 5,
  "missing_documents": ["Register of Members and Directors"],
  "files": [
    {
      "file": "Articles_of_Association.docx",
      "type": "Articles of Association",
      "confidence": 0.9,
      "issues": [
        {
          "section_hint": "Jurisdiction/Dispute Resolution",
          "issue": "Jurisdiction clause does not specify ADGM",
          "severity": "High",
          "suggestion": "Update jurisdiction to ADGM Courts.",
          "citation": "ADGM Companies Regulations 2020, Art. …"
        }
      ]
    }
  ]
}
```

### ADGM References
The system uses official ADGM documents and regulations from:
- [ADGM Official Website](https://www.adgm.com/)
- [ADGM Registration Authority](https://www.adgm.com/operating-in-adgm/registration-authority)
- [ADGM Legal Framework: Legislation](https://www.adgm.com/legal-framework/legislation)

If your uploaded files are not in official ADGM format, the app warns and recommends downloading the correct template from the official ADGM website.

---

### Notes
- The app currently focuses its checklist on “Company Incorporation”. You can extend `app/checklists.py` and `app/classifier.py` for more processes (licensing, HR, commercial, compliance).
- Inline notes are implemented for reliability across `.docx` tooling; native Word comment objects can be added if needed. 