"""Ingestion pipeline, metadata, and duplicate detection tests."""

from __future__ import annotations

from backend.ingestion.models import IndexingStatus
from backend.ingestion.pipeline import IngestionPipeline
from backend.ingestion.registry import DocumentRegistry


def test_ingest_txt_stores_metadata_and_extracted_text(isolated_settings):
    pipeline = IngestionPipeline(DocumentRegistry(isolated_settings.registry_path))
    result = pipeline.ingest_bytes(
        "employee_policy_2026.txt",
        b"ATTENDANCE\nEmployees must maintain 75% attendance.\n",
        version="2026.1",
        year=2026,
        department="HR",
        category="Policy",
        document_name="Employee Policy 2026",
    )
    assert result.success
    assert result.document is not None
    assert result.document.document_name == "Employee Policy 2026"
    assert result.document.version == "2026.1"
    assert result.document.year == 2026
    assert result.document.department == "HR"
    assert result.document.indexing_status == IndexingStatus.PARSED
    assert result.document.chunk_count == 0
    assert result.document.file_hash
    assert result.parsed is not None
    assert "75%" in result.parsed.full_text

    loaded = pipeline.load_extracted(result.document.document_id)
    assert loaded is not None
    assert loaded.metadata.document_id == result.document.document_id


def test_duplicate_hash_is_rejected(isolated_settings):
    pipeline = IngestionPipeline(DocumentRegistry(isolated_settings.registry_path))
    payload = b"Same policy bytes for duplicate detection."
    first = pipeline.ingest_bytes("a.txt", payload, document_name="Policy A")
    second = pipeline.ingest_bytes("b.txt", payload, document_name="Policy B")
    assert first.success
    assert not second.success
    assert second.duplicate
    assert DocumentRegistry(isolated_settings.registry_path).stats()["total_documents"] == 1


def test_reparse_and_delete(isolated_settings):
    pipeline = IngestionPipeline(DocumentRegistry(isolated_settings.registry_path))
    created = pipeline.ingest_bytes("ops.txt", b"Submit requests within 7 days.")
    assert created.document is not None
    doc_id = created.document.document_id

    reparsed = pipeline.reparse(doc_id)
    assert reparsed.success
    assert reparsed.document is not None
    assert "7 days" in (reparsed.parsed.full_text if reparsed.parsed else "")

    deleted = pipeline.delete(doc_id)
    assert deleted.success
    assert pipeline.registry.get(doc_id) is None


def test_parse_failure_does_not_crash(isolated_settings):
    pipeline = IngestionPipeline(DocumentRegistry(isolated_settings.registry_path))
    # Pass signature check (%PDF) but provide a payload that cannot be parsed cleanly.
    result = pipeline.ingest_bytes("bad.pdf", b"%PDF-1.4\n%corrupted")
    assert result.document is not None
    assert result.document.indexing_status in {
        IndexingStatus.PARSED,
        IndexingStatus.PARSE_FAILED,
    }
