# NexusRAG

Evidence-first enterprise knowledge intelligence. NexusRAG does not simply generate answers from documents. It is designed to connect information across documents, reason over relationships and versions, verify supporting evidence, and show why an answer can be trusted.

**Current status: Phase 1 complete (document upload + parsing).** Later phases are scaffolded but not implemented. This repository will not fake citations, graph data, or evaluation scores.

## Problem

Organizational knowledge is spread across PDFs, DOCX files, policies, manuals, spreadsheets, and multiple document versions. Keyword search and naive vector RAG often return answers without trustworthy evidence. NexusRAG treats retrieval, evidence, and verification as first-class product features.

## Phase 1 features

- Upload PDF, DOCX, TXT, CSV, and XLSX
- File validation (type, size, empty files, basic signatures, safe names)
- Text and table extraction with page/section metadata where the format supports it
- SHA-256 duplicate detection
- Persistent document registry and extracted-text storage
- Document library: view metadata, preview extraction, re-parse, delete
- Dashboard metrics derived only from real ingested files
- Streamlit enterprise shell with navigation for later phases (honest placeholders)

Not in Phase 1: embeddings, vector search, BM25, reranking, RAG answers, knowledge graph, agents, evaluation scores.

## Architecture

```
main.py                 Streamlit entry
app/                    UI, pages, theme
backend/ingestion/      validation, parsers, registry, pipeline
backend/*              reserved packages for later phases
config/                 environment-backed settings and logging
data/documents/         stored originals
data/processed/         registry.json and extracted JSON
data/samples/           synthetic demo files
tests/                  Phase 1 unit and pipeline tests
```

## Tech stack (Phase 1)

- Python 3.10+
- Streamlit
- PyMuPDF, python-docx, pandas, openpyxl
- pydantic / pydantic-settings, python-dotenv
- pytest

## Installation

```bash
cd "C:\Users\Nvija\OneDrive\Desktop\Nexus RAG"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts/generate_samples.py
```

On macOS/Linux, activate with `source .venv/bin/activate` and copy the env file with `cp .env.example .env`.

## Environment variables

See `.env.example`. Phase 1 does not require `GEMINI_API_KEY`. Do not put secrets in source files.

| Variable | Purpose |
| --- | --- |
| `DATA_DIR` | Root for documents and processed output |
| `MAX_UPLOAD_MB` | Upload size limit |
| `GEMINI_API_KEY` | Reserved for Phase 4 |
| `EMBEDDING_MODEL` | Reserved for Phase 2 |

## How to run

```bash
streamlit run main.py
```

Then open the URL printed in the terminal (typically http://localhost:8501).

1. Go to **Documents**
2. Upload a file from `data/samples`
3. Confirm metadata, extracted preview, and status `Parsed`
4. Re-upload the same file to confirm duplicate detection
5. Check **Dashboard** counts

## How document ingestion works (Phase 1)

Upload → validate → SHA-256 hash → reject duplicates → store original → parse by type → write `extracted.json` → update registry.

- PDF: per-page text, heading-like sections from font size, tables when PyMuPDF can detect them
- DOCX: paragraphs, Heading styles, tables
- TXT: full text and simple heading detection
- CSV/XLSX: sheet/table text representation

Chunking, embeddings, and indexing are intentionally not performed yet (`chunk_count` remains 0).

Scanned image PDFs are flagged as possibly needing OCR. OCR is not enabled in Phase 1.

## Later phases (not implemented)

Hybrid retrieval, RAG with citations, version comparison, knowledge graph, agentic routing, and evaluation will be added only after the previous phase is working.

## Demo questions

These questions are the target demonstration set. They cannot be answered by the product until Phase 4+. Sample documents already contain the facts those questions will need:

1. What is the current policy for this process?
2. What changed between the 2025 and 2026 policies?
3. Which document supports this requirement?
4. How does the regulation affect this process?
5. Compare the requirements across these three documents.
6. Are there any conflicting requirements?

Known synthetic conflicts for later phases: 2025 vs 2026 leave windows (7 days vs 5 days); Operations Manual still states 7 days; attendance 70% vs 75%.

## Tests

```bash
pytest
```

## Screenshots

Add screenshots here after the first demo recording (Dashboard, Documents library, extracted preview).

## Future improvements

- Phase 2: smart chunking, embeddings, ChromaDB
- Phase 3: BM25 hybrid search and reranking
- Phase 4: grounded generation with evidence cards
- Phase 5: version diffs
- Phase 6: NetworkX knowledge graph
- Phase 7: query router and tools
- Phase 8: RAG evaluation dashboard
- Optional OCR for scanned PDFs
- Neo4j migration path for the graph
