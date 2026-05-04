import pytest
from app.services.ingestion.chunker import Chunker
from langchain_core.documents import Document

def make_doc(text: str) -> Document:
    return Document(page_content=text, metadata={"source": "test"})

class TestChunker:
    def setup_method(self):
        self.chunker = Chunker()

    def test_basic_chunking_returns_chunks(self):
        doc = make_doc("word " * 500)
        chunks = self.chunker.chunk([doc])
        assert len(chunks) > 1

    def test_chunk_size_respected(self):
        doc = make_doc("word " * 500)
        chunks = self.chunker.chunk([doc])
        for chunk in chunks:
            # chunk_size is 800, so chunks should be <= 800 + small buffer for separators
            assert len(chunk.page_content) <= 900

    def test_metadata_preserved(self):
        doc = make_doc("hello world " * 200)
        chunks = self.chunker.chunk([doc])
        for chunk in chunks:
            assert chunk.metadata.get("source") == "test"

    def test_empty_input_returns_empty(self):
        assert self.chunker.chunk([]) == []

    def test_short_doc_returns_single_chunk(self):
        doc = make_doc("Short document.")
        chunks = self.chunker.chunk([doc])
        assert len(chunks) == 1
