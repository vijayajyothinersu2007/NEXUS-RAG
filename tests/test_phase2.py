"""Phase 2 indexing and import verification tests."""


def test_indexing_package_imports_cleanly():
    import backend.indexing

    assert backend.indexing.TextChunker
    assert backend.indexing.VectorStoreManager

from backend.indexing.chunker import TextChunker
from backend.indexing.vectorstore import VectorStoreManager


def test_chunking_and_vector_store(tmp_path):
    chunker = TextChunker(chunk_size=100, chunk_overlap=10)
    vstore = VectorStoreManager(storage_dir=tmp_path / "vectorstore")

    payload = {
        "doc_id": "test_1",
        "filename": "sample.pdf",
        "pages": [{"page_num": 1, "text": "NexusRAG provides evidence-first knowledge intelligence."}],
    }

    chunks = chunker.create_chunks(payload)
    assert len(chunks) > 0

    vstore.add_chunks(chunks)
    results = vstore.search_similar("evidence-first")
    assert len(results["documents"][0]) > 0