"""
Document chunking with recursive and semantic strategies.
"""
from typing import List
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from app.core.config import get_settings


class Chunker:
    """
    Two chunking strategies:

    1. recursive: LangChain RecursiveCharacterTextSplitter
       - Splits on ["\n\n", "\n", ". ", " ", ""] in order
       - Preserves paragraph boundaries

    2. semantic: Group sentences by embedding similarity
       - Use sentence-transformers to embed each sentence
       - Merge sentences until cosine similarity drops below threshold
       - Better for conceptually coherent chunks

    Both strategies must:
    - Preserve ALL original document metadata
    - Add chunk_index, chunk_total, char_start, char_end to metadata
    - Return List[Document]
    """

    def __init__(self):
        self.settings = get_settings()
        self.semantic_model = None
        if self.settings.chunking_strategy == "semantic":
            # Load the sentence transformer model for semantic chunking
            self.semantic_model = SentenceTransformer(self.settings.embedding_model)

    def chunk(self, documents: List[Document]) -> List[Document]:
        """Main chunking method that routes to the selected strategy."""
        if self.settings.chunking_strategy == "recursive":
            return self._recursive_chunk(documents)
        elif self.settings.chunking_strategy == "semantic":
            return self._semantic_chunk(documents)
        else:
            raise ValueError(f"Unknown chunking strategy: {self.settings.chunking_strategy}")

    def _recursive_chunk(self, documents: List[Document]) -> List[Document]:
        """Recursive chunking using LangChain's text splitter."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        chunked_docs = []
        for doc in documents:
            splits = text_splitter.split_text(doc.page_content)
            for i, split in enumerate(splits):
                # Calculate character start and end positions in the original text
                # This is approximate; for exact positions we would need to track during split.
                # For simplicity, we'll compute by finding the split in the original text.
                # Note: This approach may be inefficient for large documents but acceptable for now.
                start_index = doc.page_content.find(split)
                end_index = start_index + len(split)

                # Prepare metadata
                metadata = doc.metadata.copy()
                metadata.update({
                    "chunk_index": i,
                    "chunk_total": len(splits),
                    "char_start": start_index,
                    "char_end": end_index,
                })

                chunked_docs.append(Document(page_content=split, metadata=metadata))
        return chunked_docs

    def _semantic_chunk(self, documents: List[Document]) -> List[Document]:
        """Semantic chunking by grouping sentences with similar embeddings."""
        if self.semantic_model is None:
            raise ValueError("Semantic chunking model not initialized.")

        chunked_docs = []
        for doc in documents:
            # Split the document into sentences (simple split on '. ')
            sentences = [s.strip() for s in doc.page_content.split('. ') if s.strip()]
            if not sentences:
                continue

            # Embed each sentence
            embeddings = self.semantic_model.encode(sentences)

            # Group sentences by similarity
            groups = []
            current_group = [0]  # start with first sentence index
            for i in range(1, len(sentences)):
                # Compute similarity between current sentence and the first in the group
                sim = cosine_similarity([embeddings[i]], [embeddings[current_group[0]]])[0][0]
                if sim >= 0.5:  # threshold for grouping
                    current_group.append(i)
                else:
                    groups.append(current_group)
                    current_group = [i]
            groups.append(current_group)

            # Create chunks from groups
            for group_indices in groups:
                group_sentences = [sentences[i] for i in group_indices]
                chunk_text = '. '.join(group_sentences) + '.'

                # Find the start and end indices in the original text (approximate)
                start_index = doc.page_content.find(group_sentences[0])
                end_index = start_index + len(chunk_text)

                metadata = doc.metadata.copy()
                metadata.update({
                    "chunk_index": len(chunked_docs),  # temporary, will renumber
                    "chunk_total": len(groups),       # temporary
                    "char_start": start_index,
                    "char_end": end_index,
                })

                chunked_docs.append(Document(page_content=chunk_text, metadata=metadata))

            # Renumber chunk_index and chunk_total for all chunks from this document
            for i, chunk in enumerate(chunked_docs[-len(groups):]):
                chunk.metadata["chunk_index"] = i
                chunk.metadata["chunk_total"] = len(groups)
        return chunked_docs
