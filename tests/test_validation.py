"""Tests for upload validation and hashing."""

from __future__ import annotations

from backend.ingestion.hashing import sha256_bytes
from backend.ingestion.validator import sanitize_filename, validate_upload


def test_sanitize_filename_strips_paths_and_unsafe_chars():
    assert sanitize_filename("..\\..\\Policies/Q2 (Final)!.pdf") == "Q2_Final.pdf"


def test_reject_unsupported_extension(isolated_settings):
    result = validate_upload("notes.md", b"hello")
    assert not result.ok
    assert any(error.code == "unsupported_type" for error in result.errors)


def test_reject_empty_file(isolated_settings):
    result = validate_upload("policy.txt", b"")
    assert not result.ok
    assert any(error.code == "empty_file" for error in result.errors)


def test_reject_mismatched_pdf_signature(isolated_settings):
    result = validate_upload("fake.pdf", b"this is not a pdf")
    assert not result.ok
    assert any(error.code == "malformed" for error in result.errors)


def test_accept_text_file(isolated_settings):
    result = validate_upload("policy.txt", b"Attendance requirement is 75%.")
    assert result.ok
    assert result.extension == ".txt"


def test_sha256_is_stable():
    assert sha256_bytes(b"abc") == sha256_bytes(b"abc")
    assert sha256_bytes(b"abc") != sha256_bytes(b"abd")
