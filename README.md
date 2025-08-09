## ADGM Corporate Agent (RAG)

A Streamlit-based agentic RAG app that reviews ADGM corporate formation documents, flags red flags, inserts inline comments into .docx, and outputs a structured JSON report.

### Features
- Accept multiple `.docx` uploads
- Parse and classify document types
- Verify required documents checklist for Company Incorporation
- Detect red flags (rules + LLM with RAG over provided references)
- Insert inline highlighted comments in the reviewed `.docx`
- Generate a JSON report and a downloadable ZIP (reviewed docs + report)

### Setup
1. Python 3.10+ recommended
2. Optional: set env variables for LLMs
   - `OPENAI_API_KEY` and optionally `OPENAI_API_BASE`, `OPENAI_MODEL`
   - Or use Ollama locally with `OLLAMA_BASE_URL` and `OLLAMA_MODEL`
3. Install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r app/requirements.txt
   ```

### Prepare Knowledge Base
Place your ADGM reference files under `data/reference/` (already populated with your provided files). The index will be created on first run automatically, or you can click "Build/Refresh Index" in the UI.

### Run
```bash
streamlit run app/ui_streamlit.py
```

### Outputs
- Reviewed `.docx` saved to `outputs/REVIEWED_*.docx`
- `report.json` included in the ZIP download

### Notes
- Word comments are simulated by highlighted inline notes for reliability across Python libraries.
- RAG uses Sentence-Transformers + FAISS locally. OpenAI/Ollama can be used for reasoning.
- Extend `app/checklists.py` and `app/classifier.py` to add more processes and document types. 