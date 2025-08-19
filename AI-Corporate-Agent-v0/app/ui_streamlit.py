from __future__ import annotations
import io
import json
from pathlib import Path
from typing import List, Tuple
import zipfile
import os
import sys

# Ensure project root is on sys.path so `import app.*` works when running this file directly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st  # type: ignore

from app.config import load_config
from app.text_extractor import extract_text_with_metadata
from app.analyzer import analyze_documents
from app.docx_utils import annotate_docx
from app.ingest import ensure_index
from app.official_check import is_official_adgm_format


st.set_page_config(page_title="ADGM Corporate Agent", layout="wide")

cfg = load_config()

st.title("ADGM Corporate Agent - Document Reviewer")

with st.expander("Build/Refresh Knowledge Base (RAG)", expanded=False):
    st.write("Reference directory:", cfg.reference_dir)
    if st.button("Build/Refresh Index"):
        try:
            ensure_index()
            st.success("Index is ready.")
        except Exception as e:
            st.error(f"Failed to build index: {e}")

uploaded = st.file_uploader(
    "Upload one or more .docx files", type=["docx"], accept_multiple_files=True
)

if uploaded:
    docs: List[Tuple[str, str]] = []
    non_official_any = False
    temp_dir = Path("./.tmp_uploads")
    temp_dir.mkdir(exist_ok=True)
    for f in uploaded:
        temp_path = temp_dir / f.name
        with open(temp_path, "wb") as out:
            out.write(f.read())
        text, _ = extract_text_with_metadata(str(temp_path))
        is_off, reason = is_official_adgm_format(text)
        if not is_off:
            non_official_any = True
        docs.append((str(temp_path), text))

    if non_official_any:
        st.warning(
            "Some uploaded documents do not appear to be in the official ADGM format. "
            "Please use only official ADGM templates as per ADGM rules and regulations, and "
            "download the correct forms from the official ADGM website."
        )

    if st.button("Run ADGM Review"):
        with st.spinner("Analyzing documents with RAG..."):
            report = analyze_documents(docs)
        st.subheader("Structured Report")
        st.json(report)

        # Save reviewed docs and provide zip download
        output_dir = Path(cfg.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        reviewed_paths: List[Path] = []
        for item in report["files"]:
            in_name = item["file"]
            for (path, _text) in docs:
                if Path(path).name == in_name:
                    reviewed_path = output_dir / f"REVIEWED_{in_name}"
                    annotate_docx(path, item.get("issues", []), str(reviewed_path))
                    reviewed_paths.append(reviewed_path)
                    break

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for p in reviewed_paths:
                zipf.write(p, arcname=p.name)
            # Also include the structured JSON report
            json_bytes = json.dumps(report, indent=2).encode('utf-8')
            zipf.writestr('report.json', json_bytes)
        st.download_button(
            label="Download Reviewed Docs + Report (ZIP)",
            data=zip_buf.getvalue(),
            file_name="adgm_review_outputs.zip",
            mime="application/zip",
        )
else:
    st.info("Upload .docx files to start the review.") 